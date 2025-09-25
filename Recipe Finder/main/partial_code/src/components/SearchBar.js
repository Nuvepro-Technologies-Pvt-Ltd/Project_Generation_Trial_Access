// src/components/SearchBar.js
// Minimal, large touch-area search bar for ingredients; visually aligned and accessible
import React from 'react';

function SearchBar({ value, onChange, onSubmit, disabled }) {
  // Instructions:
  // - Implement the handleSubmit function to handle form submission.
  //   - It should prevent the default form action using e.preventDefault().
  //   - Check if the search bar is not disabled ('disabled' prop is false) and the 'value' prop (the input field's value) is not empty or only whitespace.
  //   - If conditions are met, trigger the 'onSubmit' callback to perform the search action.
  // - The component should return a form element with the following:
  //   - The form needs to have its onSubmit property set to your handleSubmit function.
  //   - The form should use accessibility attributes, classes for alignment, and prevent browser autocomplete.
  //   - Inside the form, include:
  //     - A visually hidden label for the input with htmlFor matching the input id.
  //     - An input field for entering ingredients:
  //         - Has id="ingredients-input", type="text", className="form-control form-control-lg".
  //         - style includes minWidth and maxWidth for responsiveness.
  //         - placeholder instructs users to enter ingredients separated by commas.
  //         - The value, onChange, and disabled props should be passed from the parent component.
  //         - aria-label for accessibility, and autoFocus to focus on mount.
  //     - A submit button:
  //         - Has type="submit", className="btn btn-primary btn-lg px-4".
  //         - Should be disabled if the search bar is disabled or input value is empty (after trimming spaces).
  //         - Accessible label provided with aria-label.
  //         - Text: 'Search'.
  // - Remember to export the SearchBar component as default at the end of the file.

  // Declare any functions or variables needed above this return statement, as described above.
}

export default SearchBar;
