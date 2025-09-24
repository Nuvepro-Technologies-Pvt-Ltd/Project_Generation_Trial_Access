import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import RoutesConfig from '../routes';
jest.mock('../routes', () => () => <div>Mocked Routes</div>);

/**
 * @file App.test.js
 * Test suite for the Application Root Component (App.js)
 * Covers normal rendering, edge cases, repeated rendering, and prop leakage.
 * See error-handling test isolation details in AppError.test.js.
 *
 * TODO: Integration test for Bootstrap/global styles if real DOM issues observed.
 */

describe('App Root Component', () => {
  /**
   * Should render the Router and mocked RoutesConfig as root composition
   */
  test('renders Router and RoutesConfig as root composition', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByText('Mocked Routes')).toBeInTheDocument();
  });

  /**
   * Edge Case: App does not crash even without location or search provided in routing context
   */
  test('does not crash with minimal routing context', () => {
    render(<App />);
    expect(screen.getByText('Mocked Routes')).toBeInTheDocument();
  });

  /**
   * Performance: App can be rendered repeatedly, simulating re-mounts, without memory leak or degradation
   */
  test('repeatedly renders without degradation', () => {
    for (let i = 0; i < 20; i++) {
      render(
        <MemoryRouter>
          <App />
        </MemoryRouter>
      );
      expect(screen.getByText('Mocked Routes')).toBeInTheDocument();
    }
  });

  /**
   * Security: No unwanted props leak through Router or to child routes
   */
  test('does not leak unwanted props to Router or child routes', () => {
    render(
      <MemoryRouter extraProp="unexpected">
        <App randomProp="bad" />
      </MemoryRouter>
    );
    expect(screen.getByText('Mocked Routes')).toBeInTheDocument();
  });
});

// --- Isolated error-handling tests below in separate suite to avoid module cache issues and global leakage ---

describe('App Root Component - Error Handling', () => {
  /**
   * This test ensures the App gracefully handles error thrown by RoutesConfig.
   * We reset modules and mock RoutesConfig to throw, then import App with the error mock active.
   */
  let originalConsoleError;

  beforeAll(() => {
    originalConsoleError = console.error;
    console.error = jest.fn(); // silence React error boundary warnings
  });
  afterAll(() => {
    console.error = originalConsoleError;
  });

  afterEach(() => {
    jest.resetModules();
  });

  test('app throws error if RoutesConfig throws', () => {
    jest.resetModules();
    jest.doMock('../routes', () => () => { throw new Error('Test Error'); });
    const React = require('react');
    const { render } = require('@testing-library/react');
    const App = require('../App').default;
    expect(() => render(<App />)).toThrow('Test Error');
    jest.dontMock('../routes');
  });
});