from marshmallow import Schema, fields

class InferenceRequestSchema(Schema):
    # Define a required string field 'patient_id' to uniquely identify each patient.
    patient_id = fields.Str(required=True, description="Unique patient identifier.")
    # Optionally, include a list of symptom strings if provided.
    symptoms = fields.List(fields.Str(), required=False, description="List of patient symptoms.")
    # Optionally, include a string containing free text clinical notes about the patient.
    clinical_text = fields.Str(required=False, description="Free text clinical notes.")
    #
    # INSTRUCTIONS:
    # No additional logic is required inside this schema. Marshmallow uses these field declarations
    # to handle serialization and deserialization of request data. You may add validation/custom logic by
    # defining 'validate_' methods or by overriding 'load'/'dump' if needed.

class InferenceEntitySchema(Schema):
    # Define a required string for the extracted entity.
    entity = fields.Str(required=True, description="Extracted entity.")
    # Define a required string for the entity label/type.
    label = fields.Str(required=True, description="Entity label/type.")
    # Define a required string for the value found in the text.
    value = fields.Str(required=True, description="Entity value found in text.")
    #
    # INSTRUCTIONS:
    # Make sure you use this schema for any structure representing an extracted entity in the inference response.
    # If you need to customize how entities are serialized, provide field-level validation or implement custom methods.

class InferenceResponseSchema(Schema):
    # Define a required string field for the predicted diagnosis.
    diagnosis = fields.Str(required=True, description="Predicted diagnosis result.")
    # Define a required float field for the confidence score of the prediction.
    confidence = fields.Float(required=True, description="Confidence score of the prediction.")
    # Optionally, include a list of InferenceEntitySchema representing the extracted entities.
    entities = fields.List(fields.Nested(InferenceEntitySchema), required=False, description="List of extracted healthcare entities.")
    #
    # INSTRUCTIONS:
    # Use this schema to serialize/deserialize inference results when responding to an API request.
    # Add any additional logic for post-processing output or validation as needed by customizing methods on this class.
