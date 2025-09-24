import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SyntheticDataTable from '../SyntheticDataTable';

// Unit tests for SyntheticDataTable React component
// Arrange-Act-Assert (AAA) pattern followed

describe('SyntheticDataTable', () => {
  // Test: should render the no data message when data prop is undefined
  it('should display no data message when data is undefined', () => {
    render(<SyntheticDataTable data={undefined} />);
    expect(screen.getByText('No synthetic data generated.')).toBeInTheDocument();
  });

  // Test: should render the no data message when data prop is empty array
  it('should display no data message when data is an empty array', () => {
    render(<SyntheticDataTable data={[]} />);
    expect(screen.getByText('No synthetic data generated.')).toBeInTheDocument();
  });

  // Test: should render table headers and rows correctly for typical data
  it('should render a table with correct headers and rows for provided data', () => {
    const sampleData = [
      { id: 1, foo: 'alpha', bar: 'beta' },
      { id: 2, foo: 'gamma', bar: 'delta' },
    ];
    render(<SyntheticDataTable data={sampleData} />);
    // Headers: id, foo, bar (column names as in data)
    expect(screen.getByText('id')).toBeInTheDocument();
    expect(screen.getByText('foo')).toBeInTheDocument();
    expect(screen.getByText('bar')).toBeInTheDocument();
    // Row values
    expect(screen.getByText('alpha')).toBeInTheDocument();
    expect(screen.getByText('beta')).toBeInTheDocument();
    expect(screen.getByText('gamma')).toBeInTheDocument();
    expect(screen.getByText('delta')).toBeInTheDocument();
  });

  // Test: should use column names with space for camelCase property names
  it('should render table headers with spaces for camelCase column names', () => {
    const dataWithCamelCase = [
      { syntheticId: 1, someValue: 'a', anotherThing: 'b' },
    ];
    render(<SyntheticDataTable data={dataWithCamelCase} />);
    // syntheticId -> 'synthetic Id', someValue -> 'some Value', anotherThing -> 'another Thing'
    expect(screen.getByText('synthetic Id')).toBeInTheDocument();
    expect(screen.getByText('some Value')).toBeInTheDocument();
    expect(screen.getByText('another Thing')).toBeInTheDocument();
  });

  // Edge Case: all fields falsy/empty
  it('should correctly render when data fields are empty or null', () => {
    const emptyFields = [{foo: '', bar: null}];
    render(<SyntheticDataTable data={emptyFields} />);
    // Table with one row, two columns
    const tableCells = screen.getAllByRole('cell');
    expect(tableCells.length).toBe(2);
    // Empty string and blank cell
    expect(tableCells[0].textContent).toBe('');
    expect(tableCells[1].textContent).toBe(''); // null renders as blank
  });

  // Error scenario: data with missing fields in some rows
  it('should render undefined values as blank if fields are missing in some rows', () => {
    const inconsistentData = [
      { a: 1, b: 2 },
      { a: 3 },
      { b: 4 }
    ];
    render(<SyntheticDataTable data={inconsistentData} />);
    // Table has 3 rows, columns: a and b
    const rows = screen.getAllByRole('row');
    // Header row + 3 data rows
    expect(rows.length).toBe(4);
    // Row with only a defined
    const cellsRow2 = rows[2].querySelectorAll('td');
    expect(cellsRow2.length).toBe(2);
    expect(cellsRow2[0].textContent).toBe('3'); // a
    expect(cellsRow2[1].textContent).toBe('');  // b is missing
  });

  // Performance: test rendering large dataset (spot check)
  it('should render table efficiently for large datasets (1000 rows)', () => {
    // Generate test data
    const largeData = Array.from({length: 1000}, (_, i) => ({ id: i, value: `row${i}` }));
    render(<SyntheticDataTable data={largeData} />);
    // Spot check that first and last row values are present
    expect(screen.getByText('row0')).toBeInTheDocument();
    expect(screen.getByText('row999')).toBeInTheDocument();
    // Total row count: header row + 1000
    const allRenderedRows = screen.getAllByRole('row');
    expect(allRenderedRows.length).toBe(1001);
  });

  // Security: test input escaping (no XSS injection in table)
  it('should not render raw HTML, protecting against HTML injection attacks', () => {
    const xssData = [{ dangerous: '<script>window.evil=true;</script>' }];
    render(<SyntheticDataTable data={xssData} />);
    // The script tag should be rendered as text, not executed
    expect(screen.getByText('<script>window.evil=true;</script>')).toBeInTheDocument();
    // Check that evil global variable is not set (script not executed)
    expect(window.evil).toBeUndefined();
  });
});