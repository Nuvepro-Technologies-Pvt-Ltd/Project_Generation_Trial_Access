// src/components/RecipeList.js
// Responsive grid for RecipeCard, clean layout for all screens
import React from 'react';
import RecipeCard from './RecipeCard';

function RecipeList({ recipes }) {
  // Instructions:
  // 1. Check if 'recipes' is defined and is not empty. If not, return null to render nothing.
  // 2. Render a <div> with className "row g-4" to create a responsive grid layout using Bootstrap grid classes.
  // 3. Iterate over the 'recipes' array using map.
  //    - For each item, extract the 'recipe' object (it could be available as item.recipe, otherwise use the item itself).
  //    - Within each iteration, render a <div> with the grid column classes "col-12 col-md-6 col-lg-4" for responsiveness.
  //    - Use either 'recipe.uri' or the map index (idx) as the unique key for each grid column div.
  //    - Inside this div, render a <RecipeCard /> component and pass the 'recipe' as its prop.
  // 4. Ensure the overall structure is contained in the main grid div.
}

export default RecipeList;
