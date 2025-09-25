// src/components/Feedback.js
// Minimal, accessible loading indicator and error feedback components

// Spinner + label, centered, minimal padding
export function LoadingIndicator({ message = 'Loading...' }) {
  // TODO: Render a centered spinner (with minimal typography and padding) and a label that displays the loading message.
  // Ensure accessibility with appropriate role and aria-label attributes.
}

// Error feedback, focusable for accessibility, optional retry
export function ErrorMessage({ error, onRetry }) {
  // TODO: Render an alert box with the error message, visually prominent, focusable for accessibility.
  // If onRetry is provided, render a button to trigger the retry action.
}
