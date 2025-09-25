// src/index.js
// Entry point for the React application
// Renders <App /> into the #root element in public/index.html

import React from 'react'; // Import React to use JSX
import ReactDOM from 'react-dom/client'; // Import the modern root API for React 18+
import App from './App'; // Main App component
import './index.css'; // Global CSS

// Use React 18+ root API for concurrent features support
const rootElement = document.getElementById('root'); // Get root DOM element
const root = ReactDOM.createRoot(rootElement); // Create React root

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
// The <React.StrictMode> helps highlight potential problems in development.
// All required imports provided, and entry root is set up for current React conventions.
