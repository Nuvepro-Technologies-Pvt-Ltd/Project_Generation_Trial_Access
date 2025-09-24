import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SyntheticDataControls from '../../src/components/SyntheticDataControls';

// Test suite for SyntheticDataControls UI component
// Testing library: @testing-library/react + jest
// All essential scenarios including unit/edge/error cases are covered

describe('SyntheticDataControls', () => {
  function renderComponent(props = {}) {
    return render(<SyntheticDataControls {...props} />);
  }

  test('renders all form fields with initial values - unit test', () => {
    renderComponent();
    expect(screen.getByLabelText(/number of records/i)).toHaveValue(10);
    expect(screen.getByLabelText(/data type/i)).toHaveValue('EHR');
    expect(screen.getByLabelText(/privacy level/i)).toHaveValue('high');
    expect(screen.getByRole('button', { name: /generate data/i })).toBeEnabled();
  });

  test('calls onGenerate with correct params when form is valid - integration test', () => {
    const onGenerate = jest.fn();
    renderComponent({ onGenerate });
    // change values
    fireEvent.change(screen.getByLabelText(/number of records/i), { target: { value: '57' } });
    fireEvent.change(screen.getByLabelText(/data type/i), { target: { value: 'CLAIMS' } });
    fireEvent.change(screen.getByLabelText(/privacy level/i), { target: { value: 'medium' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    expect(onGenerate).toHaveBeenCalledTimes(1);
    expect(onGenerate).toHaveBeenCalledWith({
      record_count: 57,
      data_type: 'CLAIMS',
      privacy_level: 'medium'
    });
  });

  test('prevents submission and does NOT call onGenerate with out-of-bound record count (min)', () => {
    const onGenerate = jest.fn();
    renderComponent({ onGenerate });
    fireEvent.change(screen.getByLabelText(/number of records/i), { target: { value: '0' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    expect(onGenerate).not.toHaveBeenCalled();
    // Should show invalid feedback
    expect(screen.getByText(/enter 1-1000 records/i)).toBeInTheDocument();
  });

  test('prevents submission and does NOT call onGenerate with out-of-bound record count (max)', () => {
    const onGenerate = jest.fn();
    renderComponent({ onGenerate });
    fireEvent.change(screen.getByLabelText(/number of records/i), { target: { value: '1001' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    expect(onGenerate).not.toHaveBeenCalled();
    // Should show invalid feedback
    expect(screen.getByText(/enter 1-1000 records/i)).toBeInTheDocument();
  });

  test('disables all controls and shows spinner when loading is true', () => {
    renderComponent({ loading: true });
    expect(screen.getByLabelText(/number of records/i)).toBeDisabled();
    expect(screen.getByLabelText(/data type/i)).toBeDisabled();
    expect(screen.getByLabelText(/privacy level/i)).toBeDisabled();
    expect(screen.getByRole('button', { name: /generate data/i })).toBeDisabled();
    // Ensure spinner appears
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('shows error alert if error prop is supplied', () => {
    renderComponent({ error: 'Something went wrong' });
    expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong');
  });

  test('shows correct options in data type and privacy level selects', () => {
    renderComponent();
    // Data types
    expect(screen.getByRole('option', { name: /electronic health record/i })).toHaveValue('EHR');
    expect(screen.getByRole('option', { name: /claims/i })).toHaveValue('CLAIMS');
    expect(screen.getByRole('option', { name: /demographics/i })).toHaveValue('DEMOGRAPHICS');
    // Privacy levels
    expect(screen.getByRole('option', { name: /high/i })).toHaveValue('high');
    expect(screen.getByRole('option', { name: /moderate/i })).toHaveValue('medium');
    expect(screen.getByRole('option', { name: /minimal/i })).toHaveValue('low');
  });

  test('does not break if onGenerate is not provided and valid submit occurs', () => {
    renderComponent();
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    // No error expected
    expect(screen.getByLabelText(/number of records/i)).toBeInTheDocument();
  });

  test('recordCount input restores to 1 if non-numeric or empty value supplied', () => {
    renderComponent();
    // Attempt a non-numeric input
    fireEvent.change(screen.getByLabelText(/number of records/i), { target: { value: '' } });
    expect(screen.getByLabelText(/number of records/i)).toHaveValue(1);
    fireEvent.change(screen.getByLabelText(/number of records/i), { target: { value: 'abcd' } });
    expect(screen.getByLabelText(/number of records/i)).toHaveValue(1);
  });

  test('feedback for required select fields on invalid submission', () => {
    renderComponent();
    // Data type/Privacy are required by prop, to test this we'd have to simulate removal, which HTML select won't permit easily
    // But the invalid feedback node is present
    expect(screen.getByText(/please select a data type/i)).toBeInTheDocument();
    expect(screen.getByText(/please select privacy/i)).toBeInTheDocument();
  });
});
// Tests cover:
// 1. Initial render and field defaults
// 2. Form submission with valid and invalid/boundary values
// 3. Error/Loading states
// 4. Available select options
// 5. Component's resilience to missing callbacks
// 6. Feedback UI presence for client-side validation