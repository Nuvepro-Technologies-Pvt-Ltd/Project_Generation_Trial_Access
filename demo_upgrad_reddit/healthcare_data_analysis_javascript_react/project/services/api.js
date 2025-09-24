// services/api.js
import axios from 'axios';

// Define the API base URL here
const API_BASE_URL = 'https://api.example.com';

// Fetches AI analysis results (entity highlights, summary stats)
export const fetchAIResults = async () => {
  // GET /api/v1/ai/analysis
  const res = await axios.get(`${API_BASE_URL}/api/v1/ai/analysis`);
  return res.data;
};

// Fetches generated synthetic data entries
export const fetchSyntheticData = async () => {
  // GET /api/v1/ai/synthetic-data
  const res = await axios.get(`${API_BASE_URL}/api/v1/ai/synthetic-data`);
  return res.data;
};
