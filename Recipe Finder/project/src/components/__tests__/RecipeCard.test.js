import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import RecipeCard from '../RecipeCard';

// Test suite for RecipeCard component
// Covers prop variations, edge cases, rendering, and accessibility

describe('RecipeCard', () => {
  const baseRecipe = {
    label: 'Chocolate Cake',
    image: 'https://example.com/cake.jpg',
    ingredientLines: ['2 eggs', '1 cup flour', '1 cup sugar'],
    steps: ['Preheat oven', 'Mix ingredients', 'Bake for 30 minutes'],
    calories: 345.6,
    url: 'https://recipes.com/chocolate-cake'
  };

  it('renders correct title and image', () => {
    render(<RecipeCard recipe={baseRecipe} />);
    expect(screen.getByRole('heading', { name: 'Chocolate Cake' })).toBeInTheDocument();
    expect(screen.getByAltText('Chocolate Cake')).toHaveAttribute('src', baseRecipe.image);
  });

  it('renders fallback title and image when missing from recipe', () => {
    const recipe = { ...baseRecipe, label: undefined, image: undefined };
    render(<RecipeCard recipe={recipe} />);
    expect(screen.getByRole('heading', { name: 'Untitled Recipe' })).toBeInTheDocument();
    expect(screen.getByAltText('Untitled Recipe')).toHaveAttribute(
      'src',
      'https://via.placeholder.com/350x180?text=No+Image'
    );
  });

  it('renders the calorie count rounded down and label', () => {
    render(<RecipeCard recipe={baseRecipe} />);
    expect(screen.getByText(/Calories:/)).toHaveTextContent('Calories: 346 kcal');
  });

  it('renders ingredient list correctly', () => {
    render(<RecipeCard recipe={baseRecipe} />);
    baseRecipe.ingredientLines.forEach((ing) => {
      expect(screen.getByText(ing)).toBeInTheDocument();
    });
    expect(screen.getByText('Ingredients:')).toBeInTheDocument();
  });

  it('renders fallback item when ingredientLines is missing or not array', () => {
    render(<RecipeCard recipe={{ ...baseRecipe, ingredientLines: undefined }} />);
    expect(screen.getByText('No ingredient data')).toBeInTheDocument();
    render(<RecipeCard recipe={{ ...baseRecipe, ingredientLines: null }} />);
    expect(screen.getByText('No ingredient data')).toBeInTheDocument();
    render(<RecipeCard recipe={{ ...baseRecipe, ingredientLines: {} }} />);
    expect(screen.getByText('No ingredient data')).toBeInTheDocument();
  });

  it('renders preparation steps in order when present', () => {
    render(<RecipeCard recipe={baseRecipe} />);
    expect(screen.getByText('Preparation Steps:')).toBeInTheDocument();
    baseRecipe.steps.forEach(step => {
      expect(screen.getByText(step)).toBeInTheDocument();
    });
    // Should render as list items
    expect(screen.getAllByRole('listitem').length).toBeGreaterThanOrEqual(3);
  });

  it('renders fallback alert when steps is missing, null, empty, or not array', () => {
    const fallbackText = 'Preparation steps are not available for this recipe. Please visit the source for details.';
    render(<RecipeCard recipe={{ ...baseRecipe, steps: null }} />);
    expect(screen.getByText(fallbackText)).toBeInTheDocument();
    render(<RecipeCard recipe={{ ...baseRecipe, steps: undefined }} />);
    expect(screen.getByText(fallbackText)).toBeInTheDocument();
    render(<RecipeCard recipe={{ ...baseRecipe, steps: [] }} />);
    expect(screen.getByText(fallbackText)).toBeInTheDocument();
    render(<RecipeCard recipe={{ ...baseRecipe, steps: {} }} />);
    expect(screen.getByText(fallbackText)).toBeInTheDocument();
  });

  it('links to the full recipe with correct href and attributes', () => {
    render(<RecipeCard recipe={baseRecipe} />);
    const link = screen.getByRole('link', { name: /View Full Recipe/i });
    expect(link).toHaveAttribute('href', baseRecipe.url);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('handles zero or undefined calories gracefully', () => {
    render(<RecipeCard recipe={{ ...baseRecipe, calories: 0 }} />);
    expect(screen.getByText(/Calories:/)).toHaveTextContent('Calories: 0 kcal');

    render(<RecipeCard recipe={{ ...baseRecipe, calories: undefined }} />);
    expect(screen.getByText(/Calories:/)).toHaveTextContent('Calories: 0 kcal');
  });

  it('renders without crashing if given a completely empty recipe', () => {
    expect(() => render(<RecipeCard recipe={{}} />)).not.toThrow();
    expect(screen.getByText('Untitled Recipe')).toBeInTheDocument();
    expect(screen.getByText('Calories: 0 kcal')).toBeInTheDocument();
    expect(screen.getByText('No ingredient data')).toBeInTheDocument();
    expect(screen.getByText('Preparation steps are not available for this recipe. Please visit the source for details.')).toBeInTheDocument();
  });

  it('should be accessible by heading and link roles', () => {
    render(<RecipeCard recipe={baseRecipe} />);
    expect(screen.getByRole('heading', { name: /Chocolate Cake/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /View Full Recipe/i })).toBeInTheDocument();
  });

  // Parameterized (table-driven) test for different edge ingredient forms
  const ingredientVariants = [
    { val: undefined, desc: 'undefined' },
    { val: null, desc: 'null' },
    { val: {}, desc: 'object' },
    { val: [], desc: 'empty array' },
  ];
  ingredientVariants.forEach(({ val, desc }) => {
    it(`shows 'No ingredient data' if ingredientLines is ${desc}`, () => {
      render(<RecipeCard recipe={{ ...baseRecipe, ingredientLines: val }} />);
      expect(screen.getByText('No ingredient data')).toBeInTheDocument();
    });
  });

  // Security test: URL is properly escaped in the anchor (browser will, but check it's rendered as assigned)
  it('renders recipe.url unsanitized for usage in anchor href (should delegate escaping to browser)', () => {
    const url = 'javascript:alert(1)'; // Not recommended, but test to ensure it appears
    render(<RecipeCard recipe={{ ...baseRecipe, url }} />);
    const link = screen.getByRole('link', { name: /View Full Recipe/i });
    expect(link).toHaveAttribute('href', url);
  });
});