import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SyntheticDataControls from '../SyntheticDataControls';

// Unit & integration tests for SyntheticDataControls React component
// Test coverage: Rendering, validation, user interaction, loading/error states, event callbacks

describe('SyntheticDataControls', () => {
  const setup = (overrides = {}) => {
    const onGenerate = jest.fn();
    const utils = render(
      <SyntheticDataControls
        onGenerate={onGenerate}
        loading={overrides.loading || false}
        error={overrides.error || null}
      />
    );
    return { ...utils, onGenerate };
  };

  test('renders form fields with defaults', () => {
    setup();
    expect(screen.getByLabelText(/Number of Records/i)).toHaveValue(10);
    expect(screen.getByLabelText(/Data Type/i)).toHaveValue('EHR');
    expect(screen.getByLabelText(/Privacy Level/i)).toHaveValue('high');
    expect(screen.getByRole('button', { name: /generate data/i })).toBeEnabled();
  });

  test('allows user to change record count', () => {
    setup();
    const input = screen.getByLabelText(/Number of Records/i);
    fireEvent.change(input, { target: { value: '23' } });
    expect(input).toHaveValue(23);
  });

  test('disables form fields and button when loading', () => {
    setup({ loading: true });
    expect(screen.getByLabelText(/Number of Records/i)).toBeDisabled();
    expect(screen.getByLabelText(/Data Type/i)).toBeDisabled();
    expect(screen.getByLabelText(/Privacy Level/i)).toBeDisabled();
    expect(screen.getByRole('button')).toBeDisabled();
    // Spinner rendered instead of text
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('shows error alert when error prop is set', () => {
    const errorMsg = 'Failed to generate data!';
    setup({ error: errorMsg });
    expect(screen.getByRole('alert')).toHaveTextContent(errorMsg);
  });

  test('changes data type and privacy level', () => {
    setup();
    fireEvent.change(screen.getByLabelText(/Data Type/i), { target: { value: 'CLAIMS' } });
    fireEvent.change(screen.getByLabelText(/Privacy Level/i), { target: { value: 'medium' } });
    expect(screen.getByLabelText(/Data Type/i)).toHaveValue('CLAIMS');
    expect(screen.getByLabelText(/Privacy Level/i)).toHaveValue('medium');
  });

  test('submits valid form and calls onGenerate with correct parameters', () => {
    const { onGenerate } = setup();
    fireEvent.change(screen.getByLabelText(/Number of Records/i), { target: { value: '50' } });
    fireEvent.change(screen.getByLabelText(/Data Type/i), { target: { value: 'DEMOGRAPHICS' } });
    fireEvent.change(screen.getByLabelText(/Privacy Level/i), { target: { value: 'low' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    expect(onGenerate).toHaveBeenCalledWith({
      record_count: 50,
      data_type: 'DEMOGRAPHICS',
      privacy_level: 'low'
    });
  });

  test('does not call onGenerate for invalid record count (lower bound)', async () => {
    const { onGenerate } = setup();
    fireEvent.change(screen.getByLabelText(/Number of Records/i), { target: { value: '0' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    await waitFor(() => expect(onGenerate).not.toHaveBeenCalled());
    expect(screen.getByText(/Enter 1-1000 records/i)).toBeInTheDocument();
  });

  test('does not call onGenerate for invalid record count (upper bound)', async () => {
    const { onGenerate } = setup();
    fireEvent.change(screen.getByLabelText(/Number of Records/i), { target: { value: '1200' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    await waitFor(() => expect(onGenerate).not.toHaveBeenCalled());
    expect(screen.getByText(/Enter 1-1000 records/i)).toBeInTheDocument();
  });

  test('does not submit form if data type is not selected', async () => {
    const { onGenerate } = setup();
    // Remove selection
    fireEvent.change(screen.getByLabelText(/Data Type/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    await waitFor(() => expect(onGenerate).not.toHaveBeenCalled());
    expect(screen.getByText(/Please select a data type/i)).toBeInTheDocument();
  });

  test('does not submit form if privacy level is not selected', async () => {
    const { onGenerate } = setup();
    fireEvent.change(screen.getByLabelText(/Privacy Level/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /generate data/i }));
    await waitFor(() => expect(onGenerate).not.toHaveBeenCalled());
    expect(screen.getByText(/Please select privacy/i)).toBeInTheDocument();
  });

  test('record count input defaults to minimum when input is cleared', () => {
    setup();
    const input = screen.getByLabelText(/Number of Records/i);
    fireEvent.change(input, { target: { value: '' } });
    expect(input).toHaveValue(1);
  });

  // Edge: Large valid input
  test('accepts upper bound value (1000) for record count', () => {
    setup();
    const input = screen.getByLabelText(/Number of Records/i);
    fireEvent.change(input, { target: { value: '1000' } });
    expect(input).toHaveValue(1000);
  });

  // Accessibility: Ensure all fields are labelled
  test('all form inputs have accessible labels', () => {
    setup();
    expect(screen.getByLabelText(/Number of Records/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Data Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Privacy Level/i)).toBeInTheDocument();
  });
});