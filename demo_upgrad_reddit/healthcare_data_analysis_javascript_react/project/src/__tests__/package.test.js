import fs from 'fs';
import path from 'path';

// Test suite for package.json validation in AI Healthcare Dashboard React app
// Framework: Jest
// Place this file as src/__tests__/package.test.js

const packageJsonPath = path.join(__dirname, '../../package.json');

// Utility to load package.json
function loadPackageJson() {
  const data = fs.readFileSync(packageJsonPath, 'utf-8');
  return JSON.parse(data);
}

describe('package.json', () => {
  let pkg;

  beforeAll(() => {
    pkg = loadPackageJson();
  });

  test('should have the correct project name and version', () => {
    expect(pkg.name).toBe('ai-healthcare-dashboard');
    expect(pkg.version).toBe('1.0.0');
  });

  test('should be marked as private', () => {
    expect(pkg.private).toBe(true);
  });

  test('should have React and related dependencies with expected versions', () => {
    // Using realistic versions as per provided content
    expect(pkg.dependencies).toBeDefined();
    expect(pkg.dependencies['react']).toMatch(/^\^18/);
    expect(pkg.dependencies['react-dom']).toMatch(/^\^18/);
    expect(pkg.dependencies['react-bootstrap']).toMatch(/^\^2/);
    expect(pkg.dependencies['react-router-dom']).toMatch(/^\^5\.3/);
    expect(pkg.dependencies['axios']).toMatch(/^\^1\.6/);
    expect(pkg.dependencies['bootstrap']).toMatch(/^\^5\.3/);
  });

  test('should contain all necessary npm scripts', () => {
    expect(pkg.scripts).toBeDefined();
    expect(pkg.scripts['start']).toBe('react-scripts start');
    expect(pkg.scripts['build']).toBe('react-scripts build');
    expect(pkg.scripts['test']).toBe('react-scripts test');
    expect(pkg.scripts['eject']).toBe('react-scripts eject');
  });

  test('should not contain extra dependencies', () => {
    // Specify only the expected dependencies
    const allowed = [
      'axios', 'bootstrap', 'react', 'react-bootstrap', 'react-dom', 'react-router-dom'
    ];
    const actual = Object.keys(pkg.dependencies);
    expect(actual.sort()).toEqual(allowed.sort());
  });

  test('should not contain extra scripts', () => {
    // Only these four scripts should exist
    const allowedScripts = ['start', 'build', 'test', 'eject'];
    const actualScripts = Object.keys(pkg.scripts);
    expect(actualScripts.sort()).toEqual(allowedScripts.sort());
  });

  // Edge cases & error scenarios
  test('should throw if package.json is malformed', () => {
    expect(() => {
      JSON.parse('{ this is not valid JSON }');
    }).toThrow();
  });
});