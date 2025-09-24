// components/EntityHighlights.js
import React from 'react';
import { Badge, ListGroup } from 'react-bootstrap';

/**
 * Shows the named entities (diseases, drugs, etc.) AI detected in the source data.
 * @param {Object[]} highlights List of entity objects {text, type, confidence}
 */
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
          {entity.confidence != null && (
            <span className="ml-2 text-success">Confidence: {entity.confidence}%</span>
          )}
        </ListGroup.Item>
      ))}
    </ListGroup>
  );
};

export default EntityHighlights;