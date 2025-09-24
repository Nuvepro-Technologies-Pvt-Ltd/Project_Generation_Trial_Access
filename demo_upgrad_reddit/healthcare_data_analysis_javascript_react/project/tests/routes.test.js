import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RoutesConfig from '../src/routes';
import DashboardPage from '../src/pages/DashboardPage';
jest.mock('../src/pages/DashboardPage', () => () => (<div>MockDashboardPage</div>));

// Test suite for App Routing (routes.js)
describe('RoutesConfig', () => {
  // Helper function to render RoutesConfig with an initial route
  function renderWithRouter(initialEntries = ['/dashboard']) {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <RoutesConfig />
      </MemoryRouter>
    );
  }

  test('testDashboardRoute_RendersDashboardPage_Success', () => {
    // Arrange & Act: Navigate directly to /dashboard
    renderWithRouter(['/dashboard']);

    // Assert: The DashboardPage component should render
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
  });

  test('testOtherRoute_RedirectsToDashboard_Success', () => {
    // Arrange & Act: Navigate to an undefined route
    renderWithRouter(['/unknown']);

    // Assert: Should redirect and still render DashboardPage
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
  });

  test('testEmptyRoute_RedirectsToDashboard_Success', () => {
    // Arrange & Act: Navigate to root path /
    renderWithRouter(['/']);

    // Assert: Should redirect and render DashboardPage
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
  });

  test('testExactMatching_OnlyDashboardPathAllowed_Success', () => {
    // Arrange & Act: Navigate to /dashboard/settings (should redirect)
    renderWithRouter(['/dashboard/settings']);

    // Assert: Should still redirect to /dashboard and show DashboardPage
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
  });

  // Negative/Edge: Could test param/fragment being ignored (advanced)
  test('testDashboardRouteWithQueryParams_RendersDashboardPage_Success', () => {
    // Arrange & Act: Navigate to /dashboard?user=test
    renderWithRouter(['/dashboard?user=test']);

    // Assert: Should still render DashboardPage
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
  });

  // Edge: Component should not break or throw on invalid input
  test('testInvalidRouteType_DoesNotThrow_ErrorHandled', () => {
    // Arrange, Act & Assert: Should not throw error on invalid path
    expect(() => renderWithRouter([null])).not.toThrow();
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
  });

  // Performance: Rendering many times should not leak memory or crash
  test('testMultipleRenders_Performance_Stability', () => {
    for(let i = 0; i < 20; i++) {
      renderWithRouter(['/dashboard']);
      expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
    }
  });

  // Security: Ensure no XSS via route rendering (if using user input in actual implementation)
  test('testXssRoute_Security_NoScriptInjected', () => {
    renderWithRouter(['/dashboard/<script>alert(1)</script>']);
    // Should not inject raw HTML or script tags
    expect(screen.getByText('MockDashboardPage')).toBeInTheDocument();
    expect(screen.queryByText(/<script>/i)).not.toBeInTheDocument();
  });
});

// Note: DashboardPage is mocked for isolation/unit testing. If integration with real component is desired, remove the jest.mock line and ensure the real DashboardPage renders a known testable element.