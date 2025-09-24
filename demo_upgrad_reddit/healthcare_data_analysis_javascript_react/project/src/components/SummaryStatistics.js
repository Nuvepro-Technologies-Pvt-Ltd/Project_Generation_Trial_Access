// components/SummaryStatistics.js
import React from 'react';
import { Row, Col } from 'react-bootstrap';

/**
 * Shows summary statistics extracted by AI (e.g., patient count, avg value, etc)
 * @param {Object} stats Dictionary of statistics (stat name: value)
 */
const SummaryStatistics = ({ stats }) => {
  if (!stats) {
    return <div className="text-muted">No statistics available.</div>;
  }
  return (
    <Row>
      {Object.entries(stats).map(([stat, value], idx) => (
        <Col key={idx} sm={6} md={4} className="mb-2">
          <div className="border bg-white rounded p-2 text-center h-100">
            <div className="h5 mb-1">{stat.replace(/([A-Z])/g, ' $1')}</div>
            <div className="display-4">{value}</div>
          </div>
        </Col>
      ))}
    </Row>
  );
};

export default SummaryStatistics;