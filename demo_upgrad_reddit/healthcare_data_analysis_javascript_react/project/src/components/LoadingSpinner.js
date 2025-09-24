// src/components/LoadingSpinner.js
import React from "react";

/**
 * Simple Bootstrap spinner centered on the page, used while loading data.
 */
function LoadingSpinner() {
  return (
    <div className="d-flex justify-content-center align-items-center my-5">
      <div className="spinner-border text-primary" role="status" aria-label="Loading...">
        <span className="visually-hidden">Loading...</span>
      </div>
    </div>
  );
}

export default LoadingSpinner;
