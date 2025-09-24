import pytest
from src.app.services import synthetic_data_service

import uuid
import re
import csv
import io
import pytest
from src.app.services import synthetic_data_service

# Fixture for base tabular input
def valid_tabular_input(columns=None, format_="csv", volume=3):
    data = {
        "data_type": "tabular",
        "format": format_,
        "volume": volume,
        "options": {}
    }
    if columns:
        data["options"]["columns"] = columns
    return data

# Fixture for base clinical text input
def valid_clinical_text_input(format_="plain_text", volume=2):
    return {
        "data_type": "clinical_text",
        "format": format_,
        "volume": volume
    }

def test_generate_synthetic_data_tabular_default_columns_csv():
    # Arrange
    data = valid_tabular_input()

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "completed"
    assert result["message"] == ""
    assert re.fullmatch(r"[0-9a-f\-]{36}", result["request_id"])
    output = io.StringIO(result["generated_data"])
    reader = csv.DictReader(output)
    rows = list(reader)
    expected_columns = ["patient_id", "age", "diagnosis"]
    assert reader.fieldnames == expected_columns
    assert len(rows) == 3
    for idx, row in enumerate(rows):
        for col in expected_columns:
            assert row[col] == f"synthetic_{col}_{idx}"


def test_generate_synthetic_data_tabular_custom_columns_csv():
    # Arrange
    columns = ["foo", "bar"]
    data = valid_tabular_input(columns=columns, volume=2)

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "completed"
    output = io.StringIO(result["generated_data"])
    reader = csv.DictReader(output)
    assert reader.fieldnames == columns
    rows = list(reader)
    assert len(rows) == 2
    for idx, row in enumerate(rows):
        for col in columns:
            assert row[col] == f"synthetic_{col}_{idx}"


def test_generate_synthetic_data_tabular_zero_volume():
    # Arrange
    data = valid_tabular_input(volume=0)

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    # Should generate CSV with only header
    assert result["status"] == "completed"
    output = io.StringIO(result["generated_data"])
    reader = csv.DictReader(output)
    rows = list(reader)
    assert len(rows) == 0
    assert reader.fieldnames == ["patient_id", "age", "diagnosis"]


def test_generate_synthetic_data_clinical_text_plain_text():
    # Arrange
    data = valid_clinical_text_input(volume=2)

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "completed"
    assert result["message"] == ""
    assert result["generated_data"].count("Synthetic patient note") == 2
    lines = result["generated_data"].split("\n")
    assert lines[0].startswith("Synthetic patient note 0:")
    assert lines[1].startswith("Synthetic patient note 1:")


def test_generate_synthetic_data_unsupported_data_type():
    # Arrange
    data = {
        "data_type": "image",
        "format": "jpeg",
        "volume": 1
    }

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "failed"
    assert result["message"] == "Unsupported data_type."
    assert result["generated_data"] is None


def test_generate_synthetic_data_missing_fields():
    # Arrange
    data = {}

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "failed"
    assert result["message"] == "Unsupported data_type."
    assert result["generated_data"] is None


def test_generate_synthetic_data_tabular_non_csv_format():
    # Arrange
    data = valid_tabular_input(format_="json")

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "completed"
    # Since format is not 'csv', returns list of dicts
    assert isinstance(result["generated_data"], list)
    for idx, row in enumerate(result["generated_data"]):
        assert set(row.keys()) == {"patient_id", "age", "diagnosis"}
        for col in row:
            assert row[col] == f"synthetic_{col}_{idx}"


def test_generate_synthetic_data_clinical_text_non_plain_text_format():
    # Arrange
    data = valid_clinical_text_input(format_="json")

    # Act
    result = synthetic_data_service.generate_synthetic_data(data)

    # Assert
    assert result["status"] == "completed"
    # Should be a list of strings
    assert isinstance(result["generated_data"], list)
    assert len(result["generated_data"]) == 2
    for idx, text in enumerate(result["generated_data"]):
        assert text.startswith(f"Synthetic patient note {idx}:")

@pytest.mark.parametrize(
    "data_type,format_,volume,expected_status",
    [
        ("tabular", "csv", 1, "completed"),
        ("clinical_text", "plain_text", 1, "completed"),
        ("nonsense", "any", 5, "failed")
    ]
)
def test_generate_synthetic_data_parametrized(data_type, format_, volume, expected_status):
    # Arrange
    data = {
        "data_type": data_type,
        "format": format_,
        "volume": volume
    }
    # Act
    result = synthetic_data_service.generate_synthetic_data(data)
    # Assert
    assert result["status"] == expected_status
    assert re.fullmatch(r"[0-9a-f\-]{36}", result["request_id"])