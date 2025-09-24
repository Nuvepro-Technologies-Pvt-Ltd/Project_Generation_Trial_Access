import axios from 'axios';
import * as api from '../api';
import {jest} from '@jest/globals'

// __tests__/api.test.js
// Comprehensive test suite for services/api.js using Jest
// Tests all API functions include success, error, and edge cases, with axios mocking.

// Mock axios
jest.mock('axios');

const mockAIResultsData = {
  highlights: ['entity1', 'entity2'],
  summaryStats: {count: 2, total: 100}
};

const mockSyntheticData = [
  {id: 1, value: 'synthetic1'},
  {id: 2, value: 'synthetic2'}
];

const API_BASE_URL = 'https://api.example.com';

describe('api.js', () => {
  afterEach(() => {
    jest.clearAllMocks(); // Reset mocks after each test
  });

  describe('fetchAIResults', () => {
    it('should fetch AI analysis results and return data on success', async () => {
      axios.get.mockResolvedValueOnce({ data: mockAIResultsData });
      const data = await api.fetchAIResults();
      expect(axios.get).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/ai/analysis`);
      expect(data).toEqual(mockAIResultsData);
    });

    it('should throw an error when axios.get fails', async () => {
      const errorObj = new Error('Network Error');
      axios.get.mockRejectedValueOnce(errorObj);
      await expect(api.fetchAIResults()).rejects.toThrow('Network Error');
    });

    it('should handle empty response gracefully', async () => {
      axios.get.mockResolvedValueOnce({ data: {} });
      const data = await api.fetchAIResults();
      expect(data).toEqual({});
    });

    it('should handle null response data', async () => {
      axios.get.mockResolvedValueOnce({ data: null });
      const data = await api.fetchAIResults();
      expect(data).toBeNull();
    });
  });

  describe('fetchSyntheticData', () => {
    it('should fetch synthetic data entries and return data on success', async () => {
      axios.get.mockResolvedValueOnce({ data: mockSyntheticData });
      const data = await api.fetchSyntheticData();
      expect(axios.get).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/ai/synthetic-data`);
      expect(data).toEqual(mockSyntheticData);
    });

    it('should throw an error when axios.get fails', async () => {
      const errorObj = new Error('Timeout');
      axios.get.mockRejectedValueOnce(errorObj);
      await expect(api.fetchSyntheticData()).rejects.toThrow('Timeout');
    });

    it('should handle empty response (empty array)', async () => {
      axios.get.mockResolvedValueOnce({ data: [] });
      const data = await api.fetchSyntheticData();
      expect(Array.isArray(data)).toBe(true);
      expect(data.length).toBe(0);
    });

    it('should handle null response data', async () => {
      axios.get.mockResolvedValueOnce({ data: null });
      const data = await api.fetchSyntheticData();
      expect(data).toBeNull();
    });
  });

  // Edge/invalid scenario: Unexpected data format
  describe('fetchAIResults - unexpected data format', () => {
    it('should handle when API returns string instead of expected object', async () => {
      axios.get.mockResolvedValueOnce({ data: "unexpected string" });
      const data = await api.fetchAIResults();
      expect(data).toBe('unexpected string');
    });
  });

  describe('fetchSyntheticData - unexpected data format', () => {
    it('should handle when API returns object instead of expected array', async () => {
      const unexpectedFormat = { items: [] };
      axios.get.mockResolvedValueOnce({ data: unexpectedFormat });
      const data = await api.fetchSyntheticData();
      expect(data).toEqual(unexpectedFormat);
    });
  });
});

// Performance & security considerations cannot be directly tested here as the module only wraps GET requests with axios. Security (injection etc.) would be addressed at the API/server.