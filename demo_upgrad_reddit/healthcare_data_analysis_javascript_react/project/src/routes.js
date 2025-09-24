// routes.js
import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';

// Defines the routes for the app. Only one route: /dashboard
const RoutesConfig = () => (
  <Switch>
    <Route path="/dashboard" component={DashboardPage} exact />
    {/* Redirect all other paths to /dashboard for simplicity */}
    <Redirect to="/dashboard" />
  </Switch>
);

export default RoutesConfig;