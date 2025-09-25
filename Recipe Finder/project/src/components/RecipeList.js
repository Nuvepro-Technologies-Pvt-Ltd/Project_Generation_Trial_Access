// src/components/RecipeList.js
// Responsive grid for RecipeCard, clean layout for all screens
import React from 'react';
import RecipeCard from './RecipeCard';

function RecipeList({ recipes }) {
  if (!recipes || recipes.length === 0) return null;
  return (
    <div className="row g-4">
      {recipes.map((item, idx) => {
        const recipe = item.recipe || item;
        return (
          <div className="col-12 col-md-6 col-lg-4" key={recipe.uri || idx}>
            <RecipeCard recipe={recipe} />
          </div>
        );
      })}
    </div>
  );
}

export default RecipeList;
