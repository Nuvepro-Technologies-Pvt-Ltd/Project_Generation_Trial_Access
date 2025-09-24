import json
import pytest
from unittest.mock import patch
from flask import Flask
from flask_smorest import Api
from src.app.routes.synthetic_data_routes import blp

class TestSyntheticDataRoutes:
    @pytest.fixture(autouse=True)
    def setup_app(self):
        # Arrange: Setup Flask test app and register blueprint
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['API_TITLE'] = 'Test API'
        app.config['API_VERSION'] = 'v1'
        app.config['OPENAPI_VERSION'] = '3.0.2'
        api = Api(app)
        api.register_blueprint(blp)
        self.client = app.test_client()

    @pytest.fixture
    def valid_headers(self):
        return {
            'Authorization': 'Bearer valid_token',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    @pytest.fixture
    def valid_body(self):
        return {
            'data_type': 'tabular',
            'format': 'csv',
            'volume': 10,
            'options': {'cols': 5}
        }

    @patch('src.app.routes.synthetic_data_routes.generate_synthetic_data')
    def test_post_synthetic_data_success(self, mock_generate, valid_headers, valid_body):
        # Arrange: Mock the service to return expected data
        mock_generate.return_value = {
            'request_id': 'req-123',
            'status': 'completed',
            'generated_data': {'dummy': 'data'},
            'message': 'Synthetic data generated successfully.'
        }
        # Act: Post valid data with auth header
        response = self.client.post(
            '/api/v1/synthetic-data/',
            data=json.dumps(valid_body),
            headers=valid_headers
        )
        # Assert: Status code and data
        assert response.status_code == 200, 'Should return 200 for valid request.'
        res_json = response.get_json()
        assert res_json['status'] == 'completed', 'Status should be completed.'
        assert res_json['request_id'] == 'req-123', 'Request ID should be present.'
        assert 'generated_data' in res_json, 'Should return generated_data.'
        assert res_json['message'] == 'Synthetic data generated successfully.'
        mock_generate.assert_called_once_with(valid_body)

    @pytest.mark.parametrize(
        'auth_header,expected_message', [
            ('', 'Missing or invalid Authorization header.'),
            ('InvalidToken', 'Missing or invalid Authorization header.'),
            ('Bearer', 'Missing or invalid Authorization header.'),
        ]
    )
    def test_post_synthetic_data_auth_failure(self, auth_header, expected_message, valid_body):
        # Arrange: Setup headers with invalid/missing authorization
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # Act: Send request
        response = self.client.post('/api/v1/synthetic-data/', data=json.dumps(valid_body), headers=headers)
        # Assert: Unauthorized
        assert response.status_code == 401, 'Should return 401 for missing/invalid auth.'
        res_json = response.get_json()
        assert expected_message in res_json['message'], 'Should return correct error message.'

    @pytest.mark.parametrize(
        'missing_field',
        ['data_type', 'format', 'volume']
    )
    def test_post_synthetic_data_missing_required_fields(self, missing_field, valid_headers, valid_body):
        # Arrange: Remove a required field
        body = dict(valid_body)
        del body[missing_field]
        # Act: Send request
        response = self.client.post('/api/v1/synthetic-data/', data=json.dumps(body), headers=valid_headers)
        # Assert: 422 for validation error
        assert response.status_code == 422, f'Missing field {missing_field} should yield 422.'
        res_json = response.get_json()
        assert 'messages' in res_json
        assert missing_field in str(res_json['messages']), f'Validation for field {missing_field} should be reported.'

    @patch('src.app.routes.synthetic_data_routes.generate_synthetic_data')
    def test_post_synthetic_data_service_failure(self, mock_generate, valid_headers, valid_body):
        # Arrange: Mock the service to throw an Exception
        mock_generate.side_effect = Exception('Service error occurred')
        # Act: Send request
        response = self.client.post('/api/v1/synthetic-data/', data=json.dumps(valid_body), headers=valid_headers)
        # Assert: Should produce a 500 Internal Server Error
        assert response.status_code == 500, 'Should return 500 when service fails.'
        res_json = response.get_json()
        assert 'Service error occurred' in str(res_json), 'Error message should propagate.'

    def test_post_synthetic_data_large_volume(self, valid_headers, valid_body):
        # Arrange: Test upper boundary (simulate, not full load)
        body = dict(valid_body)
        body['volume'] = 10000
        with patch('src.app.routes.synthetic_data_routes.generate_synthetic_data') as mock_generate:
            mock_generate.return_value = {
                'request_id': 'req-lv',
                'status': 'pending',
                'generated_data': None,
                'message': 'Job scheduled.'
            }
            response = self.client.post('/api/v1/synthetic-data/', data=json.dumps(body), headers=valid_headers)
        # Assert: Accept request, return pending status
        assert response.status_code == 200, 'Should accept large volumes.'
        res_json = response.get_json()
        assert res_json['status'] == 'pending', 'Status should be pending for large job.'
        assert res_json['request_id'] == 'req-lv', 'Req ID must be correct.'
        assert res_json['generated_data'] is None, 'Generation result may be None.'
        assert res_json['message'] == 'Job scheduled.'

    @pytest.mark.parametrize(
        'body', [
            {'data_type': 'INVALID', 'format': 'csv', 'volume': 10},
            {'data_type': 'tabular', 'format': '', 'volume': 10},
            {'data_type': 'tabular', 'format': 'csv', 'volume': -100},
        ]
    )
    def test_post_synthetic_data_invalid_input_types(self, body, valid_headers):
        # Act: Send request with invalid data_type, empty format, or negative volume
        response = self.client.post('/api/v1/synthetic-data/', data=json.dumps(body), headers=valid_headers)
        # Assert: 422 validation error
        assert response.status_code == 422, 'Invalid payloads should be rejected.'
        res_json = response.get_json()
        assert 'messages' in res_json

    @patch('src.app.routes.synthetic_data_routes.generate_synthetic_data')
    def test_post_synthetic_data_options_optional(self, mock_generate, valid_headers, valid_body):
        # Arrange: Remove options to test optional nature
        body = dict(valid_body)
        if 'options' in body:
            del body['options']
        mock_generate.return_value = {
            'request_id': 'req-noopt',
            'status': 'completed',
            'generated_data': {},
            'message': 'No options specified.'
        }
        # Act: Send request
        response = self.client.post('/api/v1/synthetic-data/', data=json.dumps(body), headers=valid_headers)
        # Assert
        assert response.status_code == 200, 'Should handle missing options.'
        res_json = response.get_json()
        assert res_json['status'] == 'completed'
        assert res_json['message'] == 'No options specified.'

    # Add more tests for format/content negotiation if needed