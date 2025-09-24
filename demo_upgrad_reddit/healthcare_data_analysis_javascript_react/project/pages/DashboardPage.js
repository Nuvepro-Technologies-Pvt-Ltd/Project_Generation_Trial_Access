// pages/DashboardPage.js
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Button } from 'react-bootstrap';
import EntityHighlights from '../components/EntityHighlights';
import SummaryStatistics from '../components/SummaryStatistics';
import SyntheticDataTable from '../components/SyntheticDataTable';
import { fetchAIResults, fetchSyntheticData } from '../services/api';

const DashboardPage = () => {
  // State for AI results, synthetic data, loading and error flags
  const [aiResults, setAiResults] = useState(null);
  const [syntheticData, setSyntheticData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [reloadTs, setReloadTs] = useState(Date.now()); // triggers refresh on change

  // Fetch dashboard data (AI results and synthetic data) on mount and on reload
  useEffect(() => {
    setLoading(true);
    setError('');
    Promise.all([fetchAIResults(), fetchSyntheticData()])
      .then(([aiRes, synthData]) => {
        setAiResults(aiRes);
        setSyntheticData(synthData);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load dashboard data. Please try again.');
        setLoading(false);
      });
  }, [reloadTs]);

  // Handler to manually trigger data reload
  const handleRefresh = () => setReloadTs(Date.now());

  return (
    <Container fluid className="bg-light min-vh-100 p-3">
      <Row className="mb-3">
        <Col>
          <h2 className="text-primary">AI-Driven Healthcare Data Dashboard</h2>
        </Col>
        <Col xs="auto">
          <Button variant="outline-primary" onClick={handleRefresh}>
            Refresh Data
          </Button>
        </Col>
      </Row>

      {loading && (
        <Row>
          <Col>
            <div className="text-center p-5">
              <Spinner animation="border" role="status" />
              <div>Loading dashboard data...</div>
            </div>
          </Col>
        </Row>
      )}
      {error && (
        <Row>
          <Col>
            <Alert variant="danger">{error}</Alert>
          </Col>
        </Row>
      )}
      {!loading && !error && (
        <>
          <Row className="mb-3">
            <Col md={6}>
              <Card className="mb-3">
                <Card.Header>Entity Recognition Highlights</Card.Header>
                <Card.Body>
                  {/* Highlights extracted entities in the healthcare data */}
                  <EntityHighlights highlights={aiResults?.entityHighlights || []} />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card className="mb-3">
                <Card.Header>Summary Statistics</Card.Header>
                <Card.Body>
                  {/* Provides key statistics from AI analysis */}
                  <SummaryStatistics stats={aiResults?.summaryStats} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
          <Row>
            <Col>
              <Card>
                <Card.Header>Generated Synthetic Data</Card.Header>
                <Card.Body>
                  {/* Table of generated synthetic entries for exploration */}
                  <SyntheticDataTable data={syntheticData} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </Container>
  );
};

export default DashboardPage;
