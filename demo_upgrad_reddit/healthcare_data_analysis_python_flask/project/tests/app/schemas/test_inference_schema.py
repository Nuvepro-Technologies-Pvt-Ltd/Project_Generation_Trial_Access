import pytest
from marshmallow import ValidationError
from src.app.schemas.inference_schema import InferenceRequestSchema, InferenceEntitySchema, InferenceResponseSchema

class TestInferenceRequestSchema:
    def test_valid_minimal_request_schema(self):
        # Arrange
        valid_data = {
            'patient_id': 'PAT123'
        }
        schema = InferenceRequestSchema()
        # Act
        result = schema.load(valid_data)
        # Assert
        assert result['patient_id'] == 'PAT123', 'Patient ID should be correctly deserialized.'
        assert 'symptoms' not in result, 'Symptoms should be optional.'
        assert 'clinical_text' not in result, 'Clinical text should be optional.'

    def test_valid_full_request_schema(self):
        valid_data = {
            'patient_id': 'PAT456',
            'symptoms': ['cough', 'fever'],
            'clinical_text': 'The patient exhibits shortness of breath.'
        }
        schema = InferenceRequestSchema()
        result = schema.load(valid_data)
        assert result['patient_id'] == 'PAT456'
        assert result['symptoms'] == ['cough', 'fever']
        assert result['clinical_text'] == 'The patient exhibits shortness of breath.'

    def test_missing_required_field_raises(self):
        invalid_data = {
            'symptoms': ['nausea']
        }
        schema = InferenceRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        assert 'patient_id' in exc_info.value.messages
        
    def test_empty_symptoms_field(self):
        data = {'patient_id': 'PAT999', 'symptoms': []}
        schema = InferenceRequestSchema()
        result = schema.load(data)
        assert isinstance(result['symptoms'], list) and result['symptoms'] == []

    def test_patient_id_wrong_type_raises(self):
        data = {
            'patient_id': 1000  # should be a string
        }
        schema = InferenceRequestSchema()
        with pytest.raises(ValidationError):
            schema.load(data)

class TestInferenceEntitySchema:
    def test_valid_entity(self):
        entity = {
            'entity': 'diabetes',
            'label': 'disease',
            'value': 'yes'
        }
        schema = InferenceEntitySchema()
        result = schema.load(entity)
        assert result['entity'] == 'diabetes'
        assert result['label'] == 'disease'
        assert result['value'] == 'yes'

    def test_missing_label_raises(self):
        entity = {
            'entity': 'hypertension',
            'value': 'no'
        }
        schema = InferenceEntitySchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(entity)
        assert 'label' in exc_info.value.messages

class TestInferenceResponseSchema:
    def test_valid_minimal_response(self):
        data = {
            'diagnosis': 'asthma',
            'confidence': 0.87
        }
        schema = InferenceResponseSchema()
        result = schema.load(data)
        assert result['diagnosis'] == 'asthma'
        assert abs(result['confidence'] - 0.87) < 1e-6
        assert 'entities' not in result

    def test_valid_full_response(self):
        data = {
            'diagnosis': 'COVID-19',
            'confidence': 0.97,
            'entities': [
                {'entity': 'fever', 'label': 'symptom', 'value': 'present'},
                {'entity': 'crp', 'label': 'lab', 'value': 'elevated'}
            ]
        }
        schema = InferenceResponseSchema()
        result = schema.load(data)
        assert result['diagnosis'] == 'COVID-19'
        assert abs(result['confidence'] - 0.97) < 1e-6
        assert isinstance(result['entities'], list) and len(result['entities']) == 2
        assert result['entities'][0]['entity'] == 'fever'
        assert result['entities'][1]['entity'] == 'crp'

    def test_missing_required_field_raises(self):
        data = {
            'confidence': 0.45
        }
        schema = InferenceResponseSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'diagnosis' in exc_info.value.messages

    def test_confidence_wrong_type_raises(self):
        data = {
            'diagnosis': 'pneumonia',
            'confidence': 'high'
        }
        schema = InferenceResponseSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'confidence' in exc_info.value.messages

    def test_entities_invalid_structure_raises(self):
        # entities should be a list of dicts with the correct structure
        data = {
            'diagnosis': 'infection',
            'confidence': 0.88,
            'entities': [{
                'entity': 'wbc',
                'label': 'lab'
                # missing 'value'
            }]
        }
        schema = InferenceResponseSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'entities' in exc_info.value.messages or 'value' in str(exc_info.value.messages)

    def test_extra_fields_are_ignored(self):
        data = {
            'diagnosis': 'allergy',
            'confidence': 0.91,
            'unexpected_field': 123
        }
        schema = InferenceResponseSchema()
        result = schema.load(data)
        assert result['diagnosis'] == 'allergy'
        assert abs(result['confidence'] - 0.91) < 1e-6
        assert 'unexpected_field' not in result, 'Unknown fields should be excluded by default.'