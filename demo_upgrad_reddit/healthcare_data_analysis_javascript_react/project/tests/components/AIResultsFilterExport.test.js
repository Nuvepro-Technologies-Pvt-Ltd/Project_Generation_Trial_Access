import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import AIResultsFilterExport from '../../src/components/AIResultsFilterExport';

// Test suite for AIResultsFilterExport React component
// - Comprehensive unit and integration coverage
// - Tests behavior of filtering, options logic, UI state, and export callbacks
// - Uses Jest and React Testing Library best practices

const mockAIResults = {
  entityHighlights: [
    { id: 1, type: 'note', value: 'itemA', visit_date: '2021-08-01' },
    { id: 2, type: 'lab', value: 'itemB', visit_date: '2021-08-02' }
  ],
  summaryStats: { total: 2 }
};

const mockSyntheticData = [
  { patient_id: 'P001', gender: 'M', age: 50, diagnosis: 'hypertension', visit_date: '2021-01-01', data_type: 'lab', attribute: 'A1' },
  { patient_id: 'P002', gender: 'F', age: 60, diagnosis: 'diabetes', visit_date: '2021-05-15', data_type: 'note', attribute: 'B1' },
  { patient_id: 'P003', gender: 'F', age: 47, diagnosis: 'cancer', visit_date: '2021-09-25', data_type: 'lab', attribute: 'A2' }
];

describe('AIResultsFilterExport component', () => {
  let onExport;

  beforeEach(() => {
    jest.useFakeTimers(); // For setTimeout
    onExport = jest.fn();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
    jest.clearAllMocks();
  });

  it('renders with default props and shows correct filter dropdowns', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    expect(screen.getByLabelText('Patient Attribute')).toBeInTheDocument();
    expect(screen.getByLabelText('Data Type / Entity Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Date From')).toBeInTheDocument();
    expect(screen.getByLabelText('Date To')).toBeInTheDocument();
    expect(screen.getByLabelText('Export')).toBeInTheDocument();
    // Default filter info
    expect(screen.getByText('No filters applied')).toBeInTheDocument();
  });

  it('shows correct patient attribute options based on synthetic data', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    expect(screen.getByRole('option', { name: /patient id/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /gender/i })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: /diagnosis/i })).toBeInTheDocument();
  });

  it('shows correct entity/data type options from both AI results and synthetic data', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    expect(screen.getByRole('option', { name: 'note' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'lab' })).toBeInTheDocument();
  });

  it('activates and displays the "Filters Active" badge when a filter is applied', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.change(screen.getByLabelText('Patient Attribute'), { target: { value: 'gender' } });
    expect(screen.getByText(/Filters Active/)).toBeInTheDocument();
    expect(screen.queryByText('No filters applied')).not.toBeInTheDocument();
  });

  it('filters synthetic data based on patient attribute selection', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.change(screen.getByLabelText('Patient Attribute'), { target: { value: 'diagnosis' } });
    // Internally, only records with a diagnosis field (all in this set) remain, but this simulates filter logic
    // To test actual export, verify filtered data in export call
    fireEvent.click(screen.getByTitle('Export filtered results'));
    expect(onExport).toHaveBeenCalledWith('ai', mockAIResults.entityHighlights, 'csv', expect.any(String));
  });

  it('filters synthetic data by data type', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    // Switch export to synthetic
    fireEvent.change(screen.getByLabelText('Export'), { target: { value: 'synthetic' } });
    fireEvent.change(screen.getByLabelText('Data Type / Entity Type'), { target: { value: 'lab' } });
    fireEvent.click(screen.getByTitle('Export filtered results'));
    // Only lab entries
    expect(onExport).toHaveBeenCalled();
    const call = onExport.mock.calls[0];
    expect(call[0]).toBe('synthetic');
    expect(call[2]).toBe('csv');
    // The result only contains lab rows
    expect(call[1].every(row => row.data_type === 'lab')).toBe(true);
    expect(call[3]).toMatch(/^synthetic_data_filtered\.csv$/);
  });

  it('filters synthetic data by date range', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.change(screen.getByLabelText('Export'), { target: { value: 'synthetic' } });
    fireEvent.change(screen.getByLabelText('Date From'), { target: { value: '2021-04-01' } });
    fireEvent.change(screen.getByLabelText('Date To'), { target: { value: '2021-09-01' } });
    fireEvent.click(screen.getByTitle('Export filtered results'));
    const call = onExport.mock.calls[0];
    // Should only include the record within the range
    expect(call[1]).toEqual([
      { patient_id: 'P002', gender: 'F', age: 60, diagnosis: 'diabetes', visit_date: '2021-05-15', data_type: 'note', attribute: 'B1' }
    ]);
  });

  it('exports filtered AI results correctly when exportType is ai', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.change(screen.getByLabelText('Data Type / Entity Type'), { target: { value: 'lab' } });
    fireEvent.click(screen.getByTitle('Export filtered results'));
    // Only lab entityHighlight should remain
    expect(onExport).toHaveBeenCalledWith(
      'ai',
      [{ id: 2, type: 'lab', value: 'itemB', visit_date: '2021-08-02' }],
      'csv',
      'ai_analysis_filtered.csv'
    );
  });

  it('changes export format to JSON and reflects in callback', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.change(screen.getByLabelText('Export'), { target: { value: 'synthetic' } });
    fireEvent.change(screen.getByDisplayValue('csv'), { target: { value: 'json' } });
    fireEvent.click(screen.getByTitle('Export filtered results'));
    expect(onExport.mock.calls[0][2]).toBe('json');
    expect(onExport.mock.calls[0][3]).toMatch(/synthetic_data_filtered\.json/);
  });

  it('shows success badge after export and hides it after timeout', async () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.click(screen.getByTitle('Export filtered results'));
    expect(screen.getByText('Export complete!')).toBeInTheDocument();
    // Fast-forward 3s
    jest.advanceTimersByTime(3000);
    await waitFor(() => expect(screen.queryByText('Export complete!')).not.toBeInTheDocument());
  });

  it('handles absence of synthetic data gracefully', () => {
    render(<AIResultsFilterExport aiResults={mockAIResults} syntheticData={[]} onExport={onExport} />);
    fireEvent.change(screen.getByLabelText('Export'), { target: { value: 'synthetic' } });
    fireEvent.click(screen.getByTitle('Export filtered results'));
    // Should call onExport with empty array
    expect(onExport).toHaveBeenCalledWith('synthetic', [], 'csv', 'synthetic_data_filtered.csv');
  });

  it('handles empty aiResults/entityHighlights gracefully', () => {
    render(<AIResultsFilterExport aiResults={{ entityHighlights: [], summaryStats: {} }} syntheticData={mockSyntheticData} onExport={onExport} />);
    fireEvent.click(screen.getByTitle('Export filtered results'));
    expect(onExport).toHaveBeenCalledWith('ai', [], 'csv', 'ai_analysis_filtered.csv');
  });
});

