// components/AIResultsFilterExport.js
import React, { useState, useMemo } from 'react';
import { Row, Col, Form, Button, Badge, InputGroup, Alert } from 'react-bootstrap';

/**
 * Filtering & export controls for AI analysis results and synthetic data.
 * Props:
 *   - aiResults: { entityHighlights: [], summaryStats: {} }
 *   - syntheticData: [ {...} ]
 *   - onExport: (type, data, format) => void -- called to export filtered data
 *
 * Returns the filtered results and provides download for CSV/JSON export.
 */
function AIResultsFilterExport({
  aiResults = { entityHighlights: [], summaryStats: {} },
  syntheticData = [],
  onExport
}) {
  // Filter states
  const [patientAttr, setPatientAttr] = useState('');
  const [dataType, setDataType] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [exportType, setExportType] = useState('ai'); // 'ai' or 'synthetic'
  const [exportFormat, setExportFormat] = useState('csv'); // 'csv' or 'json'
  const [lastExportComplete, setLastExportComplete] = useState(false);

  // Derived set of patient attribute options based on data keys
  const patientAttrOptions = useMemo(() => {
    if (!syntheticData || syntheticData.length === 0) return [];
    const first = syntheticData[0] || {};
    // Pick up suggested patient fields
    return Object.keys(first).filter(k => ["patient_id","gender","age","diagnosis","visit_date","attribute"].includes(k));
  }, [syntheticData]);

  // DataType options: from syntheticData or entity types in AI highlights
  const dataTypeOptions = useMemo(() => {
    // Use unique 'type' from aiResults.entityHighlights and syntheticData
    const aiTypes = (aiResults?.entityHighlights || []).map(e => e.type);
    const synthTypes = syntheticData.map(row => row.data_type).filter(Boolean);
    return Array.from(new Set([ ...aiTypes, ...synthTypes ])).filter(Boolean);
  }, [aiResults, syntheticData]);

  // Filtered AI highlights
  const filteredHighlights = useMemo(() => {
    let highlights = [...(aiResults?.entityHighlights || [])];
    if (dataType) highlights = highlights.filter(e => e.type === dataType);
    // Date filter if AI results have 'visit_date' or similar field
    return highlights;
  }, [aiResults, dataType]);

  // Filtered synthetic data
  const filteredSynthetic = useMemo(() => {
    let rows = [...syntheticData];
    if (patientAttr && patientAttrOptions.includes(patientAttr)) {
      rows = rows.filter(row => row[patientAttr]);
    }
    if (dataType) {
      rows = rows.filter(row => row.data_type === dataType);
    }
    if (dateFrom) {
      rows = rows.filter(row => {
        const d = row.visit_date ? new Date(row.visit_date) : null;
        return d && !isNaN(d.valueOf()) && d >= new Date(dateFrom);
      });
    }
    if (dateTo) {
      rows = rows.filter(row => {
        const d = row.visit_date ? new Date(row.visit_date) : null;
        return d && !isNaN(d.valueOf()) && d <= new Date(dateTo);
      });
    }
    return rows;
  }, [syntheticData, patientAttr, patientAttrOptions, dataType, dateFrom, dateTo]);

  // Handler: Export currently filtered data
  const handleExport = (evt) => {
    evt.preventDefault();
    let exportData, fileName;
    if (exportType === 'ai') {
      exportData = filteredHighlights;
      fileName = 'ai_analysis_filtered.' + exportFormat;
    } else {
      exportData = filteredSynthetic;
      fileName = 'synthetic_data_filtered.' + exportFormat;
    }
    if (onExport) {
      onExport(exportType, exportData, exportFormat, fileName);
      setLastExportComplete(true);
      setTimeout(() => setLastExportComplete(false), 3000);
    }
  };

  // Render UI
  return (
    <Form onSubmit={handleExport} className="mb-3">
      <Row className="align-items-end">
        <Col md={3} sm={6} xs={12} className="mb-2">
          <Form.Group>
            <Form.Label>Patient Attribute</Form.Label>
            <Form.Control as="select" value={patientAttr} onChange={e => setPatientAttr(e.target.value)}>
              <option value="">(Any)</option>
              {patientAttrOptions.map(opt => (
                <option key={opt} value={opt}>{opt.replace(/_/g, ' ')}</option>
              ))}
            </Form.Control>
          </Form.Group>
        </Col>
        <Col md={3} sm={6} xs={12} className="mb-2">
          <Form.Group>
            <Form.Label>Data Type / Entity Type</Form.Label>
            <Form.Control as="select" value={dataType} onChange={e => setDataType(e.target.value)}>
              <option value="">(Any)</option>
              {dataTypeOptions.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </Form.Control>
          </Form.Group>
        </Col>
        <Col md={2} sm={6} xs={12} className="mb-2">
          <Form.Group>
            <Form.Label>Date From</Form.Label>
            <Form.Control type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          </Form.Group>
        </Col>
        <Col md={2} sm={6} xs={12} className="mb-2">
          <Form.Group>
            <Form.Label>Date To</Form.Label>
            <Form.Control type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
          </Form.Group>
        </Col>
        <Col md={2} xs={12} className="mb-2">
          <Form.Group>
            <Form.Label>Export</Form.Label>
            <InputGroup>
              <Form.Control as="select" value={exportType} onChange={e => setExportType(e.target.value)}>
                <option value="ai">AI Results</option>
                <option value="synthetic">Synthetic Data</option>
              </Form.Control>
              <Form.Control as="select" value={exportFormat} onChange={e => setExportFormat(e.target.value)}>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </Form.Control>
              <InputGroup.Append>
                <Button type="submit" variant="primary" title="Export filtered results">Export</Button>
              </InputGroup.Append>
            </InputGroup>
          </Form.Group>
          {lastExportComplete && <div className="mt-2"><Badge variant="success">Export complete!</Badge></div>}
        </Col>
      </Row>
      <Row>
        <Col xs={12}>
          <div>
            {(patientAttr || dataType || dateFrom || dateTo) && (
              <Badge variant="info" className="mr-2">Filters Active</Badge>
            )}
            {!patientAttr && !dataType && !dateFrom && !dateTo && (
              <Badge variant="secondary">No filters applied</Badge>
            )}
          </div>
        </Col>
      </Row>
    </Form>
  );
}

export default AIResultsFilterExport;
