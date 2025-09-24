// components/EntityHighlights.js
import React from 'react';
import { Badge, ListGroup } from 'react-bootstrap';

/**
 * Shows the named entities (diseases, drugs, etc.) AI detected in the source data.
 * @param {Object[]} highlights List of entity objects {text, type, confidence}
 */
const EntityHighlights = ({ highlights }) => {
  // Instructions:
  // 1. Check if the 'highlights' prop is not present or if its length is zero.
  //    - If this is true, render a <div> element with a class of "text-muted" and text content "No entities recognized."
  //    - Then return, so the rest of the code does not execute.

  // 2. If 'highlights' exists and is not empty, render a ListGroup (from react-bootstrap) with variant "flush".
  //    - For each entity object in the highlights array, create a ListGroup.Item as a child component.
  //    - Use 'idx' as the unique 'key' prop for each ListGroup.Item.
  //      * Inside each ListGroup.Item:
  //         - Display the entity's text in a <strong> tag.
  //         - Add a Badge (variant="info") right after the text, showing the 'type' of the entity.
  //         - If the 'confidence' property exists (i.e., is not null or undefined), display a <span> element with the className "ml-2 text-success" with the label "Confidence: {entity.confidence}%"
  // 3. Make sure to properly close and nest the returned JSX as per React requirements.
};

export default EntityHighlights;