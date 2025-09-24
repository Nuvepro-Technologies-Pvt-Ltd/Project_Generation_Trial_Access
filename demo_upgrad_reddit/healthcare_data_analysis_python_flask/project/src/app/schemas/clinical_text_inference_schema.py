from marshmallow import Schema, fields, validate

class ClinicalEntitySchema(Schema):
    type = fields.String(required=True)
    span = fields.String(required=True)
    value = fields.String(required=True)

class ClinicalTextInferenceInputSchema(Schema):
    text = fields.String(required=True, metadata={"description": "Clinical note, discharge summary, or other medical text."})
    patient_id = fields.String(allow_none=True, metadata={"description": "Optional patient identifier (de-identified or hashed)."})
    model_version = fields.String(allow_none=True, metadata={"description": "Specific AI model version to use."})

class ClinicalTextInferenceResponseSchema(Schema):
    status = fields.String(required=True)
    entities = fields.List(fields.Nested(ClinicalEntitySchema), required=True)
    labels = fields.List(fields.String(), required=True)
