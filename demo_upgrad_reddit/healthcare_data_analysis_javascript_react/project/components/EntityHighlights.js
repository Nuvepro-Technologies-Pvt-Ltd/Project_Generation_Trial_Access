// components/EntityHighlights.js
import React from 'react';
import { Badge, ListGroup } from 'react-bootstrap';

// Displays highlighted medical entities found in AI analysis
const EntityHighlights = ({ highlights }) => {
  if (!highlights || highlights.length === 0) {
    return <div className="text-muted">No entities recognized.</div>;
  }
  return (
    <ListGroup variant="flush">
      {highlights.map((entity, idx) => (
        <ListGroup.Item key={idx}>
          <strong>{entity.text}</strong> {' '}
          <Badge variant="info">{entity.type}</Badge>
          {entity.confidence && (
            <span className="ml-2 text-success">Confidence: {entity.confidence}%</span>
          )}
        </ListGroup.Item>
      ))}
    </ListGroup>
  );
};

export default EntityHighlights;
