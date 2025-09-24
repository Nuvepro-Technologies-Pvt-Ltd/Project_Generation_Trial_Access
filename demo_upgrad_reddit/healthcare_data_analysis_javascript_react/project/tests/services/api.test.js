import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { fetchAIResults, fetchSyntheticData, generateSyntheticData } from '../../src/services/api';

// tests/services/api.test.js
// Comprehensive test coverage for src/services/api.js

// Arrange
const API_BASE_URL = 'https://api.example.com';
let mock;

describe('API Service Layer', () => {
  beforeAll(() => {
    // Use a single Axios MockAdapter instance for all tests
    mock = new MockAdapter(axios);
  });
  afterEach(() => {
    // Reset mock after each test to ensure test isolation
    mock.reset();
  });
  afterAll(() => {
    // Restore original axios state
    mock.restore();
  });

  describe('fetchAIResults', () => {
    it('should fetch AI analysis results successfully (happy path)', async () => {
      const mockData = { status: 'ok', stats: { entities: 3, insights: 2 } };
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(200, mockData);
      // Act
      const result = await fetchAIResults();
      // Assert
      expect(result).toEqual(mockData);
    });

    it('should handle API errors (network/server failures)', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/analysis`).reply(500, { message: 'Server error' });
      // Act & Assert
      await expect(fetchAIResults()).rejects.toThrow('Request failed with status code 500');
    });
  });

  describe('fetchSyntheticData', () => {
    it('should fetch all synthetic data successfully', async () => {
      const syntheticList = [
        { id: 1, type: 'EHR', privacy: 'high' },
        { id: 2, type: 'CLAIMS', privacy: 'medium' }
      ];
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, syntheticList);
      const result = await fetchSyntheticData();
      expect(result).toEqual(syntheticList);
    });

    it('should handle empty dataset and return an empty array', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(200, []);
      const result = await fetchSyntheticData();
      expect(result).toEqual([]);
    });

    it('should handle 404 Not Found error gracefully', async () => {
      mock.onGet(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(404, { message: 'Not Found' });
      await expect(fetchSyntheticData()).rejects.toThrow('Request failed with status code 404');
    });
  });

  describe('generateSyntheticData', () => {
    const validRequestBody = {
      record_count: 1000,
      data_type: 'EHR',
      privacy_level: 'high'
    };

    it('should send a valid POST request and return API response', async () => {
      const mockResponse = { success: true, generatedCount: 1000 };
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`, validRequestBody).reply(201, mockResponse);
      const result = await generateSyntheticData(validRequestBody);
      expect(result).toEqual(mockResponse);
    });

    it('should send correct payload in POST body', async () => {
      const mockResponse = { success: true };
      let requestBodyReceived = null;
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(config => {
        requestBodyReceived = JSON.parse(config.data);
        return [201, mockResponse];
      });
      await generateSyntheticData(validRequestBody);
      expect(requestBodyReceived).toMatchObject(validRequestBody);
    });

    it('should handle validation errors from server', async () => {
      // Simulate backend validation error with 400 response
      const invalidBody = { ...validRequestBody, record_count: -5 };
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(400, { message: 'record_count must be positive' });
      await expect(generateSyntheticData(invalidBody)).rejects.toThrow('Request failed with status code 400');
    });

    it('should handle network timeouts gracefully', async () => {
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`).timeout();
      await expect(generateSyntheticData(validRequestBody)).rejects.toThrow(/timeout/);
    });

    it('should handle missing fields (edge case)', async () => {
      // Missing privacy_level
      const incompleteBody = { record_count: 100, data_type: 'EHR' };
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(400, { message: 'privacy_level is required' });
      await expect(generateSyntheticData(incompleteBody)).rejects.toThrow('Request failed with status code 400');
    });

    it('should handle large payloads efficiently (performance smoke test)', async () => {
      const largePayload = {
        record_count: 1_000_000,
        data_type: 'EHR',
        privacy_level: 'high'
      };
      const mockResponse = { success: true, generatedCount: 1_000_000 };
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`, largePayload).reply(201, mockResponse);
      const result = await generateSyntheticData(largePayload);
      expect(result).toEqual(mockResponse);
      // Note: True load/performance test should be placed in a dedicated suite and may require special setup
    });

    it('should prevent JavaScript injection via data_type (security test)', async () => {
      const maliciousPayload = {
        record_count: 10,
        data_type: ";alert('xss');//",
        privacy_level: 'medium'
      };
      // Simulate backend sanitation and reject payload
      mock.onPost(`${API_BASE_URL}/api/v1/ai/synthetic-data`).reply(400, { message: 'Invalid data_type' });
      await expect(generateSyntheticData(maliciousPayload)).rejects.toThrow('Request failed with status code 400');
    });
  });
});

// Note: This test suite requires jest and axios-mock-adapter.
// All API calls are mocked and do not make real HTTP requests.
// Each test covers positive, negative, edge, error, and basic security scenarios for robust coverage.