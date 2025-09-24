import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { fetchAIResults, fetchSyntheticData } from './api';

// services/api.test.js
// Tests for api.js service module (API calls for AI analysis and synthetic data)

// Arrange: axios and axios-mock-adapter imports
// API functions imported from api.js

// Setup for Jest
// We use axios-mock-adapter to stub axios requests

describe('API Service Tests', () => {
  let mock;
  const API_BASE_URL = 'https://api.example.com';

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  describe('fetchAIResults', () => {
    it('should return AI analysis data for a successful API call', async () => {
      // Arrange
      const expectedData = { highlights: [{ entity: 'TestEntity' }], summaryStats: { total: 42 } };
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(200, expectedData);
      // Act
      const result = await fetchAIResults();
      // Assert
      expect(result).toEqual(expectedData);
    });

    it('should throw an error when API returns a network error', async () => {
      // Arrange
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).networkError();
      // Act & Assert
      await expect(fetchAIResults()).rejects.toThrow();
    });

    it('should throw an error when API returns HTTP error status', async () => {
      // Arrange
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(500);
      // Act & Assert
      await expect(fetchAIResults()).rejects.toThrow();
    });

    it('should handle empty response gracefully', async () => {
      // Arrange
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(200, {});
      const result = await fetchAIResults();
      expect(result).toEqual({});
    });
  });

  describe('fetchSyntheticData', () => {
    it('should return synthetic data for a successful API call', async () => {
      // Arrange
      const syntheticSample = [
        { id: 1, value: 'foo' },
        { id: 2, value: 'bar' }
      ];
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, syntheticSample);
      // Act
      const result = await fetchSyntheticData();
      // Assert
      expect(result).toEqual(syntheticSample);
    });

    it('should throw an error when API returns HTTP 404 error', async () => {
      // Arrange
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(404);
      // Act & Assert
      await expect(fetchSyntheticData()).rejects.toThrow();
    });

    it('should throw an error on network timeout', async () => {
      // Arrange
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).timeout();
      // Act & Assert
      await expect(fetchSyntheticData()).rejects.toThrow();
    });

    it('should handle empty list response gracefully', async () => {
      // Arrange
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, []);
      // Act
      const result = await fetchSyntheticData();
      // Assert
      expect(result).toEqual([]);
    });
  });

  // Parameterized tests for both endpoints (integration)
  describe.each([
    {
      fnName: 'fetchAIResults',
      apiMethod: fetchAIResults,
      url: `${API_BASE_URL}/api/v1/ai/analysis`,
      sampleResp: { highlights: [], summaryStats: { total: 0 } }
    },
    {
      fnName: 'fetchSyntheticData',
      apiMethod: fetchSyntheticData,
      url: `${API_BASE_URL}/api/v1/ai/synthetic-data`,
      sampleResp: [ { id: 1, value: 'sample' } ]
    }
  ])('$fnName integration scenarios', ({ fnName, apiMethod, url, sampleResp }) => {
    it('should return correct response body on success', async () => {
      mock.onGet(url).reply(200, sampleResp);
      const resp = await apiMethod();
      expect(resp).toEqual(sampleResp);
    });
    it('should throw for 400+ error codes', async () => {
      mock.onGet(url).reply(400);
      await expect(apiMethod()).rejects.toThrow();
    });
  });

  // Security test: Ensure that endpoint cannot be attacked by malformed URLs
  // (In this API implementation, since only valid URLs are called internally and no user input in the URL, direct injection attacks are not a concern.)
  // This is more applicable for API clients with dynamic URL generation.

  // Performance: Not applicable at unit test level (covered by e2e/load tests).
});

// Note: These tests thoroughly cover all code paths including success, HTTP/server error, network failure, and edge cases
// All functions are tested in isolation (mocking network), following Jest/JavaScript best practices