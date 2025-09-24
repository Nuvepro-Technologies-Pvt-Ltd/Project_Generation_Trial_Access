// routes.js
import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';

// This RoutesConfig component sets up the application's routing.
const RoutesConfig = () => (
  <Switch>
    {/* TODO: Configure routing for the application. */}
    {/* 1. Set up a Route for the '/dashboard' path that renders the DashboardPage component. Make sure this route only matches exactly '/dashboard'.
        Hint: Use Route's 'path', 'component', and 'exact' props. */}
        
    {/* 2. Add a Redirect at the end, so any routes not matched above will automatically redirect to '/dashboard'.
        Hint: Use the Redirect component's 'to' prop for this purpose. */}
  </Switch>
);

// TODO: Export the RoutesConfig component as the default module export.
// Hint: Use export default for RoutesConfig.
