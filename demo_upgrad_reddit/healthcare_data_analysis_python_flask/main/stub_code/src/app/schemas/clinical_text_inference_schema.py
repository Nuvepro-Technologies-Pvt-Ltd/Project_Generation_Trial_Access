class ClinicalEntitySchema(Schema):
    # TODO: Define the field for 'type' as a required string
    # TODO: Define the field for 'span' as a required string
    # TODO: Define the field for 'value' as a required string
    pass

class ClinicalTextInferenceInputSchema(Schema):
    # TODO: Define a required string field 'text' with proper metadata for description
    # TODO: Define an optional string field 'patient_id' with metadata for description
    # TODO: Define an optional string field 'model_version' with metadata for description
    pass

class ClinicalTextInferenceResponseSchema(Schema):
    # TODO: Define a required string field 'status'
    # TODO: Define a required list field 'entities' containing nested ClinicalEntitySchema
    # TODO: Define a required list field 'labels' containing strings
    pass
