import React from 'react';
import { render, screen } from '@testing-library/react';
import SyntheticDataTable from '../SyntheticDataTable';

// Test suite for SyntheticDataTable React component
// Framework: Jest + React Testing Library
// File location: components/__tests__/SyntheticDataTable.test.js

// Arrange-Act-Assert pattern is used for each test

describe('SyntheticDataTable', () => {
  
  it('should render "No synthetic data generated." when data is undefined', () => {
    // Arrange: Pass no data
    render(<SyntheticDataTable />);
    // Assert: Display no data message
    expect(screen.getByText(/no synthetic data generated./i)).toBeInTheDocument();
  });
  
  it('should render "No synthetic data generated." when data is an empty array', () => {
    render(<SyntheticDataTable data={[]} />);
    expect(screen.getByText(/no synthetic data generated./i)).toBeInTheDocument();
  });

  it('should render a table with correct columns and rows based on single data object', () => {
    const data = [
      { name: 'Alice', age: 30, role: 'Scientist' }
    ];
    render(<SyntheticDataTable data={data} />);
    // Assert columns
    expect(screen.getByText('name')).toBeInTheDocument();
    expect(screen.getByText('age')).toBeInTheDocument();
    expect(screen.getByText('role')).toBeInTheDocument();
    // Assert values
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('30')).toBeInTheDocument();
    expect(screen.getByText('Scientist')).toBeInTheDocument();
  });

  it('should render a table with correct columns and rows for multiple data entries', () => {
    const data = [
      { name: 'Bob', age: 27, email: 'bob@example.com' },
      { name: 'Sue', age: 28, email: 'sue@example.com' }
    ];
    render(<SyntheticDataTable data={data} />);
    // Assert headers
    expect(screen.getByText('name')).toBeInTheDocument();
    expect(screen.getByText('age')).toBeInTheDocument();
    expect(screen.getByText('email')).toBeInTheDocument();
    // Assert rows
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('27')).toBeInTheDocument();
    expect(screen.getByText('bob@example.com')).toBeInTheDocument();
    expect(screen.getByText('Sue')).toBeInTheDocument();
    expect(screen.getByText('28')).toBeInTheDocument();
    expect(screen.getByText('sue@example.com')).toBeInTheDocument();
  });

  it('should handle column names with camelCase and separate words appropriately', () => {
    const data = [
      { generatedName: 'Ann', syntheticAge: 40 }
    ];
    render(<SyntheticDataTable data={data} />);
    // Assert the camelCase transformation in header
    expect(screen.getByText('generated Name')).toBeInTheDocument();
    expect(screen.getByText('synthetic Age')).toBeInTheDocument();
  });

  it('should not throw if data contains undefined/null values', () => {
    const data = [
      { name: 'Carla', info: null },
      { name: undefined, info: 'test' }
    ];
    expect(() => render(<SyntheticDataTable data={data} />)).not.toThrow();
    // Null/undefined cell should render as blank
    expect(screen.getByText('Carla')).toBeInTheDocument();
    expect(screen.getByText('test')).toBeInTheDocument();
    // Cells with undefined or null render as empty cells, not throwing errors
    const cells = screen.getAllByRole('cell');
    expect(cells).toHaveLength(4);
  });

  it('should have table-responsive and correct Table classes for styling', () => {
    const data = [{ hello: 'world' }];
    const { container } = render(<SyntheticDataTable data={data} />);
    // Check for top-level div with class
    expect(container.querySelector('.table-responsive')).toBeInTheDocument();
    // Check for Table classNames
    const table = container.querySelector('table');
    expect(table).toHaveClass('table-striped');
    expect(table).toHaveClass('table-bordered');
    expect(table).toHaveClass('table-hover');
    expect(table).toHaveClass('table-sm');
  });

  it('should derive columns from first row only and ignore additional fields in other rows', () => {
    // Edge case: second row contains extra key
    const data = [
      { a: 1, b: 2 },
      { a: 3, b: 4, c: 5 }, // field 'c' should not have a column
    ];
    render(<SyntheticDataTable data={data} />);
    // Should only have columns 'a' and 'b'
    expect(screen.getByText('a')).toBeInTheDocument();
    expect(screen.getByText('b')).toBeInTheDocument();
    expect(screen.queryByText('c')).not.toBeInTheDocument();
    // All data rendered
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  // Additional error handling & edge case
  it('should render an empty cell for missing field in a row', () => {
    // Row is missing the 'b' field
    const data = [ {a: 'x', b: 'y'}, {a: 'p'} ];
    render(<SyntheticDataTable data={data} />);
    const rows = screen.getAllByRole('row');
    // 1 header + 2 rows
    expect(rows).toHaveLength(3);
    // The cell in the second data row for 'b' should be blank
    const blankCell = rows[2].querySelectorAll('td')[1];
    expect(blankCell.textContent).toBe("");
  });

});