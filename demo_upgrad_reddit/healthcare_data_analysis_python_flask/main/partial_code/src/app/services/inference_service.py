def run_inference(data):
    # Extract patient_id from the incoming data dictionary. This will be used to keep track of the patient for whom inference is being run.
    patient_id = data.get("patient_id")
    
    # Extract the list of symptoms from the data. If symptoms are not provided, default to an empty list.
    symptoms = data.get("symptoms", [])
    
    # Extract the clinical text that describes the patient's condition. Default to an empty string if not provided.
    clinical_text = data.get("clinical_text", "")
    
    # TODO: Implement the logic to perform AI model inference based on the input data.
    # Steps to implement:
    # 1. Use the extracted 'symptoms' and 'clinical_text' features to generate predictions for diagnosis.
    # 2. Initialize variables like 'diagnosis', 'confidence', and 'entities'.
    #    - 'diagnosis' should be set to the predicted diagnostic label (e.g., 'Flu', 'COVID-19', etc.).
    #    - 'confidence' should represent the probability or confidence score of the prediction.
    #    - 'entities' should be a list capturing information extracted from 'clinical_text' such as symptoms, findings, or other relevant entities with their attributes.
    # 3. If 'clinical_text' is not empty, use NLP techniques or extraction logic to extract named entities that are relevant (e.g., symptom mentions), and populate the 'entities' list with dictionaries containing details such as 'entity', 'label', and 'value'.
    # 4. Return the results as a dictionary containing the keys 'diagnosis', 'confidence', and 'entities'.
    
    # Example variables already declared for you:
    # diagnosis = None
    # confidence = 0.0
    # entities = []
    
    # Replace the following line with your implemented logic as described in the steps above.
    pass