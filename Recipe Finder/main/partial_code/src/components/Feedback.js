// src/components/Feedback.js
// Minimal, accessible loading indicator and error feedback components
import React from 'react';

// Spinner + label, centered, minimal padding
export function LoadingIndicator({ message = 'Loading...' }) {
  // INSTRUCTIONS:
  // 1. Create a container div that centers its content both horizontally and vertically using CSS classes (e.g., 'text-center my-5').
  //    - Optionally add styling for minimum height (e.g., minHeight: 180) for layout stability.
  // 2. Inside this container, display a visual loading spinner for feedback.
  //    - Use an accessible HTML structure such as a <div> with 'spinner-border' class, and assign role="status" and aria-label="Loading" attributes.
  // 3. Under the spinner, display the provided 'message' prop using a <p> tag.
  //    - Style the text to be slightly muted (e.g., 'text-secondary'), give a minimal top margin, and adjust its font size for subtlety.
  // VARIABLES:
  // - message: The loading message to display under the spinner (defaults to "Loading...").
}

// Error feedback, focusable for accessibility, optional retry
export function ErrorMessage({ error, onRetry }) {
  // INSTRUCTIONS:
  // 1. Create an alert container div with classes for error styling (e.g., 'alert alert-danger text-center').
  //    - Set the role to 'alert' and provide tabIndex={-1} for accessibility (so it can be focused programmatically).
  //    - Limit the max width and center the alert horizontally and vertically using inline styles (e.g., maxWidth: 480, margin: '1.6rem auto').
  // 2. Display the provided 'error' prop inside a <span> (for emphasis), and style the error text for prominence (e.g., fontWeight: 500).
  // 3. If the 'onRetry' prop is provided (i.e., user can retry the failed action):
  //    - Render a <button> labeled 'Try Again' beside or below the error message.
  //    - Style this retry button with minimal padding and outline-primary class for visual contrast.
  //    - Attach the 'onRetry' function to the button's onClick event handler.
  //    - Adjust the button's fontSize for visual consistency.
  // VARIABLES:
  // - error: The error message text to display to users.
  // - onRetry: (optional) Callback function to trigger when retrying the failed action.
}
