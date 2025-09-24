class HealthcareMLflowExperimentTracker:
    """
    Tracks ML experiments using MLflow for Healthcare AI pipelines.
    Captures parameters, metrics, and artifacts for each run.
    """
    def __init__(self, experiment_name: str = "HealthcareRiskPrediction"):
        # Initialize the experiment tracker with the provided experiment name
        # Set the MLflow experiment
        # Set up basic logging configuration
        pass

    def load_healthcare_data(self, file_path: str):
        """Loads healthcare dataset from the provided path."""
        # Implement loading the dataset from file_path
        # Raise FileNotFoundError if file does not exist
        # Return the loaded DataFrame
        pass

    def preprocess(self, data):
        """Preprocesses input data for ML training."""
        # Check if 'target' column is in data
        # Raise an error if target column is missing
        # Separate features (X) and target (y)
        # Impute missing values as required
        # Return imputed X and y
        pass

    def run_training_experiment(self, data_path: str, n_estimators: int, max_depth: int, random_state: int) -> str:
        """
        Executes a single experiment run, logs to MLflow.
        Returns the run_id of the experiment.
        """
        # Load data and preprocess it
        # Split data into train and test sets
        # Initialize and train the RandomForestClassifier model
        # Log parameters, metrics, and artifacts to MLflow
        # Save test arrays as artifacts
        # Return the run id
        pass

    def get_best_run(self, metric_name: str = 'roc_auc', maximize: bool = True) -> dict:
        """
        Retrieves the best MLflow run details based on metric_name.
        """
        # Connect to MLflow tracking server
        # Search runs for the current experiment
        # Find the run with the best (max or min) value for metric_name
        # Return the run details (run_id, metrics, params)
        pass

if __name__ == "__main__":
    # Create an instance of the experiment tracker
    # Construct the absolute path of the healthcare data CSV file
    # Run at least two training experiments with different parameters
    # Retrieve and print details of the best run based on the chosen metric
    pass
