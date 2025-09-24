import os
import json
import tempfile
import shutil
import pandas as pd
import numpy as np
import pytest
from pathlib import Path
from src.data.healthcare_data_pipeline import HealthcareDataPipeline, FHIRMapper, Deidentifier, DataQualityLogger, pipeline_sequence


@pytest.fixture
def sample_ehr_df():
    # Fake EHR structured data
    data = {
        'patient_id': ['123'],
        'gender': ['male'],
        'birth_date': ['1990-01-01'],
        'encounter_id': ['abc'],
        'diagnosis_code': ['I10'],
        'diagnosis_date': ['2021-03-01'],
        'patient_name': ['John Doe'],
        'ssn': ['123-45-6789'],
        'address': ['123 Main St'],
        'dob': ['1990-01-01'],
        'phone': ['555-123-4567'],
        'email': ['john.doe@example.com']
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_notes_df():
    # Fake clinical notes
    data = {
        'patient_id': ['123'],
        'encounter_id': ['abc'],
        'note_text': ['John Doe was inspected on 01/01/2010. Call 555-123-4567.'],
        'note_datetime': ['2021-03-01']
    }
    return pd.DataFrame(data)

@pytest.fixture
def temp_output_dir():
    # Temporary output directory for test artifacts
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir  # Provide path and cleanup after

@pytest.fixture(autouse=True)
def reset_numpy_seed():
    # Reset numpy RNG for reproducibility in each test
    np.random.seed(17)

def test_FHIRMapper_map_row_unit():
    # Arrange
    row = {
        'patient_id': 'p1',
        'gender': 'female',
        'birth_date': '1975-02-16',
        'encounter_id': 'e12',
        'diagnosis_code': 'X01',
        'diagnosis_date': '2022-01-01',
        'note_text': 'Sample',
        'note_datetime': '2021-12-15'
    }
    # Act
    mapped = FHIRMapper.map_row(row)
    # Assert
    resource_types = set([item['resourceType'] for item in mapped])
    assert resource_types == {'Patient', 'Encounter', 'Condition', 'DocumentReference'}, 'All FHIR resource types expected'

def test_FHIRMapper_encode_categorical_basic():
    # Arrange
    values = ['a', 'b', 'a', 'c', 'b']
    # Act
    encoded, mapping = FHIRMapper.encode_categorical(values)
    # Assert
    assert len(set(encoded)) == 3, 'Should encode 3 unique categories'
    assert set(mapping.keys()) == set(['a', 'b', 'c']), 'Mapping covers all categories'

def test_FHIRMapper_encode_categorical_unknown():
    # Arrange
    mapping = {'x': 0, 'y': 1}
    values = ['x', 'y', 'z']
    # Act
    encoded, _ = FHIRMapper.encode_categorical(values, mapping=mapping)
    # Assert
    assert encoded == [0, 1, 2], 'Unknown value assigned next available int'

def test_Deidentifier_scrub_removes_pii():
    # Arrange
    deid = Deidentifier()
    text = 'Name: John Doe. SSN: 123-45-6789, Email: foo@bar.com, DOB: 01/01/2001, Phone: (555)123-4567'
    # Act
    scrubbed = deid.scrub(text)
    # Assert
    assert '<REDACTED>' in scrubbed and 'John Doe' not in scrubbed and 'foo@bar.com' not in scrubbed

def test_Deidentifier_deid_row_applies_scrub():
    # Arrange
    deid = Deidentifier()
    row = {
        'note_text': 'Patient Jane Smith, ssn 111-22-3333. Contact jane@x.com.',
        'unrelated': 'intact'
    }
    # Act
    out = deid.deid_row(row, unstructured_fields=['note_text'])
    # Assert
    assert out['note_text'].count('<REDACTED>') >= 2
    assert out['unrelated'] == 'intact'

def test_Deidentifier_structured_deid_removes_fields(sample_ehr_df):
    # Arrange
    deid = Deidentifier()
    # Act
    deid_df = deid.structured_deid(sample_ehr_df.copy(), ['ssn', 'email'])
    # Assert
    assert deid_df['ssn'].isnull().all()
    assert deid_df['email'].isnull().all()

def test_DataQualityLogger_logs(tmp_path):
    # Arrange
    log_path = tmp_path / 'test.log'
    logger = DataQualityLogger(str(log_path))
    # Act
    logger.log('Test message')
    logger.log_stat('stat_field', 42)
    # Assert
    logger.logger.handlers[0].flush()
    with open(log_path) as f:
        log_contents = f.read()
    assert 'Test message' in log_contents
    assert 'STAT::stat_field::42' in log_contents

def test_merge_data_merges_on_ids(sample_ehr_df, sample_notes_df, temp_output_dir):
    # Arrange
    pipeline = HealthcareDataPipeline(
        ehr_path='',
        notes_path='',
        output_dir=temp_output_dir
    )
    pipeline.quality_logger = DataQualityLogger(os.path.join(temp_output_dir, 'test.log'))  # avoid writing to real path
    # Act
    merged = pipeline.merge_data(sample_ehr_df, sample_notes_df)
    # Assert
    assert 'note_text' in merged.columns
    assert merged.shape[0] == 1
    assert merged.iloc[0]['note_text'] == sample_notes_df.iloc[0]['note_text']

def test_normalize_and_encode_encodes_gender_dx(sample_ehr_df, sample_notes_df, temp_output_dir):
    # Arrange
    pipeline = HealthcareDataPipeline('', '', temp_output_dir)
    df = pd.merge(sample_ehr_df, sample_notes_df, on=['patient_id', 'encounter_id'], how='left')
    # Act
    result = pipeline.normalize_and_encode(df)
    # Assert
    assert all([isinstance(x, int) for x in result['gender']]), 'Gender should be numeric'
    assert all([isinstance(x, int) for x in result['diagnosis_code']]), 'Diagnosis code should be numeric'
    assert 'birth_date_unix' in result.columns and pd.notna(result['birth_date_unix']).all()

@pytest.mark.parametrize(
    'note,expected',
    [
        ('John Doe. SSN: 123-45-6789.', True),
        ('No identifiers here.', False),
        ('Call (123)456-7890 for help.', True),
        ('', False)
    ]
)
def test_deidentifier_scrub_catches_various_pii(note, expected):
    deid = Deidentifier()
    result = deid.scrub(note)
    contains_redacted = '<REDACTED>' in result
    assert contains_redacted == expected

def test_HealthcareDataPipeline_run_end_to_end(tmp_path):
    # Arrange
    ehr_csv = tmp_path / 'ehr.csv'
    notes_csv = tmp_path / 'notes.csv'
    # Write minimal input datasets
    ehr = pd.DataFrame({
        'patient_id': ['1'],
        'gender': ['male'],
        'birth_date': ['1981-02-12'],
        'encounter_id': ['enc_1'],
        'diagnosis_code': ['A10'],
        'diagnosis_date': ['2021-10-01'],
        'patient_name': ['Jane Doe'],
        'ssn': ['111-22-3333'],
        'address': ['1 Test St'],
        'dob': ['1981-02-12'],
        'phone': ['555-777-8888'],
        'email': ['janedoe@test.com']
    })
    notes = pd.DataFrame({
        'patient_id': ['1'],
        'encounter_id': ['enc_1'],
        'note_text': ['Contact Jane Doe at 555-777-8888.'],
        'note_datetime': ['2021-10-01']
    })
    ehr.to_csv(ehr_csv, index=False)
    notes.to_csv(notes_csv, index=False)
    outdir = tmp_path / 'output'
    # Act
    pipeline = HealthcareDataPipeline(str(ehr_csv), str(notes_csv), str(outdir))
    pipeline.run()
    # Assert
    fhir_json = outdir / 'fhir_dataset.json'
    ml_csv = outdir / 'ml_ready_dataset.csv'
    assert fhir_json.exists(), 'FHIR resource json output should exist'
    assert ml_csv.exists(), 'ML ready csv should exist'
    # Validate FHIR JSON structure
    with open(fhir_json) as f:
        data = json.load(f)
    assert any(r['resourceType'] == 'Patient' for r in data)
    # Validate de-id
    df = pd.read_csv(ml_csv)
    assert 'patient_name' in df.columns and df['patient_name'].isnull().all(), 'PHI should be removed'
    assert 'gender' in df.columns and df['gender'].dtype in [int, np.int64], 'Gender should be encoded'

def test_pipeline_sequence_completeness():
    steps = pipeline_sequence()
    steps_keys = [step['step'] for step in steps]
    assert steps_keys == [
        'Ingestion',
        'De-identification',
        'Validation & Quality Check',
        'FHIR Mapping',
        'Normalization & Encoding',
        'Audit Trail Output'
    ], 'All pipeline steps should be present in order'

# Performance Smoke Test (optional, only runs if pytest -k perf)
@pytest.mark.skipif(os.environ.get('RUN_PERF', '0') != '1', reason='perf test not requested')
def test_pipeline_performance(tmp_path):
    # Arrange: Generate large synthetic EHR dataset
    n = 10000
    ehr = pd.DataFrame({
        'patient_id': [str(i) for i in range(n)],
        'gender': np.random.choice(['male', 'female'], size=n),
        'birth_date': pd.date_range('1960-01-01', periods=n).astype(str),
        'encounter_id': ['EN' + str(i) for i in range(n)],
        'diagnosis_code': np.random.choice(['A', 'B', 'C'], size=n),
        'diagnosis_date': pd.date_range('2020-01-01', periods=n).astype(str),
        'patient_name': ['Name %d' % i for i in range(n)],
        'ssn': ['000-00-%04d' % i for i in range(n)],
        'address': ['%d Main St' % i for i in range(n)],
        'dob': pd.date_range('1960-01-01', periods=n).astype(str),
        'phone': ['555-000-%04d' % i for i in range(n)],
        'email': ['test%d@email.com' % i for i in range(n)]
    })
    notes = pd.DataFrame({
        'patient_id': [str(i) for i in range(n)],
        'encounter_id': ['EN' + str(i) for i in range(n)],
        'note_text': ['Note %d with SSN 000-00-%04d' % (i, i) for i in range(n)],
        'note_datetime': pd.date_range('2020-01-01', periods=n).astype(str)
    })
    ehr_csv = tmp_path / 'ehr_perf.csv'
    notes_csv = tmp_path / 'notes_perf.csv'
    outdir = tmp_path / 'output_perf'
    ehr.to_csv(ehr_csv, index=False)
    notes.to_csv(notes_csv, index=False)
    pipeline = HealthcareDataPipeline(str(ehr_csv), str(notes_csv), str(outdir))
    # Act
    import time
    start = time.time()
    pipeline.run()
    elapsed = time.time() - start
    # Assert
    assert elapsed < 30, f"Pipeline should complete in under 30 seconds for {n} records (got {elapsed}s)"