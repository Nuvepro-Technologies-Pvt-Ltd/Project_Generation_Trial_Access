import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter, Route } from 'react-router-dom';
import RoutesConfig from '../routes';
import DashboardPage from '../pages/DashboardPage';

// This test suite verifies routing logic for the RoutesConfig component
// - It uses react-router's MemoryRouter for isolated route context
// - DashboardPage is checked for route rendering
// - Redirects are validated for non-/dashboard paths

// Mock DashboardPage to observe rendering side effects
ojest.mock('../pages/DashboardPage', () => () => (<div data-testid="dashboard-page">Dashboard Content</div>));

describe('RoutesConfig', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('testRoute_DashboardPath_RendersDashboardPage', () => {
    // Arrange: Set the route path to /dashboard
    const { getByTestId, queryByTestId } = render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <RoutesConfig />
      </MemoryRouter>
    );

    // Assert: DashboardPage should be rendered and visible
    expect(getByTestId('dashboard-page')).toBeInTheDocument();
    // There should be only the dashboard page, no redirect happening
    expect(queryByTestId('dashboard-page')).not.toBeNull();
  });

  test('testRoute_UnknownPath_RedirectsToDashboard', () => {
    // Arrange: Simulate entering an unknown path
    const { getByTestId, container } = render(
      <MemoryRouter initialEntries={["/unknown"]}>
        <RoutesConfig />
      </MemoryRouter>
    );

    // Assert: The component redirects to /dashboard and DashboardPage is shown
    expect(getByTestId('dashboard-page')).toBeInTheDocument();
  });

  test('testRoute_EmptyPath_RedirectsToDashboard', () => {
    // Arrange: Simulate root path
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/"]}>
        <RoutesConfig />
      </MemoryRouter>
    );
    // Assert: Should redirect and render DashboardPage
    expect(getByTestId('dashboard-page')).toBeInTheDocument();
  });

  test('testRoute_QueryStringAndHash_RedirectsToDashboard', () => {
    // Arrange: Path with query and hash, not matching any route
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/anything?search=something#section"]}>
        <RoutesConfig />
      </MemoryRouter>
    );
    // Assert: Should redirect and show dashboard
    expect(getByTestId('dashboard-page')).toBeInTheDocument();
  });

  test('testRoute_DashboardPathWithParams_RedirectsToDashboard', () => {
    // Arrange: Path is partially matching, should still redirect
    const { getByTestId } = render(
      <MemoryRouter initialEntries={["/dashboard/extra"]}>
        <RoutesConfig />
      </MemoryRouter>
    );
    // Assert: Strict match only; should redirect to /dashboard
    expect(getByTestId('dashboard-page')).toBeInTheDocument();
  });

  // Edge case: Verify that all non-/dashboard routes redirect
  test.each([
    ['/profile'],
    ['/settings'],
    ['/dashboard/123'],
    ['/random/path'],
    ['']
  ])('testRoute_EdgeCases_%s_RedirectsToDashboard', (path) => {
    const { getByTestId } = render(
      <MemoryRouter initialEntries={[path]}>
        <RoutesConfig />
      </MemoryRouter>
    );
    expect(getByTestId('dashboard-page')).toBeInTheDocument();
  });
});