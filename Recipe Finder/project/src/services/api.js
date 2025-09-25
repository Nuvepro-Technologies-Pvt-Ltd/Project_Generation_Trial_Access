// src/services/api.js
// Centralized API service using Axios for recipe search based on ingredients

import axios from 'axios';

// === API Configuration ===
// Edamam Recipe Search API (for demonstration purposes)
// Replace 'YOUR_APP_ID' and 'YOUR_APP_KEY' with your actual credentials or use .env for production.
const BASE_URL = 'https://api.edamam.com/search';
const APP_ID = 'YOUR_APP_ID'; // Secure in .env for actual projects
const APP_KEY = 'YOUR_APP_KEY';

/**
 * Fetch recipes from Edamam based on a list of ingredients.
 * @param {string[]} ingredientsArr - Array of individual ingredient strings.
 * @returns {Promise<Object>} - API response data (recipes array or error)
 */
export async function fetchRecipesByIngredients(ingredientsArr) {
  // Precondition: ingredientsArr is an array of trimmed, non-empty strings.
  const query = ingredientsArr.join(',');
  const url = `${BASE_URL}?q=${encodeURIComponent(query)}&app_id=${APP_ID}&app_key=${APP_KEY}`;
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    // Forward axios error to caller for handling
    throw error;
  }
}

// Note: Credentials should be protected in a real project (e.g., with .env + build tool support)
