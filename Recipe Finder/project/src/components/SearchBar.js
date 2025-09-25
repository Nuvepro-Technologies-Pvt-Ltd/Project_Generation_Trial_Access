// src/components/SearchBar.js
// Minimal, large touch-area search bar for ingredients; visually aligned and accessible
import React from 'react';

function SearchBar({ value, onChange, onSubmit, disabled }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!disabled && value.trim() !== '') {
      onSubmit();
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="d-flex flex-wrap gap-2 justify-content-center align-items-center"
      aria-label="Ingredient Search"
      autoComplete="off"
      style={{ marginBottom: 0 }}
    >
      <label htmlFor="ingredients-input" className="visually-hidden">
        Ingredients
      </label>
      <input
        id="ingredients-input"
        type="text"
        className="form-control form-control-lg"
        style={{ minWidth: 220, maxWidth: 380 }}
        placeholder="Enter ingredients, separated by commas"
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        aria-label="Ingredients"
        autoFocus
      />
      <button
        type="submit"
        className="btn btn-primary btn-lg px-4"
        disabled={disabled || value.trim() === ''}
        aria-label="Search Recipes"
        style={{ fontWeight: 500 }}
      >
        Search
      </button>
    </form>
  );
}

export default SearchBar;
