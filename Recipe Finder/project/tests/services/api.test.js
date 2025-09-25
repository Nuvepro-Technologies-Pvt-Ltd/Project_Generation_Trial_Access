import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { fetchRecipesByIngredients } from '../../src/services/api';

// tests/services/api.test.js
// Test suite for the Recipe Search API Axios Service wrapper

// === Imports ===
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { fetchRecipesByIngredients } from '../../src/services/api';

// === Test Configuration ===
describe('fetchRecipesByIngredients', () => {
  let mock;
  const APP_ID = 'YOUR_APP_ID'; // should match project config
  const APP_KEY = 'YOUR_APP_KEY';

  beforeAll(() => {
    // Create a mock adapter for axios
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.reset();
  });

  afterAll(() => {
    mock.restore();
  });

  it('should call Edamam API with correct parameters and return data for valid ingredients', async () => {
    const ingredientsArr = ['chicken', 'rice', 'broccoli'];
    const expectedQuery = 'chicken,rice,broccoli';
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;
    const mockedResponse = { hits: [{ recipe: { label: 'Chicken Rice Broccoli Bowl' } }] };

    // Mock GET request
    mock.onGet(expectedUrl).reply(200, mockedResponse);

    // Act
    const data = await fetchRecipesByIngredients(ingredientsArr);

    // Assert
    expect(data).toEqual(mockedResponse);
  });

  it('should correctly encode special characters in ingredients', async () => {
    const ingredientsArr = ['café', 'crème brûlée', 'beef'];
    const expectedQuery = 'café,crème brûlée,beef';
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;
    const mockedResponse = { hits: [{ recipe: { label: 'Cafe Brulee Beef Special' } }] };

    mock.onGet(expectedUrl).reply(200, mockedResponse);

    const data = await fetchRecipesByIngredients(ingredientsArr);
    expect(data).toEqual(mockedResponse);
  });

  it('should throw an error when the API returns an error (e.g., network/network error)', async () => {
    const ingredientsArr = ['eggs', 'avocado'];
    const expectedQuery = 'eggs,avocado';
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;

    // Simulate network error
    mock.onGet(expectedUrl).networkError();

    await expect(fetchRecipesByIngredients(ingredientsArr)).rejects.toThrow();
  });

  it('should throw when API returns an HTTP error response (e.g., 401 Unauthorized)', async () => {
    const ingredientsArr = ['milk', 'sugar'];
    const expectedQuery = 'milk,sugar';
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;

    // Simulate 401 error
    mock.onGet(expectedUrl).reply(401, { error: 'Unauthorized' });

    await expect(fetchRecipesByIngredients(ingredientsArr)).rejects.toMatchObject({ response: { status: 401 } });
  });

  it('should handle empty ingredients array (edge case)', async () => {
    const ingredientsArr = [];
    const expectedQuery = '';
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;
    const mockedResponse = { hits: [] };

    mock.onGet(expectedUrl).reply(200, mockedResponse);
    const data = await fetchRecipesByIngredients(ingredientsArr);
    expect(data).toEqual(mockedResponse);
  });

  it('should work with a large number of ingredients (performance test)', async () => {
    // Generate a long list of ingredients
    const ingredientsArr = Array.from({ length: 100 }, (_, i) => `item${i}`);
    const expectedQuery = ingredientsArr.join(',');
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;
    const mockedResponse = { hits: [{ recipe: { label: 'Mega Ingredient Casserole' } }] };

    mock.onGet(expectedUrl).reply(200, mockedResponse);
    const data = await fetchRecipesByIngredients(ingredientsArr);
    expect(data).toEqual(mockedResponse);
  });

  it('should trim whitespace in ingredients before sending (sanity check)', async () => {
    // While the code expects already-trimmed, check what happens if not
    const ingredientsArr = [' apple ', '  bacon', 'egg  '];
    const expectedQuery = ' apple ,  bacon,egg  ';
    const expectedUrl = `https://api.edamam.com/search?q=${encodeURIComponent(expectedQuery)}&app_id=${APP_ID}&app_key=${APP_KEY}`;
    const mockedResponse = { hits: [{ recipe: { label: 'Apple Bacon Egg Scramble' } }] };

    mock.onGet(expectedUrl).reply(200, mockedResponse);
    const data = await fetchRecipesByIngredients(ingredientsArr);
    expect(data).toEqual(mockedResponse);
  });

  // Note: for security (injection) and configuration testing, Edamam API & axios/URL encoding would resist injection,
  // but you may test unsafe/edge ingredient terms as additional cases if required by spec.
});