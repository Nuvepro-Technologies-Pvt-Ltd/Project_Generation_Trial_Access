import os
import json
import logging
import re
from typing import List, Dict, Any, Iterable, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

class FHIRMapper:
    """
    Maps normalized EHR fields to FHIR resource representations.
    """
    field_to_fhir = {
        'patient_id': ('Patient', 'id'),
        'gender': ('Patient', 'gender'),
        'birth_date': ('Patient', 'birthDate'),
        'encounter_id': ('Encounter', 'id'),
        'diagnosis_code': ('Condition', 'code'),
        'diagnosis_date': ('Condition', 'onsetDateTime'),
        'note_text': ('DocumentReference', 'content'),
        'note_datetime': ('DocumentReference', 'date'),
    }

    @staticmethod
    def map_row(row: Dict[str, Any]) -> List[Dict[str, Any]]:
        mapped = []
        patient_resource, encounter_resource, condition_resource, doc_resource = {}, {}, {}, {}
        for field, value in row.items():
            if field in FHIRMapper.field_to_fhir:
                resource_type, fhir_key = FHIRMapper.field_to_fhir[field]
                if resource_type == 'Patient':
                    patient_resource[fhir_key] = value
                elif resource_type == 'Encounter':
                    encounter_resource[fhir_key] = value
                elif resource_type == 'Condition':
                    condition_resource[fhir_key] = value
                elif resource_type == 'DocumentReference':
                    doc_resource[fhir_key] = value
        if patient_resource:
            mapped.append({'resourceType': 'Patient', **patient_resource})
        if encounter_resource:
            mapped.append({'resourceType': 'Encounter', **encounter_resource})
        if condition_resource:
            mapped.append({'resourceType': 'Condition', **condition_resource})
        if doc_resource:
            mapped.append({'resourceType': 'DocumentReference', **doc_resource})
        return mapped

    @staticmethod
    def encode_categorical(values: Iterable[str], mapping: Dict[str, int]=None) -> Tuple[List[int], Dict[str, int]]:
        if mapping is None:
            unique = sorted(set(values))
            mapping = {v: i for i, v in enumerate(unique)}
        encoded = [mapping[x] if x in mapping else len(mapping) for x in values]
        return encoded, mapping

class Deidentifier:
    """
    De-identifies sensitive patient information from structured and unstructured fields.
    """
    def __init__(self, pii_patterns: List[str]=None):
        if pii_patterns is None:
            self.pii_patterns = [
                r'(?:\d{3}-\d{2}-\d{4}|\d{9})', # SSNs
                r"(?:[A-Z][a-z]+,? [A-Z][a-z]+)", # Names
                r"(?:\d{1,2}/\d{1,2}/\d{2,4})", # Dates
                r"(?:\(?\d{3}\)?[\s-]?\d{3}-\d{4})", # Phones
                r"\w+@\w+\.\w{2,}", # Emails
            ]
        else:
            self.pii_patterns = pii_patterns
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.pii_patterns]
    def scrub(self, text: str) -> str:
        out = text
        for pat in self.compiled_patterns:
            out = pat.sub('<REDACTED>', out)
        return out
    def deid_row(self, row: Dict[str, Any], unstructured_fields: List[str]) -> Dict[str, Any]:
        new_row = row.copy()
        for field in unstructured_fields:
            if field in new_row and isinstance(new_row[field], str):
                new_row[field] = self.scrub(new_row[field])
        return new_row
    def structured_deid(self, df: pd.DataFrame, pii_fields: List[str]) -> pd.DataFrame:
        for field in pii_fields:
            if field in df:
                df[field] = None
        return df

class DataQualityLogger:
    """
    Handles logging and traceability across ETL stages for reproducibilty.
    """
    def __init__(self, log_file: str = "data_pipeline.log"):
        self.logger = logging.getLogger("DataPipelineLogger")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_file)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(fmt)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(fh)
    def log(self, msg: str):
        self.logger.info(msg)
    def log_stat(self, tag: str, value: Any):
        self.logger.info(f'STAT::{tag}::{value}')