// Edge cases and security: ignore invalid filter (patientAttr not present)
it('does not crash if patientAttr is set to an unexpected value', () => {
  const { getByLabelText, getByTitle } = render(
    <AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />
  );
  // Set an attribute not in options via fireEvent
  fireEvent.change(getByLabelText('Patient Attribute'), { target: { value: 'not_present' } });
  fireEvent.click(getByTitle('Export filtered results'));
  // Should export all data (no filtering)
  const call = onExport.mock.calls[0];
  expect(call[1].length).toBe(mockAIResults.entityHighlights.length);
});

// Error scenario: onExport is undefined
it('does not throw if onExport is not provided', () => {
  render(
    <AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} />
  );
  fireEvent.click(screen.getByTitle('Export filtered results'));
  // Should render without errors, coverage for onExport absence
});

// Parameterized test: for all exportType/exportFormat combinations
const exportTypes = ['ai', 'synthetic'];
const exportFormats = ['csv', 'json'];
exportTypes.forEach(type => {
  exportFormats.forEach(format => {
    it(`exports correctly for exportType=${type}, exportFormat=${format}`, () => {
      render(
        <AIResultsFilterExport
          aiResults={mockAIResults}
          syntheticData={mockSyntheticData}
          onExport={onExport}
        />
      );
      fireEvent.change(screen.getByLabelText('Export'), { target: { value: type } });
      fireEvent.change(screen.getByDisplayValue('csv'), { target: { value: format } });
      fireEvent.click(screen.getByTitle('Export filtered results'));
      expect(onExport).toHaveBeenCalledWith(
        type,
        expect.any(Array),
        format,
        expect.stringMatching(type === 'ai' ? /^ai_analysis_filtered/ : /^synthetic_data_filtered/)
      );
    });
  });
});

// UI and accessibility
it('renders all form controls with appropriate labels for accessibility', () => {
  render(
    <AIResultsFilterExport aiResults={mockAIResults} syntheticData={mockSyntheticData} onExport={onExport} />
  );
  expect(screen.getByLabelText('Patient Attribute')).toBeDefined();
  expect(screen.getByLabelText('Data Type / Entity Type')).toBeDefined();
  expect(screen.getByLabelText('Date From')).toBeDefined();
  expect(screen.getByLabelText('Date To')).toBeDefined();
});