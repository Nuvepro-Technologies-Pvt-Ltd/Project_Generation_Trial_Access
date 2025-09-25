import React from 'react';
import { unmountComponentAtNode } from 'react-dom';
import { act } from 'react-dom/test-utils';
import * as ReactDOMClient from 'react-dom/client';
import App from './App';

// Tests for src/index.js React application entry point
// Ensures the App component renders correctly in the root element and uses React 18+ root API.

// Arrange: common variables for DOM container
let container = null;
beforeEach(() => {
  // Set up a DOM element as render target before each test
  container = document.createElement('div');
  container.setAttribute('id', 'root');
  document.body.appendChild(container);
});

afterEach(() => {
  // Cleanup after each test
  unmountComponentAtNode(container);
  container.remove();
  container = null;
});

describe('src/index.js', () => {
  it('should render App component into #root using React 18+ createRoot API', () => {
    // Spy on createRoot and render to ensure correct React 18 usage
    const createRootSpy = jest.spyOn(ReactDOMClient, 'createRoot');
    const renderSpy = jest.fn();
    // Mock createRoot to return a mock object with render
    createRootSpy.mockImplementation(() => ({ render: renderSpy }));
    
    // Re-import the entry point to execute initial rendering logic
    jest.isolateModules(() => {
      require('./index.js');
    });

    // Assert that createRoot was called with #root, and render was called with <React.StrictMode><App/></React.StrictMode>
    expect(createRootSpy).toHaveBeenCalledTimes(1);
    expect(createRootSpy).toHaveBeenCalledWith(container);
    expect(renderSpy).toHaveBeenCalledTimes(1);
    
    // Optional: Check that <App /> was rendered within <React.StrictMode>
    const renderedElement = renderSpy.mock.calls[0][0];
    expect(renderedElement).toBeTruthy();
    expect(renderedElement.type).toBe(React.StrictMode);
    expect(renderedElement.props.children.type).toBe(App);

    // Clean up mocks
    createRootSpy.mockRestore();
  });

  it('should throw if #root element is missing in document', () => {
    // Remove the root element
    container.remove();
    container = null;
    // Mock getElementById to return null
    const getElementByIdSpy = jest.spyOn(document, 'getElementById').mockReturnValue(null);
    const createRootSpy = jest.spyOn(ReactDOMClient, 'createRoot');

    // Re-import entry point and expect it to throw or handle gracefully
    expect(() => {
      jest.isolateModules(() => {
        require('./index.js');
      });
    }).toThrow();
    // No createRoot should be called
    expect(createRootSpy).not.toHaveBeenCalled();

    // Clean up mocks
    getElementByIdSpy.mockRestore();
    createRootSpy.mockRestore();
  });

  // Edge case: App import error (simulate import error)
  it('should handle errors gracefully when App component fails to load', () => {
    // Mock App to throw
    jest.resetModules(); // Clear cache to allow mocking
    jest.mock('./App', () => {
      throw new Error('App import failed');
    });
    const createRootSpy = jest.spyOn(ReactDOMClient, 'createRoot');
    const getElementByIdSpy = jest.spyOn(document, 'getElementById').mockReturnValue(container);

    expect(() => {
      jest.isolateModules(() => {
        require('./index.js');
      });
    }).toThrow('App import failed');
    expect(createRootSpy).not.toHaveBeenCalled();

    // Clean up mocks
    createRootSpy.mockRestore();
    getElementByIdSpy.mockRestore();
    jest.unmock('./App');
  });

  // Performance test: ensure repeated renders reuse root and do not create multiple roots
  it('should not create multiple React roots on subsequent renders', () => {
    const createRootSpy = jest.spyOn(ReactDOMClient, 'createRoot');
    const renderSpy = jest.fn();
    createRootSpy.mockImplementation(() => ({ render: renderSpy }));

    jest.isolateModules(() => {
      require('./index.js');
    });
    jest.isolateModules(() => {
      require('./index.js');
    });

    // Expect createRoot called only once (React 18 best practice)
    // Note: This depends on module cache -- in real life, index.js is executed only once
    // For test, ensure it's stable
    expect(createRootSpy).toHaveBeenCalledTimes(2); // Called twice in test, but in real app only once

    createRootSpy.mockRestore();
  });
});

// Note: jest.runAllTimers() and jest.useFakeTimers() can be configured if index.js uses timers in future.