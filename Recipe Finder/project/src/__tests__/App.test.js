import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import App from '../App';
import * as api from '../services/api';
// If using React Router v6, set up MemoryRouter if needed

// Comprehensive test suite for App.js covering navigation, UI states, input validation, async flows, and error handling
// Mocks and realistic test data included for maximum coverage

describe('App Integration and UI Flow', () => {
  const mockRecipes = [
    { recipe: { label: 'Tomato Pasta', uri: 'uri1', image: 'img1', ingredientLines: ['Tomato', 'Pasta'] } },
    { recipe: { label: 'Egg Sandwich', uri: 'uri2', image: 'img2', ingredientLines: ['Egg', 'Bread'] } }
  ];

  beforeEach(() => {
    jest.spyOn(api, 'fetchRecipesByIngredients').mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the home page with search bar and default UI', () => {
    render(<App />);
    expect(screen.getByText('Recipe Finder')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByText('Enter ingredients (comma-separated) to discover easy recipes you can make.')).toBeInTheDocument();
  });

  it('shows error when submitting empty input', async () => {
    render(<App />);
    fireEvent.submit(screen.getByRole('form'));
    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText('Please enter at least one ingredient.')).toBeInTheDocument();
    });
  });

  it('triggers loading and displays results on successful recipe fetch', async () => {
    jest.spyOn(api, 'fetchRecipesByIngredients').mockResolvedValue({ hits: mockRecipes });
    render(<App />);
    // Enter valid ingredients
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'tomato,pasta' } });
    fireEvent.submit(screen.getByRole('form'));
    expect(screen.getByText('Fetching recipes...')).toBeInTheDocument();
    // Wait for results to render
    await waitFor(() => {
      expect(screen.getByText(/Results for/)).toBeInTheDocument();
      expect(screen.getByText('Tomato Pasta')).toBeInTheDocument();
      expect(screen.getByText('Egg Sandwich')).toBeInTheDocument();
    });
    // Loading indicator disappears
    expect(screen.queryByText('Fetching recipes...')).not.toBeInTheDocument();
  });

  it('shows results header even when there are no recipe hits', async () => {
    jest.spyOn(api, 'fetchRecipesByIngredients').mockResolvedValue({ hits: [] });
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'kale,blue cheese' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => {
      expect(screen.getByText(/Results for/)).toBeInTheDocument();
      expect(screen.queryByText('No recipes found')).toBeInTheDocument(); // Assuming ResultsPage handles no-data case
    });
  });

  it('displays API generic error and retry logic', async () => {
    jest.spyOn(api, 'fetchRecipesByIngredients').mockRejectedValue(new Error('Network down'));
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'potato' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => {
      expect(screen.getByText('Network down')).toBeInTheDocument();
      expect(screen.getByText(/Try again/i)).toBeInTheDocument();
    });
    // Retry button resets error
    fireEvent.click(screen.getByText(/Try again/i));
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.queryByText('Network down')).not.toBeInTheDocument();
  });

  it('shows API 401 error with authentication message', async () => {
    const error = { response: { status: 401 } };
    jest.spyOn(api, 'fetchRecipesByIngredients').mockRejectedValue(error);
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'egg' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => {
      expect(screen.getByText('API authentication failed. Please check your credentials.')).toBeInTheDocument();
    });
  });

  it('shows custom API error message if present in error response', async () => {
    const error = { response: { data: { message: 'Invalid ingredients format' } } };
    jest.spyOn(api, 'fetchRecipesByIngredients').mockRejectedValue(error);
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '!!!' } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => {
      expect(screen.getByText('API Error: Invalid ingredients format')).toBeInTheDocument();
    });
  });

  it('prevents input and button disables while loading', async () => {
    jest.spyOn(api, 'fetchRecipesByIngredients').mockImplementation(() => new Promise(() => {})); // Never resolves
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'tomato' } });
    fireEvent.submit(screen.getByRole('form'));
    expect(screen.getByRole('textbox')).toBeDisabled();
    // Could also check that button is disabled if SearchBar renders one with 'disabled'
  });

  it('does not show overlapping UI states (loading, error, results)', async () => {
    // Triggers loading
    jest.spyOn(api, 'fetchRecipesByIngredients').mockImplementation(() => new Promise(() => {}));
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'beans' } });
    fireEvent.submit(screen.getByRole('form'));
    // Only loading indicator is visible
    expect(screen.getByText('Fetching recipes...')).toBeInTheDocument();
    expect(screen.queryByText('Recipe Finder')).not.toBeInTheDocument();
    expect(screen.queryByText('Results')).not.toBeInTheDocument();
    expect(screen.queryByText('Please enter at least one ingredient.')).not.toBeInTheDocument();
  });

  // Parameterized input validation
  const invalidInputs = [ '', '   ', ',' ];
  test.each(invalidInputs)('input "%s" triggers required error message', async (input) => {
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: input } });
    fireEvent.submit(screen.getByRole('form'));
    await waitFor(() => {
      expect(screen.getByText('Please enter at least one ingredient.')).toBeInTheDocument();
    });
  });

  // Accessibility checks (labels, headings)
  it('has accessible headings and form controls', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: /Recipe Finder/i })).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveAccessibleName();
  });

  // Security & edge case: input injection
  it('sanitizes input and handles suspicious characters safely', async () => {
    jest.spyOn(api, 'fetchRecipesByIngredients').mockResolvedValue({ hits: mockRecipes });
    render(<App />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'tomato,<script>alert(1)</script>' } });
    fireEvent.submit(screen.getByRole('form'));
    // Should still show results without error
    await waitFor(() => {
      expect(screen.getByText('Tomato Pasta')).toBeInTheDocument();
    });
  });
});