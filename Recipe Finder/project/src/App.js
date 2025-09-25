// src/App.js
// Refined, responsive minimal version: ensures visual hierarchy, non-overlapping states, and clear navigation
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchBar from './components/SearchBar';
import ResultsPage from './pages/ResultsPage';
import { fetchRecipesByIngredients } from './services/api';
import { LoadingIndicator, ErrorMessage } from './components/Feedback';
import './App.css';

// Home/Search page logic (no clutter, fully responsive)
function SearchPage({
  onSearch,
  inputValue,
  onInputChange,
  disabled,
  inputError
}) {
  return (
    <div className="container p-4" style={{ maxWidth: 640 }}>
      <h1 className="mb-4 text-center">Recipe Finder</h1>
      <p className="text-center mb-3 text-muted" style={{fontSize:'1.09rem',lineHeight:'1.38'}}>Enter ingredients (comma-separated) to discover easy recipes you can make.</p>
      <SearchBar
        value={inputValue}
        onChange={onInputChange}
        onSubmit={onSearch}
        disabled={disabled}
      />
      {inputError && (<ErrorMessage error={inputError} />)}
    </div>
  );
}

function App() {
  // Core state and feedback/flow logic
  const [searchValue, setSearchValue] = useState('');
  const [searchedIngredients, setSearchedIngredients] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [uiState, setUiState] = useState('idle'); // idle | loading | error
  const [errorMsg, setErrorMsg] = useState('');

  // Ensures only one feedback state at a time (either loading, error, or normal)
  const handleSearch = async () => {
    const ingredientsArr = searchValue
      .split(',')
      .map(i => i.trim())
      .filter(i => i.length > 0);
    if (ingredientsArr.length === 0) {
      setUiState('error');
      setErrorMsg('Please enter at least one ingredient.');
      setRecipes([]);
      return;
    }
    setUiState('loading');
    setErrorMsg('');
    setRecipes([]);
    setSearchedIngredients(ingredientsArr.join(', '));
    try {
      const data = await fetchRecipesByIngredients(ingredientsArr);
      setRecipes(data.hits || []);
      setUiState('idle');
    } catch (error) {
      let msg = 'An error occurred fetching recipes.';
      if (error.response && error.response.status === 401) {
        msg = 'API authentication failed. Please check your credentials.';
      } else if (error.response && error.response.data && error.response.data.message) {
        msg = `API Error: ${error.response.data.message}`;
      } else if (error.message) {
        msg = error.message;
      }
      setErrorMsg(msg);
      setUiState('error');
      setRecipes([]);
    }
  };

  // Retry resets to idle/input
  const handleRetry = () => {
    setUiState('idle');
    setErrorMsg('');
  };

  return (
    <Router>
      <main className="bg-light min-vh-100 d-flex flex-column align-items-center pt-4">
        <Routes>
          <Route
            path="/"
            element={
              <div className="w-100">
                {uiState === 'idle' && (
                  <>
                    <SearchPage
                      onSearch={handleSearch}
                      inputValue={searchValue}
                      onInputChange={setSearchValue}
                      disabled={uiState === 'loading'}
                      inputError={''}
                    />
                    {(recipes.length > 0 || (searchedIngredients && recipes.length === 0)) && (
                      <section className="container mt-4" style={{ maxWidth: 960 }}>
                        <h2 className="mb-3 text-center" style={{fontWeight:600}}>
                          Results{searchedIngredients ? ` for "${searchedIngredients}"` : ''}
                        </h2>
                        <ResultsPage
                          recipes={recipes}
                          loading={false}
                          error={''}
                          searchedIngredients={searchedIngredients}
                        />
                      </section>
                    )}
                  </>
                )}
                {uiState === 'loading' && (
                  <LoadingIndicator message="Fetching recipes..." />
                )}
                {uiState === 'error' && (
                  <div className="container p-4" style={{ maxWidth: 640 }}>
                    <ErrorMessage error={errorMsg} onRetry={handleRetry} />
                    <SearchBar
                      value={searchValue}
                      onChange={setSearchValue}
                      onSubmit={handleSearch}
                      disabled={false}
                    />
                  </div>
                )}
              </div>
            }
          />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
