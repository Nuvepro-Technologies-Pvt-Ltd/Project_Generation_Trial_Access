import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import RecipeList from './RecipeList';
// The following import is needed to mock child component RecipeCard
import RecipeCard from './RecipeCard';
jest.mock('./RecipeCard', () => ({ recipe }) => (<div data-testid="mock-recipecard">{recipe.label}</div>));

// src/components/RecipeList.test.js
// Comprehensive test suite for RecipeList component
// Covers default, edge, and error scenarios; uses React Testing Library and Jest

describe('RecipeList', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('testRender_WithEmptyRecipes_ReturnsNull', () => {
    // Arrange: empty and undefined scenarios
    const { container: empty } = render(<RecipeList recipes={[]} />);
    const { container: none } = render(<RecipeList recipes={undefined} />);
    // Assert: nothing is rendered
    expect(empty.firstChild).toBeNull();
    expect(none.firstChild).toBeNull();
  });

  test('testRender_WithOneRecipe_RendersOneCard', () => {
    // Arrange
    const testRecipe = {
      uri: 'http://www.edamam.com/ontologies/edamam.owl#recipe_cake123',
      label: 'Test Cake',
      image: 'image_url',
      calories: 500
    };
    const recipesProp = [
      { recipe: testRecipe }
    ];
    // Act
    render(<RecipeList recipes={recipesProp} />);
    // Assert: mock RecipeCard used, grid exists
    expect(screen.getByText('Test Cake')).toBeInTheDocument();
    expect(screen.getByTestId('mock-recipecard')).toBeInTheDocument();
    expect(document.querySelector('.row.g-4')).toBeTruthy();
    expect(document.querySelectorAll('.col-12.col-md-6.col-lg-4')).toHaveLength(1);
  });

  test('testRender_WithMultipleRecipes_RendersAllCards', () => {
    // Arrange
    const makeRecipe = (i) => ({
      uri: `uri${i}`,
      label: `Recipe #${i}`,
      image: 'img', calories: 100
    });
    const recipesProp = [
      { recipe: makeRecipe(1) },
      { recipe: makeRecipe(2) },
      { recipe: makeRecipe(3) }
    ];
    // Act
    render(<RecipeList recipes={recipesProp} />);
    // Assert: three cards
    recipesProp.forEach((item) => {
      expect(screen.getByText(item.recipe.label)).toBeInTheDocument();
    });
    expect(document.querySelectorAll('[data-testid="mock-recipecard"]')).toHaveLength(3);
    expect(document.querySelectorAll('.col-12.col-md-6.col-lg-4')).toHaveLength(3);
  });

  test('testRender_WithItemsLackingRecipeKey_RendersCorrectly', () => {
    // Arrange: robust against malformed input (e.g., API responses with direct recipe objects)
    const directRecipe = {
      uri: 'uri42', label: 'Directly Provided', image: 'img', calories: 123
    };
    const recipes = [directRecipe];
    // Act
    render(<RecipeList recipes={recipes} />);
    // Assert
    expect(screen.getByText('Directly Provided')).toBeInTheDocument();
    expect(screen.getByTestId('mock-recipecard')).toBeInTheDocument();
  });

  test('testRender_WithMissingUri_FallbacksToIdxKey', () => {
    // Arrange: input where recipe.uri is missing
    const recipesProp = [
      { recipe: { label: 'No URI', image: 'img', calories: 9 } },
      { recipe: { label: 'Another No URI', image: 'img', calories: 11 } }
    ];
    // Act
    render(<RecipeList recipes={recipesProp} />);
    // Assert: rendered correctly
    expect(screen.getByText('No URI')).toBeInTheDocument();
    expect(screen.getByText('Another No URI')).toBeInTheDocument();
    const gridCols = document.querySelectorAll('.col-12.col-md-6.col-lg-4');
    expect(gridCols).toHaveLength(2);
  });

  // Edge case: recipes prop is a very large array (simple render performance test)
  test('testRender_WithLargeNumberOfRecipes_RendersAll', () => {
    const recipes = Array.from({ length: 50 }, (_, i) => ({ recipe: { uri: `uri${i}`, label: `R${i}` } }));
    render(<RecipeList recipes={recipes} />);
    // Assert
    expect(document.querySelectorAll('[data-testid="mock-recipecard"]').length).toBe(50);
    recipes.forEach(r => {
      expect(screen.getByText(r.recipe.label)).toBeInTheDocument();
    });
  });

  // Security test: ensure dangerous props (like XSS) in recipe label are escaped by React
  test('testRender_WithMaliciousLabel_EscapesContent', () => {
    const maliciousRecipe = { recipe: { uri: 'mal', label: '<img src=x onerror=alert(1)>', image: '', calories: 0 } };
    render(<RecipeList recipes={[maliciousRecipe]} />);
    // By default, React escapes HTML, so the tag is rendered as text, not as an image node
    const node = screen.getByText('<img src=x onerror=alert(1)>');
    expect(node).toBeInTheDocument();
    expect(node.tagName).toMatch(/div/i);
  });

  // Error scenario: recipes not an array
  test('testRender_WithNonArrayRecipes_GracefulNull', () => {
    render(<RecipeList recipes={42} />);
    expect(document.body.innerHTML).not.toMatch(/mock-recipecard/);
  });

  // Test correct Bootstrap grid classes for responsiveness
  test('testRender_GridClassPresent', () => {
    const testRecipe = { recipe: { uri: 'uri1', label: 'Responsive' } };
    render(<RecipeList recipes={[testRecipe]} />);
    expect(document.querySelector('.row.g-4')).toBeTruthy();
    expect(document.querySelector('.col-12.col-md-6.col-lg-4')).toBeTruthy();
  });
});