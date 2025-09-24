import uuid

def generate_synthetic_data(data):
    data_type = data.get("data_type")
    format_ = data.get("format")
    volume = data.get("volume")
    options = data.get("options", {})
    request_id = str(uuid.uuid4())
    generated_data = None
    status = "completed"
    message = ""
    if data_type == "tabular":
        generated_data = []
        columns = options.get("columns", ["patient_id", "age", "diagnosis"])
        for i in range(volume):
            row = {col: f"synthetic_{col}_{i}" for col in columns}
            generated_data.append(row)
        if format_ == "csv":
            import io, csv
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(generated_data)
            generated_data = output.getvalue()
    elif data_type == "clinical_text":
        generated_data = []
        for i in range(volume):
            text = f"Synthetic patient note {i}: The patient shows no sign of infection. No past medical history."
            generated_data.append(text)
        if format_ == "plain_text":
            generated_data = "
".join(generated_data)
    else:
        status = "failed"
        generated_data = None
        message = "Unsupported data_type."
    return {
        "request_id": request_id,
        "status": status,
        "generated_data": generated_data,
        "message": message
    }