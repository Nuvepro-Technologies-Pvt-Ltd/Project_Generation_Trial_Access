from marshmallow import Schema, fields

class SyntheticDataRequestSchema(Schema):
    data_type = fields.Str(required=True, description="Type of synthetic data (e.g., 'tabular', 'clinical_text').")
    format = fields.Str(required=True, description="Output format (e.g., 'json', 'csv', 'plain_text').")
    volume = fields.Int(required=True, description="Number of synthetic records or data units to generate.")
    options = fields.Dict(required=False, description="Additional generation parameters (e.g., column specs, model type).")
    # Instructions: 
    # This schema defines the input required for a synthetic data generation request.
    # - Ensure 'data_type', 'format', and 'volume' are required fields and validate their types.
    # - 'options' is an optional dictionary for additional parameters. 
    # - Do not add custom logic here; use this schema to deserialize and validate incoming JSON data for POST requests.

class SyntheticDataResponseSchema(Schema):
    request_id = fields.Str(required=True, description="Unique identifier for the synthetic data request.")
    status = fields.Str(required=True, description="Generation status: 'completed', 'pending', 'failed'.")
    generated_data = fields.Raw(required=True, description="The generated synthetic data in requested format.")
    message = fields.Str(required=False, description="Additional info about the generation process.")
    # Instructions:
    # This schema defines the structure of the API's response to a synthetic data generation request.
    # - Ensure 'request_id', 'status', and 'generated_data' are included and their types are correctly validated.
    # - 'message' is optional and should contain any supplementary information about the response.
    # - Use this schema for serializing response data from the backend to the client; no method logic to implement here.
