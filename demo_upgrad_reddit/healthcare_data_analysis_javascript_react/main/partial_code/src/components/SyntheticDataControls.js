// components/SyntheticDataControls.js
import React, { useState } from 'react';
import { Form, Button, Row, Col, Spinner, Alert, InputGroup } from 'react-bootstrap';

/**
 * UI for user to request new synthetic data from backend.
 * Allows config of generation params: count, data type, privacy level.
 * On success triggers the onSuccess callback with API result.
 */
function SyntheticDataControls({ onGenerate, loading, error }) {
  // Form fields for API params
  const [recordCount, setRecordCount] = useState(10);  // Holds the number of records user wants to generate
  const [dataType, setDataType] = useState('EHR');     // Stores the data type selected by the user
  const [privacyLevel, setPrivacyLevel] = useState('high'); // Stores the privacy level selected
  const [validated, setValidated] = useState(false);       // Tracks if the form was validated/submitted

  // Options for dropdowns - can be adjusted according to backend schema
  const DATA_TYPE_OPTIONS = [
    { label: 'Electronic Health Record (EHR)', value: 'EHR' },
    { label: 'Claims', value: 'CLAIMS' },
    { label: 'Demographics', value: 'DEMOGRAPHICS' },
  ];
  const PRIVACY_LEVEL_OPTIONS = [
    { label: 'High (Maximum anonymization)', value: 'high' },
    { label: 'Moderate', value: 'medium' },
    { label: 'Minimal (Best data quality)', value: 'low' },
  ];

  // Handler for form submission (validates and triggers API call)
  const handleSubmit = evt => {
    // BEGIN LOGIC
    // 1. Prevent the default form submission behavior by calling evt.preventDefault().
    // 2. Mark the form as validated using setValidated(true).
    // 3. Add validation:
    //    - Check if recordCount is in the allowed range (>=1 and <=1000).
    //    - If not valid, do not proceed (simply return from the function).
    // 4. If the onGenerate callback prop is provided, call it with an object containing:
    //      record_count: value from recordCount
    //      data_type: value from dataType
    //      privacy_level: value from privacyLevel
    //    This should trigger the parent's data generation logic.
    // END LOGIC
  };

  return (
    // BEGIN RENDERING INSTRUCTIONS
    // Render a <Form> containing:
    //   - A number input for 'Number of Records' bound to recordCount, with min/max validation and disabled=true if loading
    //   - A select dropdown for 'Data Type', showing labels from DATA_TYPE_OPTIONS, bound to dataType, disabled if loading
    //   - A select dropdown for 'Privacy Level', showing labels from PRIVACY_LEVEL_OPTIONS, bound to privacyLevel, disabled if loading
    //   - A submit button that is disabled if loading; if loading is true, show a <Spinner>, else the text 'Generate Data'
    //   - If there's a non-null error prop, display it in a Bootstrap <Alert> below the form
    //   - Use form validation feedbacks as in the original solution for invalid fields
    // END RENDERING INSTRUCTIONS
  );
}

export default SyntheticDataControls;
