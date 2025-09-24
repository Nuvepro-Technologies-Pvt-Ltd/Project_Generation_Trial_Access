// routes.js
import React from 'react';
import { Switch, Route, Redirect } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';

// Defines the routes for the app.
// Implement a component that handles routing in your application.
// 1. Use a <Switch> component to ensure that only a single route is rendered at a time.
// 2. Inside the <Switch>, define the specific route(s) for your app:
//    - Add a <Route> with the path set to '/dashboard', which renders the DashboardPage component.
//      - The 'exact' prop ensures this is only matched on the exact path.
// 3. Add a <Redirect> as a fallback to redirect any unmatched route to '/dashboard'.
// 4. Ensure this component is exported as default so it can be used throughout your app.
const RoutesConfig = () => (
  // Replace the contents below with the implementation described in the instructions above.
  // - Use the <Switch> component for routing exclusivity
  // - Add a <Route> to render DashboardPage at path '/dashboard'
  // - Add a <Redirect> as a catch-all for unmatched paths
);

export default RoutesConfig;