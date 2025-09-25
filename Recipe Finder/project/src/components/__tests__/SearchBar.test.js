import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SearchBar from '../SearchBar';

// Comprehensive tests for SearchBar component using React Testing Library (Jest)
// Covers unit, integration, accessibility, edge, and error scenarios

describe('SearchBar Component', () => {
  const setup = (props = {}) => {
    const defaultProps = {
      value: '',
      onChange: jest.fn(),
      onSubmit: jest.fn(),
      disabled: false,
    };
    const utils = render(<SearchBar {...defaultProps} {...props} />);
    const input = screen.getByLabelText(/ingredients/i);
    const button = screen.getByRole('button', { name: /search/i });
    return { input, button, ...utils, ...defaultProps, ...props };
  };

  test('renders input and button with correct attributes', () => {
    const { input, button } = setup();
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('placeholder', 'Enter ingredients, separated by commas');
    expect(input).toHaveClass('form-control');
    expect(input).toHaveClass('form-control-lg');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('btn-primary');
    expect(button).toHaveClass('btn-lg');
    expect(button).toHaveTextContent('Search');
  });

  test('calls onChange with the correct value on input change', () => {
    const onChange = jest.fn();
    const { input } = setup({ onChange });
    fireEvent.change(input, { target: { value: 'onion, garlic' } });
    expect(onChange).toHaveBeenCalledWith('onion, garlic');
  });

  test('submit button is disabled when input is empty or whitespace', () => {
    const { button } = setup({ value: '   ' });
    expect(button).toBeDisabled();
  });

  test('submit button is enabled when input is non-empty and not disabled', () => {
    const { button } = setup({ value: 'carrot' });
    expect(button).toBeEnabled();
  });

  test('does not call onSubmit if input is empty', () => {
    const onSubmit = jest.fn();
    const { button } = setup({ value: '', onSubmit });
    fireEvent.click(button);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('does not call onSubmit if component is disabled', () => {
    const onSubmit = jest.fn();
    const { button } = setup({ value: 'apple', disabled: true, onSubmit });
    fireEvent.click(button);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('calls onSubmit when submitted with valid value and not disabled', () => {
    const onSubmit = jest.fn();
    const { button } = setup({ value: 'banana', onSubmit });
    fireEvent.click(button);
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  test('submits form using Enter key when valid', () => {
    const onSubmit = jest.fn();
    const { input } = setup({ value: 'kiwi', onSubmit });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });
    fireEvent.submit(input.form);
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  test('input has autoFocus and is focusable', () => {
    const { input } = setup();
    expect(input).toHaveFocus();
  });

  test('disables input and button if `disabled` prop is true', () => {
    const { input, button } = setup({ disabled: true, value: 'xyz' });
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  test('form has correct aria-label for accessibility', () => {
    setup();
    // Use aria-label to get the form
    const form = screen.getByLabelText('Ingredient Search');
    expect(form).toBeInTheDocument();
    expect(form.tagName.toLowerCase()).toBe('form');
  });

  test('input has visually-hidden label for accessibility', () => {
    setup();
    // Locate the label by text
    const label = screen.getByText('Ingredients');
    expect(label).toBeInTheDocument();
    expect(label.tagName.toLowerCase()).toBe('label');
    expect(label).toHaveClass('visually-hidden');
    expect(label).toHaveAttribute('for', 'ingredients-input');
  });

  // Removed invalid test: does not call onChange or onSubmit with null/undefined values

  // Parameterized tests for multiple edge cases (using actual whitespace/control characters)
  const invalidInputs = ['', '   ', '\n', '\t', String.fromCharCode(10), String.fromCharCode(9)];
  test.each(invalidInputs)('submit button is disabled when supplied value = "%s"', (testValue) => {
    const value =
      testValue === '\n' ? '\n' :
      testValue === '\t' ? '\t' : testValue;
    const { button } = setup({ value });
    expect(button).toBeDisabled();
  });

  // Parameterized tests for valid edge-case inputs
  const validInputs = ['egg', 'milk, tomato', '  cheese ', 'onion,garlic'];
  test.each(validInputs)('submit button is enabled when supplied value = "%s"', (testValue) => {
    const { button } = setup({ value: testValue });
    expect(button).toBeEnabled();
  });
  
  // Prevent form submission when disabled even with valid values
  test('does not submit when input has value but form is disabled', () => {
    const onSubmit = jest.fn();
    const { button } = setup({ value: 'toast', disabled: true, onSubmit });
    fireEvent.click(button);
    expect(onSubmit).not.toHaveBeenCalled();
  });
});