import React from 'react';
import ReactDOM from 'react-dom';
import App from '../src/App';
import '@testing-library/jest-dom/extend-expect';
import { render, unmountComponentAtNode } from 'react-dom';
import { act } from 'react-dom/test-utils';

// Test suite for 'src/index.js' (App entry point)
describe('index.js App Entry Point', () => {
  let container = null;

  beforeEach(() => {
    // Set up a DOM element as a render target
    container = document.createElement('div');
    container.setAttribute('id', 'root');
    document.body.appendChild(container);
  });

  afterEach(() => {
    // Clean up after each test
    unmountComponentAtNode(container);
    container.remove();
    container = null;
    // Remove any possible duplicate root
    const rootNode = document.getElementById('root');
    if (rootNode) rootNode.remove();
  });

  it('renders App component into #root with React.StrictMode', () => {
    // Arrange: Mock document.getElementById to ensure correct element is used
    const getElementByIdSpy = jest.spyOn(document, 'getElementById');

    // Act: Render the root component as in index.js
    act(() => {
      ReactDOM.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>,
        document.getElementById('root')
      );
    });

    // Assert: Check that App has rendered into the container
    expect(getElementByIdSpy).toHaveBeenCalledWith('root');
    // Since App component is application-defined, minimal check: container has content
    expect(container.innerHTML.length).toBeGreaterThan(0);
    getElementByIdSpy.mockRestore();
  });

  it('throws if #root element is missing from DOM', () => {
    // Remove the root element to simulate missing root
    container.remove();
    container = null;

    // Act & Assert:
    expect(() => {
      ReactDOM.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>,
        document.getElementById('root') // Will be null
      );
    }).toThrow();
  });

  it('does not crash if App component is empty', () => {
    // Arrange: Mock an empty App for this test
    jest.mock('../src/App', () => () => null);
    const EmptyApp = require('../src/App').default || require('../src/App');
    
    // Act: Should not throw
    expect(() => {
      act(() => {
        ReactDOM.render(
          <React.StrictMode>
            <EmptyApp />
          </React.StrictMode>,
          document.getElementById('root')
        );
      });
    }).not.toThrow();
    
    // Clean up manual mock
    jest.resetModules();
  });

  it('unmounts App component cleanly', () => {
    // Arrange: Render as usual
    act(() => {
      ReactDOM.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>,
        document.getElementById('root')
      );
    });
    // Act: Unmount
    expect(() => {
      unmountComponentAtNode(document.getElementById('root'));
    }).not.toThrow();
    // Assert: The root should be empty
    expect(document.getElementById('root').innerHTML).toBe('');
  });

  it('renders the same output on multiple calls (idempotence test)', () => {
    // Arrange: Render twice
    let firstRender, secondRender;
    act(() => {
      ReactDOM.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>,
        document.getElementById('root')
      );
      firstRender = container.innerHTML;
      ReactDOM.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>,
        document.getElementById('root')
      );
      secondRender = container.innerHTML;
    });
    // Assert: Both outputs must match
    expect(secondRender).toEqual(firstRender);
  });

  // Edge case: simulate error thrown by rendering
  it('catches errors thrown by App component during render', () => {
    // Arrange: App that throws on render
    const ErrorApp = () => { throw new Error('Test render error'); };
    expect(() => {
      act(() => {
        ReactDOM.render(
          <React.StrictMode>
            <ErrorApp />
          </React.StrictMode>,
          document.getElementById('root')
        );
      });
    }).toThrow('Test render error');
  });
});

// Note: Performance and security tests are limited for entrypoint rendering in browser-based React apps. Most are handled in integration or E2E tests.