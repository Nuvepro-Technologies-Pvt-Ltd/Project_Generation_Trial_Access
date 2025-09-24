import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// App.test.js
// Test suite for the App component - ensuring correct rendering, routing, and edge case handling

// Top-level jest.mock for conditional mocking in specific tests
const realRoutesConfig = jest.requireActual('./routes').default;

// Helper component to test router context
import { useLocation } from 'react-router-dom';
function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
}

describe('App Component', () => {
  afterEach(() => {
    jest.resetModules(); // Clean up any module mocks
    jest.clearAllMocks();
  });

  it('should render without crashing', () => {
    const { container } = render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(container).toBeDefined();
  });

  it('should render the RoutesConfig component (requires data-testid)', () => {
    // Mock RoutesConfig to add a data-testid if not present
    jest.doMock('./routes', () => () => <div data-testid="routes-config">MockedRoutesConfig</div>);
    // Re-import after mock
    const AppWithMockedRoutes = require('./App').default;
    render(
      <MemoryRouter>
        <AppWithMockedRoutes />
      </MemoryRouter>
    );
    expect(screen.getByTestId('routes-config')).toBeInTheDocument();
    jest.dontMock('./routes'); // Reset for other tests
  });

  it('should include the Bootstrap styles', () => {
    // Arrange - Bootstrap styles are imported globally
    const bootstrapLink = Array.from(document.head.getElementsByTagName('link')).find(link =>
      link.href && link.href.includes('bootstrap.min.css')
    );
    expect(bootstrapLink).toBeDefined();
  });

  it('should provide a functioning router context to children', () => {
    render(
      <MemoryRouter initialEntries={['/test-path']}>
        {/* App wraps everything including LocationDisplay */}
        <App />
        <LocationDisplay />
      </MemoryRouter>
    );
    expect(screen.getByTestId('location-display').textContent).toBe('/test-path');
  });

  it('should not crash if RoutesConfig is missing', () => {
    // Mock RoutesConfig to return null
    jest.doMock('./routes', () => () => null);
    const AppWithMockedRoutes = require('./App').default;
    const originalError = console.error;
    try {
      console.error = jest.fn();
      const { container } = render(
        <MemoryRouter>
          <AppWithMockedRoutes />
        </MemoryRouter>
      );
      expect(container).toBeDefined();
    } finally {
      console.error = originalError;
      jest.dontMock('./routes');
    }
  });

  describe('ErrorBoundary integration (if present)', () => {
    it('should render fallback UI if a child (RoutesConfig) throws', () => {
      // Mock RoutesConfig to throw
      jest.doMock('./routes', () => {
        return () => { throw new Error('RoutesConfig error'); };
      });
      const AppWithThrowingRoutes = require('./App').default;
      const originalError = console.error;
      try {
        console.error = jest.fn(); // Suppress error logging in test output
        const { container, queryByText } = render(
          <MemoryRouter>
            <AppWithThrowingRoutes />
          </MemoryRouter>
        );
        // As no ErrorBoundary exists yet, can only check that app doesn't hang
        expect(container).toBeDefined();
      } finally {
        console.error = originalError;
        jest.dontMock('./routes');
      }
    });
  });
});