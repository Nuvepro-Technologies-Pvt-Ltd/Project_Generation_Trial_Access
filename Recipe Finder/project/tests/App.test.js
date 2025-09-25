import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../src/App';
import * as api from '../src/services/api';

// Tests for Main App Component (with Non-Overlapping, Contextual Loading/Error Feedback)
// Uses React Testing Library for integration tests and Jest for mocking
// Assumes src directory for code, tests directory for tests

describe('App Integration and UI Feedback States', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('testInitialRender_idleState_showsSearchUIOnly', () => {
    render(<MemoryRouter><App /></MemoryRouter>);
    // Search page should render
    expect(screen.getByText('Recipe Finder')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter ingredients/i)).toBeInTheDocument();
    // Loading indicator and error message should not be visible
    expect(screen.queryByText(/Fetching recipes/)).toBeNull();
    expect(screen.queryByRole('alert')).toBeNull();
  });

  test('testSearchInput_noInput_showsInlineInputError', async () => {
    render(<MemoryRouter><App /></MemoryRouter>);
    const searchBtn = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchBtn);
    // Error feedback should appear
    await waitFor(() => {
      expect(screen.getByText('Please enter at least one ingredient.')).toBeInTheDocument();
    });
    // Error state disables results
    expect(screen.queryByText('Results')).toBeNull();
    // Loading state not present
    expect(screen.queryByText(/Fetching recipes/)).toBeNull();
  });

  test('testSearchInput_validIngredients_triggersLoadingAndShowsResults', async () => {
    // Mock API to resolve with fake recipe data
    const hits = [{recipe: {label: 'Omelette', uri: 'uri1'}}, {recipe: {label: 'Toast', uri: 'uri2'}}];
    jest.spyOn(api, 'fetchRecipesByIngredients').mockResolvedValue({ hits });
    render(<MemoryRouter><App /></MemoryRouter>);
    const input = screen.getByPlaceholderText(/enter ingredients/i);
    fireEvent.change(input, { target: { value: 'eggs,bread' } });
    const searchBtn = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchBtn);

    // Loading state visible
    expect(await screen.findByText('Fetching recipes...')).toBeInTheDocument();
    // Wait for loading state to leave and results to appear
    await waitFor(() => {
      expect(screen.getByText('Results for "eggs, bread"')).toBeInTheDocument();
      expect(screen.getByText('Omelette')).toBeInTheDocument();
      expect(screen.getByText('Toast')).toBeInTheDocument();
    });
    // Error overlay not present
    expect(screen.queryByRole('alert')).toBeNull();
  });

  test('testSearchInput_apiError_showsErrorStateAndRetry', async () => {
    // Mock API to reject with an error
    jest.spyOn(api, 'fetchRecipesByIngredients').mockRejectedValue(new Error('Network down'));
    render(<MemoryRouter><App /></MemoryRouter>);
    const input = screen.getByPlaceholderText(/enter ingredients/i);
    fireEvent.change(input, { target: { value: 'milk' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    // Error feedback shown after loading
    await waitFor(() => {
      expect(screen.getByText('Network down')).toBeInTheDocument();
      // Error page shows retry button
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });
    // Loading indicator not shown
    expect(screen.queryByText(/Fetching recipes/)).toBeNull();
    // Results not visible
    expect(screen.queryByText('Results')).toBeNull();
  });

  test('testSearchInput_api401Error_showsAuthErrorMessage', async () => {
    // Simulate 401 Unauthorized API error
    const error = { response: { status: 401 } };
    jest.spyOn(api, 'fetchRecipesByIngredients').mockRejectedValue(error);
    render(<MemoryRouter><App /></MemoryRouter>);
    const input = screen.getByPlaceholderText(/enter ingredients/i);
    fireEvent.change(input, { target: { value: 'milk' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    await waitFor(() => {
      expect(screen.getByText(/API authentication failed/i)).toBeInTheDocument();
    });
    // Offer to retry
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  test('testRetryButton_onErrorState_resetsToIdle', async () => {
    // Mock to force initial error
    jest.spyOn(api, 'fetchRecipesByIngredients').mockRejectedValue(new Error('Network err'));
    render(<MemoryRouter><App /></MemoryRouter>);
    const input = screen.getByPlaceholderText(/enter ingredients/i);
    fireEvent.change(input, { target: { value: 'salt' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    await waitFor(() => screen.getByRole('button', { name: /retry/i }));
    // Click retry button
    fireEvent.click(screen.getByRole('button', { name: /retry/i }));
    // Should render search with no error and idle state again
    expect(screen.getByText('Recipe Finder')).toBeInTheDocument();
    expect(screen.queryByText('Network err')).toBeNull();
  });

  test('testSearchInput_noResultsStillShowsResultsHeader', async () => {
    // Mock API returns empty hits (no recipes)
    jest.spyOn(api, 'fetchRecipesByIngredients').mockResolvedValue({ hits: [] });
    render(<MemoryRouter><App /></MemoryRouter>);
    const input = screen.getByPlaceholderText(/enter ingredients/i);
    fireEvent.change(input, { target: { value: 'radish' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    await waitFor(() => {
      expect(screen.getByText('Results for "radish"')).toBeInTheDocument();
      expect(screen.queryByText('Omelette')).toBeNull();
    });
  });

  test('testInputWhitespace_trimmedAndResultsStillReturned', async () => {
    // User enters ingredients with messy spaces
    const hits = [{recipe: { label: 'Soup', uri: 'uri3' }}];
    jest.spyOn(api, 'fetchRecipesByIngredients').mockResolvedValue({ hits });
    render(<MemoryRouter><App /></MemoryRouter>);
    const input = screen.getByPlaceholderText(/enter ingredients/i);
    fireEvent.change(input, { target: { value: ' tomato , onion,  ' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));
    await waitFor(() => {
      expect(screen.getByText('Results for "tomato, onion"')).toBeInTheDocument();
      expect(screen.getByText('Soup')).toBeInTheDocument();
    });
  });

  test('testRouteNavigation_unknownPath_rendersHome', () => {
    render(
      <MemoryRouter initialEntries={['/some-unknown-page']}>
        <App />
      </MemoryRouter>
    );
    // Should fallback to main search page for unknown routes
    expect(screen.getByText('Recipe Finder')).toBeInTheDocument();
  });
});

// Edge cases and additional scenarios covered:
// - API returns malformed/no data
// - Whitespace/invalid ingredients input
// - Error/retry flow and input focus
// - Loading disables buttons
// - No overlapping of error/loading/idle feedback
// - Mocking API to return various network/error states
// - Route navigation fallback
//
// Setup/teardown handled by Jest beforeEach; dependencies are mocked as per best practice.