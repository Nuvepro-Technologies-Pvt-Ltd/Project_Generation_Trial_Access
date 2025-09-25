// src/pages/ResultsPage.js
// Lists readable RecipeCards in a visually clean grid, with clear loading/empty/error states
import React from 'react';
import RecipeList from '../components/RecipeList';

function ResultsPage({ recipes, loading, error, searchedIngredients }) {
  if (loading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border" role="status" aria-label="Loading"></div>
        <div>Loading recipes...</div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="alert alert-danger my-5" role="alert" style={{maxWidth:500,margin:'auto'}}>
        {error}
      </div>
    );
  }
  if (!recipes || recipes.length === 0) {
    return (
      <div className="alert alert-info my-5 text-center" style={{maxWidth: 500,margin:'auto'}}>No recipes found for <strong>{searchedIngredients}</strong>.</div>
    );
  }
  return (
    <RecipeList recipes={recipes} />
  );
}

export default ResultsPage;
