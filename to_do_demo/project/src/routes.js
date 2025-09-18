// src/routes.js
// Not strictly necessary for a single-route app, but provided per structure reference
import TodoListPage from './pages/TodoListPage';

// Simple export of route definitions for extensibility
export const routes = [
  {
    path: '/',
    element: <TodoListPage />
  }
];
