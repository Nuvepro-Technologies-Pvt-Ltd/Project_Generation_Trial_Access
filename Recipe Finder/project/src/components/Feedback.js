// src/components/Feedback.js
// Minimal, accessible loading indicator and error feedback components
import React from 'react';

// Spinner + label, centered, minimal padding
export function LoadingIndicator({ message = 'Loading...' }) {
  return (
    <div className="text-center my-5" style={{ minHeight: 180 }}>
      <div className="spinner-border" role="status" aria-label="Loading"></div>
      <p className="mt-3 text-secondary" style={{fontSize: '1.07rem'}}>{message}</p>
    </div>
  );
}

// Error feedback, focusable for accessibility, optional retry
export function ErrorMessage({ error, onRetry }) {
  return (
    <div className="alert alert-danger text-center" role="alert" tabIndex={-1} style={{maxWidth: 480, margin: '1.6rem auto'}}>
      <span style={{fontWeight: 500}}>{error}</span>
      {onRetry && (
        <button type="button" className="btn btn-outline-primary mx-3 px-4 py-1" onClick={onRetry} style={{fontSize:'1em'}}>
          Try Again
        </button>
      )}
    </div>
  );
}
