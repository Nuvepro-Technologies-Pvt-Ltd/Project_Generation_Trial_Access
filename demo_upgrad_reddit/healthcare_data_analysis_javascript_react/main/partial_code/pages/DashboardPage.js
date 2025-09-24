// pages/DashboardPage.js
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Button } from 'react-bootstrap';
import EntityHighlights from '../components/EntityHighlights';
import SummaryStatistics from '../components/SummaryStatistics';
import SyntheticDataTable from '../components/SyntheticDataTable';
import { fetchAIResults, fetchSyntheticData } from '../services/api';

const DashboardPage = () => {
  // State for storing AI analysis results
  const [aiResults, setAiResults] = useState(null);
  // State for holding the generated synthetic data
  const [syntheticData, setSyntheticData] = useState([]);
  // Loading flag to indicate ongoing fetch operation
  const [loading, setLoading] = useState(false);
  // Error message holder
  const [error, setError] = useState('');
  // Timestamp to trigger reloads
  const [reloadTs, setReloadTs] = useState(Date.now());

  // useEffect: Fetch dashboard data (AI results and synthetic data) when the component mounts or reloadTs changes
  useEffect(() => {
    // 1. Set loading state to true and clear any previous error.
    // 2. Use Promise.all to fetch both AI results and synthetic data in parallel using fetchAIResults and fetchSyntheticData functions.
    // 3. On successful fetch, update aiResults and syntheticData state with fetched values, then set loading to false.
    // 4. If an error occurs during the fetch, set the error state with a user-friendly message and set loading to false.
  }, [reloadTs]);

  // Handler to manually reload dashboard data
  const handleRefresh = () => {
    // 1. Update 'reloadTs' with current timestamp. This will re-trigger the useEffect above, causing data to re-fetch.
  };

  return (
    <Container fluid className="bg-light min-vh-100 p-3">
      {/*
        1. Create a header row with the dashboard title and a 'Refresh Data' button on the right.
        2. If loading is true, display a centered Spinner and a loading message inside a Row/Col layout.
        3. If error contains a message, display an Alert variant="danger" with the error text.
        4. If not loading or error:
           a. Show a Row with two columns:
               - Left: Card containing <EntityHighlights highlights={aiResults?.entityHighlights || []} />. (Pass the highlights array from aiResults)
               - Right: Card containing <SummaryStatistics stats={aiResults?.summaryStats} />. (Pass the stats object from aiResults)
           b. Below: Card with a synthetic data table <SyntheticDataTable data={syntheticData} />. (Pass the syntheticData array)
        * Make sure to structure each section with appropriate Bootstrap Card, Row, and Col components for responsive layout.
      */}
    </Container>
  );
};

export default DashboardPage;
