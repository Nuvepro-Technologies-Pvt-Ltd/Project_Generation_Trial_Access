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
  const [recordCount, setRecordCount] = useState(10);
  const [dataType, setDataType] = useState('EHR');
  const [privacyLevel, setPrivacyLevel] = useState('high');
  const [validated, setValidated] = useState(false);

  // Options could be adapted if backend provides schema
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
    evt.preventDefault();
    // Simple validation
    setValidated(true);
    if (recordCount < 1 || recordCount > 1000) return;
    if (onGenerate) {
      onGenerate({
        record_count: recordCount,
        data_type: dataType,
        privacy_level: privacyLevel
      });
    }
  };

  return (
    <Form noValidate validated={validated} onSubmit={handleSubmit} className="mb-3">
      <Row className="align-items-end">
        <Col md={3} sm={6} xs={12} className="mb-2">
          <Form.Group controlId="formRecordCount">
            <Form.Label>Number of Records</Form.Label>
            <InputGroup>
              <Form.Control
                type="number"
                min={1}
                max={1000}
                value={recordCount}
                required
                onChange={e => setRecordCount(parseInt(e.target.value, 10) || 1)}
                disabled={loading}
              />
              <InputGroup.Append>
                <InputGroup.Text>rows</InputGroup.Text>
              </InputGroup.Append>
              <Form.Control.Feedback type="invalid">Enter 1-1000 records</Form.Control.Feedback>
            </InputGroup>
          </Form.Group>
        </Col>
        <Col md={4} sm={6} xs={12} className="mb-2">
          <Form.Group controlId="formDataType">
            <Form.Label>Data Type</Form.Label>
            <Form.Control
              as="select"
              value={dataType}
              onChange={e => setDataType(e.target.value)}
              disabled={loading}
              required
            >
              {DATA_TYPE_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </Form.Control>
            <Form.Control.Feedback type="invalid">Please select a data type</Form.Control.Feedback>
          </Form.Group>
        </Col>
        <Col md={3} sm={6} xs={12} className="mb-2">
          <Form.Group controlId="formPrivacyLevel">
            <Form.Label>Privacy Level</Form.Label>
            <Form.Control
              as="select"
              value={privacyLevel}
              onChange={e => setPrivacyLevel(e.target.value)}
              disabled={loading}
              required
            >
              {PRIVACY_LEVEL_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </Form.Control>
            <Form.Control.Feedback type="invalid">Please select privacy</Form.Control.Feedback>
          </Form.Group>
        </Col>
        <Col md={2} sm={6} xs={12} className="mb-2 text-right">
          <Button variant="success" type="submit" disabled={loading} block>
            {loading ? <Spinner animation="border" size="sm" /> : 'Generate Data'}
          </Button>
        </Col>
      </Row>
      {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
    </Form>
  );
}

export default SyntheticDataControls;
