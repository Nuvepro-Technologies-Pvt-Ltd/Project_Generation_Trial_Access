def run_inference(data):
    patient_id = data.get("patient_id")
    symptoms = data.get("symptoms", [])
    clinical_text = data.get("clinical_text", "")
    diagnosis = "Flu"
    confidence = 0.95
    entities = []
    if clinical_text:
        entities = [
            {
                "entity": "Cough",
                "label": "symptom",
                "value": "present"
            },
            {
                "entity": "Fever",
                "label": "symptom",
                "value": "present"
            }
        ]
    return {
        "diagnosis": diagnosis,
        "confidence": confidence,
        "entities": entities
    }