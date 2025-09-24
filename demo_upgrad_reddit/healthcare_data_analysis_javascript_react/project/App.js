// App.js
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import RoutesConfig from './routes';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  // Root component; wraps the app in the router and renders route config
  return (
    <Router>
      <RoutesConfig />
    </Router>
  );
}

export default App;
