import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResultsPage from '../../src/pages/ResultsPage';
import RecipeList from '../../src/components/RecipeList';
jest.mock('../../src/components/RecipeList');

// Test suite for ResultsPage React component.
// Covers all UI states: loading, error, empty results, successful results.
// Mocks RecipeList for isolation.
describe('ResultsPage', () => {
  const sampleRecipes = [
    { id: 1, title: 'Pancakes', description: 'Fluffy breakfast pancakes', image: 'pancakes.jpg' },
    { id: 2, title: 'Omelette', description: 'Cheesy omelette', image: 'omelette.jpg' }
  ];
  const searchedIngredients = 'eggs, milk';

  beforeEach(() => {
    // Reset mocked implementations before each test
    RecipeList.mockImplementation(() => <div data-testid="mocked-recipe-list"></div>);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('testLoading_True_ShowsLoadingSpinnerAndText', () => {
    // Arrange & Act
    render(<ResultsPage recipes={[]} loading={true} error={null} searchedIngredients={searchedIngredients} />);

    // Assert
    expect(screen.getByRole('status', { name: /loading/i })).toBeInTheDocument();
    expect(screen.getByText(/Loading recipes.../i)).toBeInTheDocument();
    // Should not render any error or recipe list
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.queryByTestId('mocked-recipe-list')).not.toBeInTheDocument();
    expect(screen.queryByText(/No recipes found/i)).not.toBeInTheDocument();
  });

  test('testError_NonNull_ShowsErrorMessage', () => {
    // Arrange
    const errorText = 'Failed to fetch recipes!';
    // Act
    render(<ResultsPage recipes={[]} loading={false} error={errorText} searchedIngredients={searchedIngredients} />);

    // Assert
    const alert = screen.getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveClass('alert-danger');
    expect(alert).toHaveTextContent(errorText);
    // Should not render spinner or recipe list
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.queryByTestId('mocked-recipe-list')).not.toBeInTheDocument();
    expect(screen.queryByText(/No recipes found/i)).not.toBeInTheDocument();
  });

  test('testRecipes_EmptyArrayOrNull_ShowsEmptyStateMessage', () => {
    // Arrange & Act
    render(<ResultsPage recipes={[]} loading={false} error={null} searchedIngredients={searchedIngredients} />);
    // Assert
    const emptyMsg = screen.getByText(/No recipes found for/i);
    expect(emptyMsg).toBeInTheDocument();
    expect(emptyMsg).toHaveClass('alert-info');
    expect(emptyMsg).toHaveTextContent('No recipes found for');
    expect(emptyMsg).toHaveTextContent(searchedIngredients);
    // Should not render spinner, error, or recipe list
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.queryByRole('alert', { class: /alert-danger/ })).not.toBeInTheDocument();
    expect(screen.queryByTestId('mocked-recipe-list')).not.toBeInTheDocument();
  });

  test('testRecipes_Null_ShowsEmptyStateMessage', () => {
    render(<ResultsPage recipes={null} loading={false} error={null} searchedIngredients={searchedIngredients} />);
    const emptyMsg = screen.getByText(/No recipes found for/i);
    expect(emptyMsg).toBeInTheDocument();
    expect(emptyMsg).toHaveClass('alert-info');
    expect(emptyMsg).toHaveTextContent('No recipes found for');
    expect(emptyMsg).toHaveTextContent(searchedIngredients);
    expect(screen.queryByTestId('mocked-recipe-list')).not.toBeInTheDocument();
  });

  test('testRecipes_WithResults_CallsRecipeListWithCorrectProps', () => {
    render(<ResultsPage recipes={sampleRecipes} loading={false} error={null} searchedIngredients={searchedIngredients} />);
    // Confirm RecipeList gets rendered
    expect(screen.getByTestId('mocked-recipe-list')).toBeInTheDocument();
    // Confirm correct props passed
    expect(RecipeList).toHaveBeenCalledWith(
      expect.objectContaining({ recipes: sampleRecipes }),
      {}
    );
    // No loading, error or empty message
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.queryByText(/No recipes found/i)).not.toBeInTheDocument();
  });

  test('testSearchedIngredients_Empty_ShowsNoRecipesForBlank', () => {
    render(<ResultsPage recipes={[]} loading={false} error={null} searchedIngredients={''} />);
    const emptyMsg = screen.getByText(/No recipes found for/i);
    expect(emptyMsg).toBeInTheDocument();
    expect(emptyMsg).toHaveTextContent('No recipes found for');
    // Empty strong tag means blank ingredient
    expect(emptyMsg.querySelector('strong')).toBeInTheDocument();
    expect(emptyMsg.querySelector('strong')).toHaveTextContent('');
  });

  test('testInvalidProps_RecipesUndefined_DefaultsToEmptyState', () => {
    render(<ResultsPage loading={false} error={null} searchedIngredients={searchedIngredients} />);
    expect(screen.getByText(/No recipes found for/i)).toBeInTheDocument();
    expect(screen.queryByTestId('mocked-recipe-list')).not.toBeInTheDocument();
  });

  // Parameterized edge cases for recipes prop
  test.each([
    [[], 'No recipes found for'],
    [null, 'No recipes found for'],
    [undefined, 'No recipes found for'],
  ])('testRecipes_%p_ShowsEmptyState', (input, expectedMsg) => {
    render(<ResultsPage recipes={input} loading={false} error={null} searchedIngredients={searchedIngredients} />);
    expect(screen.getByText(new RegExp(expectedMsg, 'i'))).toBeInTheDocument();
  });
});