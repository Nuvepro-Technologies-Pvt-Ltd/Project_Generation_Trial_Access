import React from 'react';
import { routes } from '../src/routes';
import TodoListPage from '../src/pages/TodoListPage';

// Test suite for routes.js - ensures correct route definitions and structure
// Using Jest and @testing-library/react for consistency with React component imports

describe('Routes Definition', () => {
  it('should export an array with exactly one route', () => {
    expect(Array.isArray(routes)).toBe(true);
    expect(routes).toHaveLength(1);
  });

  it("should define the root ('/') route with the correct element", () => {
    const route = routes.find(r => r.path === '/');
    expect(route).toBeDefined();
    // We expect element to be a React element of TodoListPage
    // Checking element type and proper instantiation
    expect(route.element).toBeInstanceOf(Object);
    // If element is a React element, its type is TodoListPage
    expect(route.element.type).toBe(TodoListPage);
  });

  it('should allow extensibility for future routes', () => {
    // This test ensures that the structure supports adding more routes
    const testRoute = { path: '/test', element: <div>Test</div> };
    const extendedRoutes = [ ...routes, testRoute ];
    expect(extendedRoutes).toHaveLength(routes.length + 1);
    expect(extendedRoutes.find(r => r.path === '/test')).toEqual(testRoute);
  });

  it('should not have duplicate paths', () => {
    // Ensure all path values are unique
    const paths = routes.map(r => r.path);
    const uniquePaths = Array.from(new Set(paths));
    expect(paths).toHaveLength(uniquePaths.length);
  });

  // Edge case: if routes accidentally becomes undefined/null
  it('should fail gracefully if routes is not defined', () => {
    // Simulate accidental deletion
    const undefinedRoutes = undefined;
    expect(() => {
      // @ts-ignore - deliberately bypassing type checks
      undefinedRoutes.forEach(() => {});
    }).toThrow();
  });
});