// components/EntityHighlights.js
import React from 'react';
import { Badge, ListGroup } from 'react-bootstrap';

// Displays highlighted medical entities found in AI analysis
const EntityHighlights = ({ highlights }) => {
  // Instructions:
  // 1. Check if the 'highlights' prop is undefined, null, or has a length of zero.
  //    - If so, return a <div> element with the text "No entities recognized." and a className of "text-muted".
  // 2. If 'highlights' has items:
  //    - Iterate (map) over each item in the 'highlights' array.
  //    - For each 'entity', render a ListGroup.Item:
  //      a. Display the entity's text (entity.text) inside a <strong> tag.
  //      b. Display a <Badge> with the entity's type (entity.type) and a variant of "info".
  //      c. If the entity has a 'confidence' value, render a <span> element:
  //         - The class should be "ml-2 text-success"
  //         - Text should say: "Confidence: {entity.confidence}%"
  //    - Ensure each ListGroup.Item has a unique 'key' (here 'idx' from .map).
  // 3. All ListGroup.Item elements should be wrapped inside a <ListGroup variant="flush"> element.
  //
  // Use the imports from 'react' and 'react-bootstrap' as shown.
  
};

export default EntityHighlights;
