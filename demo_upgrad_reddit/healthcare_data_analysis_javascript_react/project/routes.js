// routes.js
import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';

const RoutesConfig = () => (
  <Switch>
    {/* Only one route: /dashboard */}
    <Route path="/dashboard" component={DashboardPage} exact />
    {/* Redirect all other routes to dashboard */}
    <Redirect to="/dashboard" />
  </Switch>
);

export default RoutesConfig;
