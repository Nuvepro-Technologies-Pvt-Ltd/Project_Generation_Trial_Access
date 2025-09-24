import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { fetchAIResults, fetchSyntheticData } from '../api';

// src/services/__tests__/api.test.js
// Unit and integration tests for src/services/api.js
// Framework: Jest, mocks: axios-mock-adapter

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { fetchAIResults, fetchSyntheticData } from '../api';

describe('API Service Integration (api.js)', () => {
  let mock;
  const API_BASE_URL = 'https://api.example.com';

  beforeAll(() => {
    // Use a shared axios-mock-adapter instance for all tests
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    // Reset history and handlers after each test for isolation
    mock.reset();
  });

  afterAll(() => {
    // Clean up any mocked resources
    mock.restore();
  });

  describe('fetchAIResults', () => {
    it('should return data when server responds with 200 and valid payload', async () => {
      const mockData = {
        summary: 'Extraction Complete',
        entities: [
          { type: 'PERSON', text: 'Alice', relevance: 0.98 },
          { type: 'ORG', text: 'OpenAI', relevance: 0.95 }
        ],
        stats: { count: 2 }
      };
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(200, mockData);
      const result = await fetchAIResults();
      expect(result).toEqual(mockData);
    });

    it('should throw when server responds with 500 error', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(500, { error: 'Internal server error' });
      await expect(fetchAIResults()).rejects.toThrow();
    });

    it('should propagate axios network error', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).networkError();
      await expect(fetchAIResults()).rejects.toThrow(/Network Error/);
    });

    it('should handle empty payload gracefully', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(200, {});
      const result = await fetchAIResults();
      // Accepts empty object if returned by backend
      expect(result).toEqual({});
    });
  });

  describe('fetchSyntheticData', () => {
    it('should return synthetic samples when server responds with 200', async () => {
      const mockData = [
        { id: 1, synthetic: true, fields: { name: 'Bob', age: 30 } },
        { id: 2, synthetic: true, fields: { name: 'Carol', age: 25 } }
      ];
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, mockData);
      const result = await fetchSyntheticData();
      expect(result).toEqual(mockData);
    });

    it('should throw if server times out', async () => {
      // Simulate timeout (Timeout by axios-mock-adapter means no response after certain ms)
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).timeout();
      await expect(fetchSyntheticData()).rejects.toThrow(/timeout/);
    });

    it('should throw on 401 Unauthorized error', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(401, { message: 'Unauthorized' });
      await expect(fetchSyntheticData()).rejects.toThrow();
    });

    it('should handle empty array case', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, []);
      const result = await fetchSyntheticData();
      expect(result).toEqual([]);
    });
  });

  describe('Endpoint Integration', () => {
    it('should hit correct URL for AI Results API', async () => {
      mock.onGet().reply(config => {
        // Ensure the request URL matches expectation
        expect(config.url).toBe(`${API_BASE_URL}/api/v1/ai/analysis`);
        return [200, { ok: true }];
      });
      const data = await fetchAIResults();
      expect(data).toHaveProperty('ok', true);
    });

    it('should hit correct URL for Synthetic Data API', async () => {
      mock.onGet().reply(config => {
        expect(config.url).toBe(`${API_BASE_URL}/api/v1/ai/synthetic-data`);
        return [200, { ok: 'yes' }];
      });
      const data = await fetchSyntheticData();
      expect(data).toHaveProperty('ok', 'yes');
    });
  });

  // Example for performance/load test (demonstration only, not for production load)
  it('should handle multiple concurrent fetchSyntheticData requests', async () => {
    const payload = Array(3).fill({
      id: 123,
      synthetic: true,
      fields: { key: 'val' }
    });
    mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, payload);
    // Fire off multiple concurrent requests
    const results = await Promise.all([
      fetchSyntheticData(),
      fetchSyntheticData(),
      fetchSyntheticData()
    ]);
    for (const data of results) {
      expect(data).toEqual(payload);
    }
  });

  // Input validation / security smoke check
  it('should not allow injection or extra params in GET (security test)', async () => {
    // Since fetchAIResults and fetchSyntheticData do not take arguments, ensure invocations with extra params throw or ignore
    expect(() => fetchAIResults('UNEXPECTED')).toThrow();
    expect(() => fetchSyntheticData({ key: 'hack' })).toThrow();
  });
});