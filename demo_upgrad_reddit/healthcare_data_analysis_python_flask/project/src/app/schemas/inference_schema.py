from marshmallow import Schema, fields

class InferenceRequestSchema(Schema):
    patient_id = fields.Str(required=True, description="Unique patient identifier.")
    symptoms = fields.List(fields.Str(), required=False, description="List of patient symptoms.")
    clinical_text = fields.Str(required=False, description="Free text clinical notes.")

class InferenceEntitySchema(Schema):
    entity = fields.Str(required=True, description="Extracted entity.")
    label = fields.Str(required=True, description="Entity label/type.")
    value = fields.Str(required=True, description="Entity value found in text.")

class InferenceResponseSchema(Schema):
    diagnosis = fields.Str(required=True, description="Predicted diagnosis result.")
    confidence = fields.Float(required=True, description="Confidence score of the prediction.")
    entities = fields.List(fields.Nested(InferenceEntitySchema), required=False, description="List of extracted healthcare entities.")