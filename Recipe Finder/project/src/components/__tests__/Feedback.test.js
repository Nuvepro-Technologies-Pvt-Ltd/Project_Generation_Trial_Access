import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LoadingIndicator, ErrorMessage } from '../Feedback';

// src/components/__tests__/Feedback.test.js
// Test suite for Feedback.js components (LoadingIndicator, ErrorMessage)
// Uses React Testing Library for rendering and interaction testing

describe('LoadingIndicator', () => {
  it('renders with default message', () => {
    // Arrange & Act
    render(<LoadingIndicator />);
    // Assert spinner and message are shown
    const spinner = screen.getByRole('status', { name: /loading/i });
    const message = screen.getByText('Loading...');
    expect(spinner).toBeInTheDocument();
    expect(message).toBeInTheDocument();
    // Style checks (accessibility / minimal design)
    expect(spinner).toHaveClass('spinner-border');
    expect(message).toHaveClass('mt-3', 'text-secondary');
    expect(message).toHaveStyle({ fontSize: '1.07rem' });
  });

  it('renders with a custom message', () => {
    const msg = 'Fetching records, please wait';
    render(<LoadingIndicator message={msg} />);
    // The custom message must be visible
    expect(screen.getByText(msg)).toBeInTheDocument();
  });
});

describe('ErrorMessage', () => {
  it('renders the error message and is focusable', () => {
    const errorMsg = 'A network error occurred';
    render(<ErrorMessage error={errorMsg} />);
    // Main error text
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveTextContent(errorMsg);
    // Should have proper classes and styling
    expect(alert).toHaveClass('alert', 'alert-danger', 'text-center');
    expect(alert).toHaveAttribute('tabIndex', '-1');
    expect(alert).toHaveStyle({ maxWidth: '480px' });
  });

  it('renders the retry button if onRetry is provided', () => {
    const onRetryMock = jest.fn();
    render(<ErrorMessage error="Error!" onRetry={onRetryMock} />);
    // Button should be present
    const retryBtn = screen.getByRole('button', { name: /try again/i });
    expect(retryBtn).toBeInTheDocument();
    // Accessible and styled
    expect(retryBtn).toHaveClass('btn', 'btn-outline-primary', 'mx-3', 'px-4', 'py-1');
    expect(retryBtn).toHaveStyle({ fontSize: '1em' });
    // Click triggers onRetry
    fireEvent.click(retryBtn);
    expect(onRetryMock).toHaveBeenCalledTimes(1);
  });

  it('does not render the retry button if onRetry is absent', () => {
    render(<ErrorMessage error="Not found" />);
    // Button must not appear
    const retryBtn = screen.queryByRole('button', { name: /try again/i });
    expect(retryBtn).not.toBeInTheDocument();
  });

  it('renders correctly when error message is empty (edge case)', () => {
    render(<ErrorMessage error="" />);
    // Alert exists, but no text
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    // Should not throw and must be empty
    expect(alert.textContent).toBe("");
  });

  it('renders safely if error is null or undefined (edge case)', () => {
    render(<ErrorMessage error={null} />);
    const alertNull = screen.getByRole('alert');
    expect(alertNull).toBeInTheDocument();
    expect(alertNull.textContent).toBe("");
    render(<ErrorMessage error={undefined} />);
    const alertUndef = screen.getByRole('alert');
    expect(alertUndef).toBeInTheDocument();
    expect(alertUndef.textContent).toBe("");
  });

  it('calls onRetry only once per click (error recovery test)', () => {
    // Ensures no double firing
    const onRetryMock = jest.fn();
    render(<ErrorMessage error="Error occurred" onRetry={onRetryMock} />);
    const retryBtn = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryBtn);
    expect(onRetryMock).toHaveBeenCalledTimes(1);
  });
});

// Note: No async or performance tests are required as components are purely presentational and render instantly.
// Security tests limited by stateless display logic -- all user-provided text is rendered as plain text, not HTML.
// All styling/accessibility requirements are checked via role, class, and tabIndex assertions.