class InferenceRequestSchema(Schema):
    # Define a required string field for patient_id with a descriptive docstring.
    # Define an optional list of strings for symptoms with a descriptive docstring.
    # Define an optional string field for clinical_text with a descriptive docstring.
    pass

class InferenceEntitySchema(Schema):
    # Define a required string field for entity with a descriptive docstring.
    # Define a required string field for label with a descriptive docstring.
    # Define a required string field for value with a descriptive docstring.
    pass

class InferenceResponseSchema(Schema):
    # Define a required string field for diagnosis with a descriptive docstring.
    # Define a required float field for confidence with a descriptive docstring.
    # Define an optional list of nested InferenceEntitySchema objects for entities with a descriptive docstring.
    pass
