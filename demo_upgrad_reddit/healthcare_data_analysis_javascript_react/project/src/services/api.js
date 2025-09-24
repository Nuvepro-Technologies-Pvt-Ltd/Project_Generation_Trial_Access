// services/api.js
import axios from 'axios';

// Base API URL
const API_BASE_URL = 'https://api.example.com';

// Fetch AI entity/stats analysis
export const fetchAIResults = async () => {
  const res = await axios.get(`${API_BASE_URL}/api/v1/ai/analysis`);
  return res.data;
};

// Fetch all generated synthetic data (GET)
export const fetchSyntheticData = async () => {
  const res = await axios.get(`${API_BASE_URL}/api/v1/ai/synthetic-data`);
  return res.data;
};

// POST endpoint to trigger backend synthesis. Follows provided request body structure.
// POST /api/v1/ai/synthetic-data
// Required request body:
// {
//    "record_count": <int>,
//    "data_type": <str>,    // e.g., "EHR", "CLAIMS", ...
//    "privacy_level": <str> // e.g., "high", "medium", "low"
// }
export const generateSyntheticData = async ({ record_count, data_type, privacy_level }) => {
  const res = await axios.post(
    `${API_BASE_URL}/api/v1/ai/synthetic-data`,
    {
      record_count,
      data_type,
      privacy_level
    }
  );
  // Assume API returns new entries or success indicator
  return res.data;
};
