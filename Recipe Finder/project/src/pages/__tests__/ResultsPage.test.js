import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ResultsPage from '../ResultsPage';

// src/pages/__tests__/ResultsPage.test.js
// Unit and integration tests for ResultsPage component covering all states, edge and error cases

// Arrange: common test data
const sampleRecipes = [
  { id: 1, name: 'Tomato Soup', ingredients: ['tomato'] },
  { id: 2, name: 'Chicken Salad', ingredients: ['chicken', 'lettuce'] }
];
const searchedIngredientsSample = 'tomato, chicken';

// Act & Assert: Loading scenario
it('testRender_loading_showsSpinnerAndLoadingText', () => {
  render(<ResultsPage recipes={[]} loading={true} error={null} searchedIngredients={searchedIngredientsSample} />);
  expect(screen.getByLabelText('Loading')).toBeInTheDocument();
  expect(screen.getByText('Loading recipes...')).toBeInTheDocument();
});

// Act & Assert: Error scenario
it('testRender_error_showsAlertWithError', () => {
  const errorMsg = 'Network error! Please try again.';
  render(<ResultsPage recipes={[]} loading={false} error={errorMsg} searchedIngredients={searchedIngredientsSample} />);
  const alert = screen.getByRole('alert');
  expect(alert).toHaveClass('alert-danger');
  expect(alert).toHaveTextContent(errorMsg);
});

// Act & Assert: No recipes found (empty array)
it('testRender_emptyRecipes_showsNoFoundMessage', () => {
  render(<ResultsPage recipes={[]} loading={false} error={null} searchedIngredients={searchedIngredientsSample} />);
  const alert = screen.getByRole('alert');
  expect(alert).toHaveClass('alert-info');
  expect(alert).toHaveTextContent('No recipes found');
  expect(alert).toHaveTextContent(searchedIngredientsSample);
});

// Act & Assert: No recipes found (null recipes)
it('testRender_nullRecipes_showsNoFoundMessage', () => {
  render(<ResultsPage recipes={null} loading={false} error={null} searchedIngredients={searchedIngredientsSample} />);
  const alert = screen.getByRole('alert');
  expect(alert).toHaveClass('alert-info');
  expect(alert).toHaveTextContent('No recipes found');
  expect(alert).toHaveTextContent(searchedIngredientsSample);
});

// Act & Assert: Normal (non-empty) render
it('testRender_withRecipes_rendersRecipeList', () => {
  render(<ResultsPage recipes={sampleRecipes} loading={false} error={null} searchedIngredients={searchedIngredientsSample} />);
  // Should not render any alert or spinner
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument();
  // Should delegate to RecipeList and render recipe names
  expect(screen.getByText('Tomato Soup')).toBeInTheDocument();
  expect(screen.getByText('Chicken Salad')).toBeInTheDocument();
});

// Edge case: long error message wraps gracefully
it('testRender_longError_showsScrollableAlert', () => {
  const errorMsg = 'An unexpected error occurred while fetching data. Please check your network connection or try again later. This is a long error message to test wrapping.';
  render(<ResultsPage recipes={[]} loading={false} error={errorMsg} searchedIngredients={searchedIngredientsSample} />);
  const alert = screen.getByRole('alert');
  expect(alert).toHaveTextContent('unexpected error occurred');
});

// Edge case: searchedIngredients is empty or null
it('testRender_noSearchedIngredients_displaysGenericMessage', () => {
  render(<ResultsPage recipes={[]} loading={false} error={null} searchedIngredients={''} />);
  const alert = screen.getByRole('alert');
  expect(alert).toHaveTextContent('No recipes found');
});

// Parameterized error state (multiple types of error)
['Failed to load!', 'Server timeout', 'Something went wrong.'].forEach((msg) => {
  it(`testRender_errorMessageVariant_'${msg}'_showsAlert`, () => {
    render(<ResultsPage recipes={[]} loading={false} error={msg} searchedIngredients={searchedIngredientsSample} />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(msg);
  });
});

// Negative scenario: recipes prop is not an array, should fallback to empty/edge behavior
it('testRender_nonArrayRecipes_treatsAsNoRecipes', () => {
  render(<ResultsPage recipes={42} loading={false} error={null} searchedIngredients={searchedIngredientsSample} />);
  const alert = screen.getByRole('alert');
  expect(alert).toHaveTextContent('No recipes found');
});

// Performance (lightweight): very large recipe list
it('testRender_largeRecipeList_rendersQuicklyWithoutError', () => {
  const largeRecipes = Array.from({length: 100}, (_, i) => ({ id: i, name: `Recipe ${i}` }));
  render(<ResultsPage recipes={largeRecipes} loading={false} error={null} searchedIngredients={searchedIngredientsSample} />);
  expect(screen.getByText('Recipe 0')).toBeInTheDocument();
  expect(screen.getByText('Recipe 99')).toBeInTheDocument();
});

// Security: XSS input into error or searchedIngredients is rendered safely
it('testRender_xssInErrorAndIngredients_rendersAsText', () => {
  const xssStr = '<img src=x onerror=alert(1) />';
  render(<ResultsPage recipes={[]} loading={false} error={xssStr} searchedIngredients={xssStr} />);
  // Resulting text is present as text, not rendered as actual HTML
  expect(screen.getByRole('alert')).toHaveTextContent(xssStr);
});