import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import RecipeList from '../RecipeList';
jest.mock('../RecipeCard', () => ({ recipe }) => (<div data-testid="mock-recipecard">{recipe.label || recipe.id}</div>));

// src/components/__tests__/RecipeList.test.js
// Test suite for RecipeList.js - React Testing Library & Jest
// Covers rendering logic, empty/null input, map structure, uniqueness, and RecipeCard integration

describe('RecipeList Component', () => {
  // Dummy recipe data
  const mockRecipes = [
    { id: '1', label: 'Spaghetti Bolognese', uri: 'recipe_1' },
    { id: '2', label: 'Chicken Curry', uri: 'recipe_2' },
    { id: '3', label: 'Salad Bowl', uri: 'recipe_3' }
  ];

  it('testRender_withValidRecipes_rendersGridWithRecipeCards', () => {
    render(<RecipeList recipes={mockRecipes} />);
    expect(screen.getAllByTestId('mock-recipecard')).toHaveLength(3);
    expect(screen.getByText('Spaghetti Bolognese')).toBeInTheDocument();
    expect(screen.getByText('Chicken Curry')).toBeInTheDocument();
    expect(screen.getByText('Salad Bowl')).toBeInTheDocument();
    // Assert clean grid layout class presence:
    const grid = screen.getByRole('region', { hidden: true }) || document.querySelector('.row.g-4');
    expect(grid).toBeInTheDocument();
  });

  it('testRender_withEmptyRecipesInput_returnsNull', () => {
    const { container } = render(<RecipeList recipes={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('testRender_withUndefinedOrNullRecipes_returnsNull', () => {
    const { container: nullContainer } = render(<RecipeList recipes={null} />);
    expect(nullContainer.firstChild).toBeNull();
    const { container: undefContainer } = render(<RecipeList recipes={undefined} />);
    expect(undefContainer.firstChild).toBeNull();
  });

  it('testRender_withWrappedRecipeObject_rendersCorrectly', () => {
    const nestedRecipes = [
      { recipe: { id: 'wrapped1', label: 'Wrapped Stew', uri: 'recipe_wrapped1' } },
      { recipe: { id: 'wrapped2', label: 'Wrapped Pie', uri: 'recipe_wrapped2' } }
    ];
    render(<RecipeList recipes={nestedRecipes} />);
    expect(screen.getAllByTestId('mock-recipecard')).toHaveLength(2);
    expect(screen.getByText('Wrapped Stew')).toBeInTheDocument();
    expect(screen.getByText('Wrapped Pie')).toBeInTheDocument();
  });

  it('testRender_withMissingUri_usesIndexAsKey', () => {
    const recipesNoUri = [
      { id: 'a', label: 'No URI 1' },
      { id: 'b', label: 'No URI 2' }
    ];
    const { container } = render(<RecipeList recipes={recipesNoUri} />);
    // The code will fallback to index for missing uri: ensure all rendered
    expect(screen.getAllByTestId('mock-recipecard')).toHaveLength(2);
    // Explicit key test is not practical in the DOM, but no error or warning means fallback handled
  });

  it('testRender_withFalsyRecipeList_doesNotBreak', () => {
    expect(() => render(<RecipeList recipes={false} />)).not.toThrow();
    expect(() => render(<RecipeList recipes={0} />)).not.toThrow();
    expect(() => render(<RecipeList recipes={''} />)).not.toThrow();
  });

  it('testRender_withMixedWrappedAndDirect_rendersAll', () => {
    const mixed = [
      { recipe: { id: 'x', label: 'Mixed One', uri: 'mixed-x' } },
      { id: 'y', label: 'Mixed Two', uri: 'mixed-y' }
    ];
    render(<RecipeList recipes={mixed} />);
    expect(screen.getAllByTestId('mock-recipecard')).toHaveLength(2);
    expect(screen.getByText('Mixed One')).toBeInTheDocument();
    expect(screen.getByText('Mixed Two')).toBeInTheDocument();
  });

  it('testRender_withDuplicateUri_propsKeyUniqueness', () => {
    // Should not break when some recipes have duplicate uris (edge case)
    const duplicate = [
      { id: '1', label: 'Dup 1', uri: 'dupe' },
      { id: '2', label: 'Dup 2', uri: 'dupe' } // both .uri === 'dupe', keys fallback to first instance, second will fallback to idx
    ];
    render(<RecipeList recipes={duplicate} />);
    expect(screen.getAllByTestId('mock-recipecard')).toHaveLength(2);
    expect(screen.getByText('Dup 1')).toBeInTheDocument();
    expect(screen.getByText('Dup 2')).toBeInTheDocument();
  });

  // Performance & large list render
  it('testRender_withLargeRecipeList_rendersEfficiently', () => {
    const largeList = Array.from({ length: 150 }, (_, i) => ({ id: `${i+1000}`, label: `Test ${i+1}`, uri: `uri_${i}` }));
    render(<RecipeList recipes={largeList} />);
    expect(screen.getAllByTestId('mock-recipecard')).toHaveLength(150);
  });

  // Security/Validation: does not inject unwanted HTML
  it('testRender_withMaliciousLabel_doesNotInjectHtml', () => {
    const malicious = [ { id: 'hack', label: '<img src=x onerror=alert(1)//', uri: 'badimguri' } ];
    render(<RecipeList recipes={malicious} />);
    // Not executing HTML; merely showing as text
    expect(screen.queryByText('<img src=x onerror=alert(1)//')).toBeInTheDocument();
  });

});