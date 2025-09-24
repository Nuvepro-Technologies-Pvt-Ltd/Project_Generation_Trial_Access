import pytest
from src.app.services.inference_service import run_inference

# Test suite for run_inference function in inference_service.py

class TestRunInference:
    def test_run_inference_with_clinical_text_entities_extracted(self):
        # Arrange
        input_data = {
            "patient_id": "1234",
            "symptoms": ["fever", "cough"],
            "clinical_text": "Patient reports fever and cough for 3 days."
        }

        # Act
        result = run_inference(input_data)

        # Assert
        assert result["diagnosis"] == "Flu", "Diagnosis should always be 'Flu' for given logic."
        assert result["confidence"] == 0.95, "Confidence should always be 0.95."
        assert isinstance(result["entities"], list), "Entities should be a list."
        # Entities expected to be extracted from non-empty clinical_text
        assert {"entity": "Cough", "label": "symptom", "value": "present"} in result["entities"], "Missing 'Cough' entity."
        assert {"entity": "Fever", "label": "symptom", "value": "present"} in result["entities"], "Missing 'Fever' entity."

    def test_run_inference_with_empty_clinical_text_no_entities(self):
        # Arrange
        input_data = {
            "patient_id": "4321",
            "symptoms": ["fatigue"],
            "clinical_text": ""
        }

        # Act
        result = run_inference(input_data)

        # Assert
        assert result["diagnosis"] == "Flu", "Diagnosis should always be 'Flu' for given logic."
        assert result["confidence"] == 0.95, "Confidence should always be 0.95."
        assert result["entities"] == [], "Entities should be empty if clinical_text is empty."

    def test_run_inference_with_missing_symptoms(self):
        # Arrange
        input_data = {
            "patient_id": "5678",
            "clinical_text": "Fever and cough noted."
            # symptoms key is omitted
        }

        # Act
        result = run_inference(input_data)

        # Assert
        assert result["diagnosis"] == "Flu"
        assert result["confidence"] == 0.95
        assert any(entity["entity"] == "Fever" for entity in result["entities"]), "Should extract 'Fever' entity."
        assert any(entity["entity"] == "Cough" for entity in result["entities"]), "Should extract 'Cough' entity."

    def test_run_inference_with_missing_clinical_text_returns_no_entities(self):
        # Arrange
        input_data = {
            "patient_id": "9876",
            "symptoms": ["headache"]
            # clinical_text is missing
        }

        # Act
        result = run_inference(input_data)

        # Assert
        assert result["entities"] == [], "Entities should be empty when clinical_text is missing."

    @pytest.mark.parametrize(
        "input_data,expected_entities",
        [
            ({"patient_id": "1", "clinical_text": "", "symptoms": []}, []),
            ({"patient_id": "2", "clinical_text": None, "symptoms": ["fatigue"]}, []),
            ({"patient_id": "3", "clinical_text": "Has cough.", "symptoms": []}, [{"entity": "Cough", "label": "symptom", "value": "present"}, {"entity": "Fever", "label": "symptom", "value": "present"}]),
        ]
    )
    def test_run_inference_parametrized(self, input_data, expected_entities):
        # Arrange & Act
        result = run_inference(input_data)

        # Assert
        assert result["diagnosis"] == "Flu"
        assert result["confidence"] == 0.95
        if input_data.get("clinical_text"):
            # Entities should match the hardcoded ones if clinical_text is not empty/None
            assert all(e in result["entities"] for e in expected_entities)
        else:
            assert result["entities"] == []

    def test_run_inference_handles_missing_patient_id(self):
        # Arrange
        input_data = {
            "clinical_text": "Fever described.",
            "symptoms": ["fever"]
            # patient_id key is missing
        }

        # Act
        result = run_inference(input_data)

        # Assert
        assert result["diagnosis"] == "Flu"
        assert result["confidence"] == 0.95
        assert isinstance(result["entities"], list)

    def test_run_inference_error_on_non_dict_input(self):
        # Arrange
        input_data = None

        # Act & Assert
        with pytest.raises(AttributeError):
            run_inference(input_data)

    def test_run_inference_with_additional_unexpected_keys(self):
        # Arrange
        input_data = {
            "patient_id": "2154",
            "clinical_text": "Standard exam.",
            "symptoms": ["cough"],
            "extra_field": "unexpected",
            "another": 123
        }

        # Act
        result = run_inference(input_data)

        # Assert
        # Additional keys shouldn't affect logic
        assert result["diagnosis"] == "Flu"
        assert result["confidence"] == 0.95
        assert {"entity": "Cough", "label": "symptom", "value": "present"} in result["entities"]