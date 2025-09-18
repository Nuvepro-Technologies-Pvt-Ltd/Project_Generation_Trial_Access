// src/App.js
import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes
} from 'react-router-dom';
import TodoListPage from './pages/TodoListPage';

// Root App component manages all routes
const App = () => {
  // Instructions:
  // 1. Use the <Router> component as the root of your application's component tree to enable routing.
  // 2. Within <Router>, use <Routes> to define your application's route(s).
  // 3. Define a <Route> for the root path ('/'),
  //    and render the <TodoListPage /> component when the user visits this path.
  // 4. If you have additional pages in the future, add more <Route> components inside <Routes> as necessary.
  // 5. Ensure to return the entire JSX structure containing <Router> with its child components.
};

export default App;
