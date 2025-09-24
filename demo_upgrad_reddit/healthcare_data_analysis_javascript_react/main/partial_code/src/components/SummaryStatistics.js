// components/SummaryStatistics.js
import React from 'react';
import { Row, Col } from 'react-bootstrap';

/**
 * Shows summary statistics extracted by AI (e.g., patient count, avg value, etc)
 * @param {Object} stats Dictionary of statistics (stat name: value)
 */
const SummaryStatistics = ({ stats }) => {
  // INSTRUCTION: Check if the 'stats' prop is not provided or falsy (e.g., null or undefined).
  // If 'stats' is falsy, return a div element with the text "No statistics available." styled with the class "text-muted".

  // INSTRUCTION: If 'stats' is provided, render a set of summary statistics.
  // Use React-Bootstrap's Row and Col components to layout statistics.
  // For each statistic entry (key-value pair) in the 'stats' object:
    // - Render each statistic in a separate Col component.
    // - Use a unique key for each Col (for example, the index of the entry).
    // - In each Col, render a styled div with these elements:
    //   1. The statistic's name, converted from camelCase (or PascalCase) to space-separated words, e.g., "avgValue" becomes "avg Value".
    //   2. The value of the statistic, styled with "display-4" class for emphasis.

  // INSTRUCTION: The entire list of stats should be wrapped inside a Row component for proper horizontal alignment.
};

export default SummaryStatistics;