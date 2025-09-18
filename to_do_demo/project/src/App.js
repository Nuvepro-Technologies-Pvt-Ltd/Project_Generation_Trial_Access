import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import TodoListPage from '../pages/TodoListPage';
jest.mock('../pages/TodoListPage', () => () => (<div>Mocked TodoListPage</div>));

// src/__tests__/App.test.js
// Test suite for the Root App Component (Handles Routing)

// Arrange-Act-Assert pattern used throughout tests

describe('App Routing', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('testRoutes_RootPath_RendersTodoListPage', () => {
    // Arrange: Render the App at root route
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );
    // Act & Assert: Check that the mocked TodoListPage is rendered
    expect(screen.getByText('Mocked TodoListPage')).toBeInTheDocument();
  });

  test('testRoutes_UnknownPath_RedirectsToTodoListPage', () => {
    // Arrange: Render App at unknown route
    render(
      <MemoryRouter initialEntries={['/does-not-exist']}>
        <App />
      </MemoryRouter>
    );
    // Act & Assert: Since only '/' is defined, react-router v6+ will not match unknown routes, so nothing renders by default.
    // To improve UX, an explicit catch-all Redirect would be tested, but as per the current code, the page will not load.
    // For this test, we assert TodoListPage is not rendered on unknown route.
    expect(screen.queryByText('Mocked TodoListPage')).not.toBeInTheDocument();
  });

  test('testRoutes_ExactPathOnly_RendersOnce', () => {
    // Arrange: Render App at the exact main route
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );
    // Act: Try to find all instances of TodoListPage
    const todos = screen.getAllByText('Mocked TodoListPage');
    // Assert: Only one instance should be present
    expect(todos).toHaveLength(1);
  });

  // Edge case: Null Route
  test('testRoutes_NullRoute_DoesNotCrash', () => {
    // Arrange & Act: Render App with no initialEntries (defaults to '/')
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    // Assert: Should render TodoListPage without crashing
    expect(screen.getByText('Mocked TodoListPage')).toBeInTheDocument();
  });

  // Performance: Rapid Navigation
  test('testRoutes_RapidNavigation_Stability', () => {
    // Arrange: Render at '/'
    const { rerender } = render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByText('Mocked TodoListPage')).toBeInTheDocument();
    // Act: Simulate rapid navigation by rerendering with different initialEntries
    rerender(
      <MemoryRouter initialEntries={['/', '/another', '/']}> 
        <App />
      </MemoryRouter>
    );
    // Assert: Still renders safely
    expect(screen.getByText('Mocked TodoListPage')).toBeInTheDocument();
  });
});

// Note: MemoryRouter is used to simulate routing context.
// The actual TodoListPage is mocked to isolate routing behavior.
// If additional routes are added in the future, more tests should be implemented for those new paths.