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

// TODO: Render the main App component inside <React.StrictMode> into the DOM using the React root API.
// 1. Use 'root.render(...)' to render your component tree.
// 2. Inside the render method, wrap your <App /> component with <React.StrictMode> for highlighting potential problems during development.
// Example:
// root.render(
//   <React.StrictMode>
//     <App />
//   </React.StrictMode>
// );
// Make sure that you are rendering into the DOM element with id 'root' as created above.
// Additionally, confirm all imports are correctly referenced.
