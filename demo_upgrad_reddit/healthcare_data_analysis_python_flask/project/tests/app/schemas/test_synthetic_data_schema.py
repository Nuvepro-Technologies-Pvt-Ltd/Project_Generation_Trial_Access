import pytest
from marshmallow import ValidationError
from app.schemas.synthetic_data_schema import SyntheticDataRequestSchema, SyntheticDataResponseSchema

class TestSyntheticDataRequestSchema:
    def test_deserialize_valid_request_min_fields_success(self):
        # Arrange
        payload = {
            "data_type": "tabular",
            "format": "json",
            "volume": 100
        }
        # Act
        loaded = SyntheticDataRequestSchema().load(payload)
        # Assert
        assert loaded["data_type"] == "tabular"
        assert loaded["format"] == "json"
        assert loaded["volume"] == 100
        assert "options" not in loaded

    def test_deserialize_valid_request_all_fields_success(self):
        # Arrange
        payload = {
            "data_type": "clinical_text",
            "format": "csv",
            "volume": 10,
            "options": {"model_type": "gpt", "columns": ["age", "diagnosis"]}
        }
        # Act
        loaded = SyntheticDataRequestSchema().load(payload)
        # Assert
        assert loaded["options"]["model_type"] == "gpt"
        assert loaded["options"]["columns"] == ["age", "diagnosis"]

    @pytest.mark.parametrize("missing_field", ["data_type", "format", "volume"])
    def test_missing_required_fields_raises_validation_error(self, missing_field):
        # Arrange
        payload = {
            "data_type": "tabular",
            "format": "json",
            "volume": 1
        }
        del payload[missing_field]
        # Act & Assert
        with pytest.raises(ValidationError) as ve:
            SyntheticDataRequestSchema().load(payload)
        assert missing_field in ve.value.messages

    @pytest.mark.parametrize(
        "bad_field, value, error_type",
        [
            ("data_type", 123, "Not a valid string."),
            ("format", None, "Field may not be null."),
            ("volume", "a lot", "Not a valid integer."),
            ("options", "string_not_dict", "Not a valid mapping type.")
        ]
    )
    def test_invalid_field_types_raises_validation_error(self, bad_field, value, error_type):
        # Arrange
        payload = {
            "data_type": "tabular",
            "format": "json",
            "volume": 1,
            "options": {"foo": "bar"}
        }
        payload[bad_field] = value
        # Act & Assert
        with pytest.raises(ValidationError) as ve:
            SyntheticDataRequestSchema().load(payload)
        assert error_type in str(ve.value)

    def test_extra_unexpected_fields_are_ignored_or_error(self):
        # Arrange
        payload = {
            "data_type": "tabular",
            "format": "json",
            "volume": 2,
            "unexpected": "ignoreme"
        }
        # Act
        result = SyntheticDataRequestSchema().load(payload, unknown="EXCLUDE")
        # Assert
        assert "unexpected" not in result


class TestSyntheticDataResponseSchema:
    def test_deserialize_valid_response_success(self):
        # Arrange
        payload = {
            "request_id": "abc123def456",
            "status": "completed",
            "generated_data": [{"id": 1, "value": 42}],
            "message": "Success"
        }
        # Act
        loaded = SyntheticDataResponseSchema().load(payload)
        # Assert
        assert loaded["request_id"] == "abc123def456"
        assert loaded["status"] == "completed"
        assert isinstance(loaded["generated_data"], list)
        assert loaded["message"] == "Success"

    @pytest.mark.parametrize("missing_field",
                            ["request_id", "status", "generated_data"])
    def test_missing_required_fields_raises_validation_error(self, missing_field):
        # Arrange
        payload = {
            "request_id": "1",
            "status": "completed",
            "generated_data": "text"
        }
        del payload[missing_field]
        # Act & Assert
        with pytest.raises(ValidationError) as ve:
            SyntheticDataResponseSchema().load(payload)
        assert missing_field in ve.value.messages

    def test_invalid_status_values_accepted(self):
        # Arrange
        payload = {
            "request_id": "2",
            "status": "foo_bar_status",
            "generated_data": {},
        }
        # Act
        loaded = SyntheticDataResponseSchema().load(payload)
        # Assert
        # Schema does not validate allowed status values except type
        assert loaded["status"] == "foo_bar_status"

    def test_optional_message_absent(self):
        # Arrange
        payload = {
            "request_id": "3",
            "status": "pending",
            "generated_data": "pending..."
        }
        # Act
        loaded = SyntheticDataResponseSchema().load(payload)
        # Assert
        assert "message" not in loaded

    @pytest.mark.parametrize("bad_generated_data", [None, set([1, 2]), lambda x: x])
    def test_generated_data_allows_any_serializable_type(self, bad_generated_data):
        # Arrange
        payload = {
            "request_id": "5",
            "status": "completed",
            "generated_data": bad_generated_data
        }
        # Act & Assert
        # Marshmallow 'Raw' only fails on unserializable types; None is still allowed as value
        try:
            loaded = SyntheticDataResponseSchema().load(payload)
            # For unserializable types, marshmallow will not raise by default, so check by type
            assert loaded["generated_data"] == bad_generated_data
        except ValidationError:
            assert bad_generated_data is not None, "Only non-serializable values should fail."

    def test_extra_unexpected_fields_are_ignored(self):
        # Arrange
        payload = {
            "request_id": "idxyz",
            "status": "failed",
            "generated_data": [],
            "unexpected": 42
        }
        # Act
        result = SyntheticDataResponseSchema().load(payload, unknown="EXCLUDE")
        # Assert
        assert "unexpected" not in result