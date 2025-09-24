// App.js
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import RoutesConfig from './routes';
import 'bootstrap/dist/css/bootstrap.min.css';

// Root app component wraps routes with Bootstrap styles
function App() {
  return (
    <Router>
      <RoutesConfig />
    </Router>
  );
}

export default App;