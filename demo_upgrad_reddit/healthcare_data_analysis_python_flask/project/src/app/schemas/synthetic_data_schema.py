from marshmallow import Schema, fields

class SyntheticDataRequestSchema(Schema):
    data_type = fields.Str(required=True, description="Type of synthetic data (e.g., 'tabular', 'clinical_text').")
    format = fields.Str(required=True, description="Output format (e.g., 'json', 'csv', 'plain_text').")
    volume = fields.Int(required=True, description="Number of synthetic records or data units to generate.")
    options = fields.Dict(required=False, description="Additional generation parameters (e.g., column specs, model type).")

class SyntheticDataResponseSchema(Schema):
    request_id = fields.Str(required=True, description="Unique identifier for the synthetic data request.")
    status = fields.Str(required=True, description="Generation status: 'completed', 'pending', 'failed'.")
    generated_data = fields.Raw(required=True, description="The generated synthetic data in requested format.")
    message = fields.Str(required=False, description="Additional info about the generation process.")