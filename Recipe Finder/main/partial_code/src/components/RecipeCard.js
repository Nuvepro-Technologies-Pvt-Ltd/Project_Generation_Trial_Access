// src/components/RecipeCard.js
// Clean, legible, visually balanced card for recipe summary
import React from 'react';

function RecipeCard({ recipe }) {
  // Set up variables for display
  const title = recipe.label || 'Untitled Recipe';
  const image = recipe.image || 'https://via.placeholder.com/350x180?text=No+Image';
  const ingredients = Array.isArray(recipe.ingredientLines) ? recipe.ingredientLines : [];
  const steps = recipe.steps || null; // Steps might be unavailable

  // Function to render preparation steps
  const renderSteps = () => {
    // INSTRUCTION: If 'steps' exists, is an array, and contains at least one step, render an ordered list (ol) where each step is a list item (li).
    // Otherwise, display a warning message informing the user that preparation steps are not available.
    // Use appropriate CSS classes for styling, such as 'ps-3 mb-2 small' for the list and an alert for the warning message.
    // Iterate over 'steps' using map and assign a unique 'key' to each li.
    // If no steps, show a div with a warning text.
  };

  // Component render logic
  return (
    // INSTRUCTION: Create a card layout for the recipe summary.
    // 1. Display the recipe image using the 'image' variable. Add proper alt text using the 'title' variable, set CSS class 'card-img-top', and restrict height with 'objectFit' and 'height' style properties.
    // 2. Create a container for card content with class 'card-body d-flex flex-column'.
    // 3. Inside the card body:
    //    - Render the recipe 'title' as an h5 element (class 'card-title mb-1').
    //    - Render the calories (rounded) using 'recipe.calories'.
    //    - Display the ingredients:
    //        a. Render a heading 'Ingredients:'.
    //        b. Use an unordered list (ul) with 'ps-3 small mb-2' classes.
    //        c. For each ingredient in 'ingredients' array, render a list item. If the array is empty, show 'No ingredient data'.
    //    - Display the preparation steps section:
    //        a. Render a heading 'Preparation Steps:'.
    //        b. Invoke the 'renderSteps()' function to display either the steps list or the unavailable warning.
    //    - Add a link (<a>) to view the full recipe:
    //        a. Set href to 'recipe.url'.
    //        b. Use class 'btn btn-outline-primary btn-sm mt-auto align-self-start'.
    //        c. Open the link in a new tab, using target='_blank' and rel='noopener noreferrer'.
    //        d. The link text should be 'View Full Recipe'.
    // Remember to wrap the card layout in a root div with class 'card h-100 shadow-sm'.
  );
}

export default RecipeCard;