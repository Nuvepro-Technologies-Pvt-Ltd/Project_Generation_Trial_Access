// src/pages/ResultsPage.js
// Lists readable RecipeCards in a visually clean grid, with clear loading/empty/error states
import React from 'react';
import RecipeList from '../components/RecipeList';

function ResultsPage({ recipes, loading, error, searchedIngredients }) {
  // Instructions:
  // 1. Check if the 'loading' variable is true.
  //    - If so, render a spinner and a message indicating the recipes are loading (centered on the page, using appropriate classes/styles for a user-friendly appearance).
  // 2. If not loading, check if the 'error' variable has a value.
  //    - If there is an error, render an alert-style div with the error message clearly displayed (centered, visually highlighted as an error).
  // 3. If not loading and there is no error, check if the 'recipes' array is empty or not defined.
  //    - If so, render an info alert indicating that no recipes could be found for the ingredients inside 'searchedIngredients'.
  //    - Use a bold/strong element to display 'searchedIngredients' within the message.
  // 4. If none of the above, render the RecipeList component, passing the 'recipes' array as a prop to display them in a visually clean grid.
  // 5. Ensure all divs and elements use appropriate classes/styles for spacing, centering, and accessibility (e.g., my-5, text-center, alert classes).
}

export default ResultsPage;
