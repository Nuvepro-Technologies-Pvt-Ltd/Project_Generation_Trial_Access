// src/routes.js
// Not strictly necessary for a single-route app, but provided per structure reference
import TodoListPage from './pages/TodoListPage';

// Simple export of route definitions for extensibility
// TODO: Define an array called 'routes'. For each route you want your app to handle, add an object with the following properties:
//   - 'path': the URL path for the route (e.g., '/')
//   - 'element': the React component to render for that route (e.g., <TodoListPage />)
// Currently, only the root path '/' renders TodoListPage.
// If you want to add more routes, add additional objects to the array.
export const routes = [
  // Example route object:
  // {
  //   path: '/your-path',
  //   element: <YourComponent />
  // },
  {
    path: '/',
    element: <TodoListPage />
  }
];
