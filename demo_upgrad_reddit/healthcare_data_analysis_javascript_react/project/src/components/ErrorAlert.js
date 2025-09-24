// src/components/ErrorAlert.js
import React from "react";

/**
 * Displays a Bootstrap alert for error messages, if any.
 */
function ErrorAlert({ message }) {
  return (
    <div className="alert alert-danger" role="alert">
      {message || "An error occurred."}
    </div>
  );
}

export default ErrorAlert;