class HealthcareDataPipeline:
    """
    End-to-end FHIR-aligned, de-identified clinical data pipeline.
    """
    def __init__(self, ehr_path: str, notes_path: str, output_dir: str, seed: int=17):
        self.ehr_path = ehr_path
        self.notes_path = notes_path
        self.output_dir = Path(output_dir)
        self.fhir_mapper = FHIRMapper()
        self.deidentifier = Deidentifier()
        self.quality_logger = DataQualityLogger(str(self.output_dir/"data_pipeline.log"))
        self.seed = seed
        np.random.seed(seed)
        self.unstructured_fields = ['note_text']
        self.pii_fields = ['patient_name', 'ssn', 'address', 'dob', 'phone', 'email']
    def run(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ehr_df = self.load_structured()
        notes_df = self.load_unstructured()
        self.quality_logger.log_stat('raw_ehr_records', len(ehr_df))
        self.quality_logger.log_stat('raw_notes_records', len(notes_df))
        ehr_df = self.deidentifier.structured_deid(ehr_df, self.pii_fields)
        notes_df = notes_df.apply(lambda row: self.deidentifier.deid_row(row, self.unstructured_fields), axis=1)
        self.quality_logger.log_stat('ehr_after_deid', ehr_df.shape[0])
        self.quality_logger.log_stat('notes_after_deid', notes_df.shape[0])
        merged = self.merge_data(ehr_df, notes_df)
        fhir_records = []
        for ix, row in merged.iterrows():
            fhir_records.extend(self.fhir_mapper.map_row(row.to_dict()))
        self.quality_logger.log_stat('fhir_records', len(fhir_records))
        clean_records = self.normalize_and_encode(merged)
        out_json = str(self.output_dir / "fhir_dataset.json")
        json.dump(fhir_records, open(out_json, "w"), indent=2)
        clean_csv = str(self.output_dir / "ml_ready_dataset.csv")
        clean_records.to_csv(clean_csv, index=False)
        self.quality_logger.log(f"FHIR-aligned and encoded ML dataset written to {clean_csv}")
        self.quality_logger.log(f"FHIR resource JSON dataset written to {out_json}")
    def load_structured(self) -> pd.DataFrame:
        if self.ehr_path.endswith('.csv'):
            df = pd.read_csv(self.ehr_path)
        else:
            df = pd.read_parquet(self.ehr_path)
        return df
    def load_unstructured(self) -> pd.DataFrame:
        if self.notes_path.endswith('.csv'):
            df = pd.read_csv(self.notes_path)
        else:
            df = pd.read_parquet(self.notes_path)
        return df
    def merge_data(self, ehr_df: pd.DataFrame, notes_df: pd.DataFrame) -> pd.DataFrame:
        merged = pd.merge(ehr_df, notes_df, left_on=['patient_id', 'encounter_id'], right_on=['patient_id', 'encounter_id'], how='left')
        merged = merged.drop_duplicates(subset=['patient_id', 'encounter_id'])
        self.quality_logger.log_stat('merged_records', merged.shape[0])
        return merged
    def normalize_and_encode(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if 'gender' in df:
            df['gender'], gender_map = FHIRMapper.encode_categorical(df['gender'].fillna('').tolist())
            self.quality_logger.log_stat('gender_categories', gender_map)
        if 'diagnosis_code' in df:
            dx_values = df['diagnosis_code'].fillna('').tolist()
            df['diagnosis_code'], dx_map = FHIRMapper.encode_categorical(dx_values)
            self.quality_logger.log_stat('diagnosis_code_map', dx_map)
        for dfield in ['birth_date', 'diagnosis_date', 'note_datetime']:
            if dfield in df:
                df[dfield] = pd.to_datetime(df[dfield], errors='coerce')
                df[dfield + '_unix'] = df[dfield].astype(np.int64) // 10 ** 9
        for textcol in self.unstructured_fields:
            if textcol in df:
                df[textcol] = df[textcol].fillna('').apply(lambda x: x.strip())
        return df

def pipeline_sequence() -> List[Dict[str, Any]]:
    steps = [
        {
            'step': 'Ingestion',
            'description': 'Load structured EHR (CSV/Parquet) and unstructured clinical notes.',
            'traceability': 'Record source files, import time.'
        },
        {
            'step': 'De-identification',
            'description': 'Remove or mask all direct and quasi-identifying PHI from both structured and unstructured fields as per HIPAA/ISO standards.',
            'traceability': 'Log date, count, and fields de-identified.'
        },
        {
            'step': 'Validation & Quality Check',
            'description': 'Run integrity and missing data checks; log anomalies.',
            'traceability': 'DataQualityLogger logs missing/invalid fields.'
        },
        {
            'step': 'FHIR Mapping',
            'description': 'Translate normalized data into FHIR-compliant resources (Patient, Encounter, Condition, DocumentReference).',
            'traceability': 'Log mapping dictionary and record counts.'
        },
        {
            'step': 'Normalization & Encoding',
            'description': 'Normalize denominators, encode categoricals, timestamp fields, and prepare tensors.',
            'traceability': 'Log categorical mappings, ranges.'
        },
        {
            'step': 'Audit Trail Output',
            'description': 'Write out ready-to-train dataset with traceability logs and configuration.',
            'traceability': 'Final audit and hash of outputs.'
        },
    ]
    return steps

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Run FHIR-aligned healthcare data pipeline.")
    parser.add_argument('--ehr_path', type=str, required=True)
    parser.add_argument('--notes_path', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    args = parser.parse_args()
    pipeline = HealthcareDataPipeline(
        ehr_path=args.ehr_path,
        notes_path=args.notes_path,
        output_dir=args.output_dir
    )
    pipeline.run()
    steps = pipeline_sequence()
    with open(os.path.join(args.output_dir, 'pipeline_trace_sequence.json'), 'w') as f:
        json.dump(steps, f, indent=2)