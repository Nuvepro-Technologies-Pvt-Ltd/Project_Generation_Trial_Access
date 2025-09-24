// index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

// App entry point: renders root React component into DOM
ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);