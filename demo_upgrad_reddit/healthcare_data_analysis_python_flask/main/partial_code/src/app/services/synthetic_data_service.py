import uuid

def generate_synthetic_data(data):
    # Retrieve necessary input values from the 'data' dictionary
    data_type = data.get("data_type")        # Type of data to generate (e.g., 'tabular', 'clinical_text')
    format_ = data.get("format")              # Desired output format (e.g., 'csv', 'plain_text')
    volume = data.get("volume")               # Amount of data to generate (number of rows or texts)
    options = data.get("options", {})          # Additional generation options (e.g., columns for tabular)
    request_id = str(uuid.uuid4())             # Generate a unique request ID for this generation job
    generated_data = None                      # Variable to hold the output data
    status = "completed"                      # Status of the generation process (default: 'completed')
    message = ""                               # Message for errors or additional information

    # Start logic for data generation below:
    # 1. Check the data_type. Implement different logic for each supported type (e.g., 'tabular', 'clinical_text').
    #  - For 'tabular':
    #      a. Use 'options' to get a list of columns (default to ['patient_id', 'age', 'diagnosis']).
    #      b. Generate a number of rows equal to 'volume'.
    #      c. Each row should be a dictionary with column names as keys and synthetic data as values (e.g., 'synthetic_{col}_{i}').
    #      d. If format_ == 'csv', write this list of dicts to a CSV string.
    #  - For 'clinical_text':
    #      a. Generate a number of synthetic text notes equal to 'volume'.
    #      b. Each note can be a string, such as a synthetic or template patient note. 
    #      c. If format_ == 'plain_text', join the notes into a single plain text string separated by newlines.
    # 2. If data_type is not supported, set status to 'failed', set generated_data to None, and set an appropriate message (e.g., 'Unsupported data_type.').
    # 3. Return a dictionary with 'request_id', 'status', 'generated_data', and 'message'.
    #
    # Use the declared variables (data_type, format_, volume, options, request_id, generated_data, status, message) to implement the above logic and prepare your output accordingly.

    pass  # Remove this after adding your implementation as per instructions above
