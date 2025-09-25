// src/components/RecipeCard.js
// Clean, legible, visually balanced card for recipe summary
import React from 'react';

function RecipeCard({ recipe }) {
  const title = recipe.label || 'Untitled Recipe';
  const image = recipe.image || 'https://via.placeholder.com/350x180?text=No+Image';
  const ingredients = Array.isArray(recipe.ingredientLines) ? recipe.ingredientLines : [];
  const steps = recipe.steps || null; // Edamam: not present, use null

  const renderSteps = () => {
    if (steps && Array.isArray(steps) && steps.length > 0) {
      return (
        <ol className="ps-3 mb-2 small">
          {steps.map((step, idx) => (<li key={idx}>{step}</li>))}
        </ol>
      );
    }
    return (
      <div className="alert alert-warning py-2 px-3 small mb-1" style={{fontSize: '0.97em'}}>
        Preparation steps are not available for this recipe. Please visit the source for details.
      </div>
    );
  };

  return (
    <div className="card h-100 shadow-sm">
      <img
        src={image}
        alt={title}
        className="card-img-top"
        style={{objectFit: 'cover', height: '220px'}}
      />
      <div className="card-body d-flex flex-column">
        <h5 className="card-title mb-1">{title}</h5>
        <p className="text-muted mb-1" style={{fontSize: '0.98em'}}>
          <strong>Calories:</strong> {Math.round(recipe.calories || 0)} kcal
        </p>
        <div>
          <strong>Ingredients:</strong>
          <ul className="ps-3 small mb-2">
            {ingredients.length === 0 ? (
              <li>No ingredient data</li>
            ) : (
              ingredients.map((ing, i) => <li key={i}>{ing}</li>)
            )}
          </ul>
        </div>
        <div>
          <strong>Preparation Steps:</strong>
          {renderSteps()}
        </div>
        <a
          href={recipe.url}
          className="btn btn-outline-primary btn-sm mt-auto align-self-start"
          target="_blank"
          rel="noopener noreferrer"
        >
          View Full Recipe
        </a>
      </div>
    </div>
  );
}

export default RecipeCard;