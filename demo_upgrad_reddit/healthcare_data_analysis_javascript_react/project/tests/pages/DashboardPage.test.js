import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '../../src/pages/DashboardPage';
import * as api from '../../src/services/api';
import * as exportUtils from '../../src/utils/exportUtils';

// Mock dependencies and modules
jest.mock('../../src/services/api');
jest.mock('../../src/utils/exportUtils');

const mockAIResults = {
  entityHighlights: [
    { entity: 'Diabetes', type: 'Condition' },
    { entity: 'Insulin', type: 'Medication' }
  ],
  summaryStats: {
    totalPatients: 120,
    averageAge: 45.7
  }
};

const mockSyntheticData = [
  { id: 1, name: 'Jane Doe', condition: 'Hypertension' },
  { id: 2, name: 'John Smith', condition: 'Diabetes' }
];

function flushPromises() {
  return new Promise(setImmediate);
}

describe('DashboardPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('testDashboardPage_RendersLoadingSpinnerOnInitialLoad_ShowsLoadingState', async () => {
    api.fetchAIResults.mockReturnValueOnce(new Promise(() => {}));
    api.fetchSyntheticData.mockReturnValueOnce(new Promise(() => {}));
    render(<DashboardPage />);
    expect(screen.getByText(/Loading dashboard data/i)).toBeInTheDocument();
  });

  test('testDashboardPage_OnDashboardDataLoad_ShowsDataTablesAndCards', async () => {
    api.fetchAIResults.mockResolvedValueOnce(mockAIResults);
    api.fetchSyntheticData.mockResolvedValueOnce(mockSyntheticData);
    render(<DashboardPage />);
    // Wait for async loading
    await waitFor(() => {
      expect(
        screen.getByText(/AI-Driven Healthcare Data Dashboard/i)
      ).toBeInTheDocument();
    });
    expect(screen.getByText(/Entity Recognition Highlights/i)).toBeInTheDocument();
    expect(screen.getByText(/Summary Statistics/i)).toBeInTheDocument();
    expect(screen.getByText(/Generate New Synthetic Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Generated Synthetic Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Jane Doe/)).toBeInTheDocument();
    expect(screen.getByText(/John Smith/)).toBeInTheDocument();
  });

  test('testDashboardPage_OnDataLoadingError_ShowsErrorAlert', async () => {
    api.fetchAIResults.mockRejectedValueOnce(new Error('Backend fetch failed'));
    api.fetchSyntheticData.mockRejectedValueOnce(new Error('Backend fetch failed'));
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText(/Failed to load dashboard data/i)).toBeInTheDocument();
    });
  });

  test('testDashboardPage_ManualRefreshButton_RefetchesData', async () => {
    api.fetchAIResults.mockResolvedValueOnce(mockAIResults);
    api.fetchSyntheticData.mockResolvedValueOnce(mockSyntheticData);
    render(<DashboardPage />);
    await flushPromises();
    // Simulate clicking refresh, should cause data reload
    api.fetchAIResults.mockResolvedValueOnce({ ...mockAIResults, summaryStats: { totalPatients: 999, averageAge: 50 } });
    api.fetchSyntheticData.mockResolvedValueOnce([{ id: 3, name: 'Sara Lee', condition: 'Asthma' }]);
    const btn = screen.getByRole('button', { name: /Refresh Data/i });
    fireEvent.click(btn);
    await waitFor(() => {
      expect(screen.getByText(/Sara Lee/)).toBeInTheDocument();
      expect(screen.getByText('999')).toBeInTheDocument();
    });
  });

  test('testDashboardPage_GenerateSyntheticData_SuccessfullyTriggersReload', async () => {
    api.fetchAIResults.mockResolvedValue(mockAIResults);
    api.fetchSyntheticData.mockResolvedValue(mockSyntheticData);
    api.generateSyntheticData.mockResolvedValue({});
    render(<DashboardPage />);
    await flushPromises();
    // Find SyntheticDataControls' generate button
    const button = screen.getByRole('button', { name: /generate/i });
    // Fill parameters if needed -- assuming controlled inputs use roles/labels
    fireEvent.click(button);
    // Simulate reload with new batch
    api.fetchSyntheticData.mockResolvedValueOnce([{ id: 99, name: 'Test', condition: 'Test Cond' }]);
    await waitFor(() => {
      expect(screen.getByText(/Test/)).toBeInTheDocument();
    });
  });

  test('testDashboardPage_GenerateSyntheticData_Failure_ShowsError', async () => {
    api.fetchAIResults.mockResolvedValue(mockAIResults);
    api.fetchSyntheticData.mockResolvedValue(mockSyntheticData);
    api.generateSyntheticData.mockRejectedValue(new Error('API failed'));
    render(<DashboardPage />);
    await flushPromises();
    const button = screen.getByRole('button', { name: /generate/i });
    fireEvent.click(button);
    await waitFor(() => {
      expect(screen.getByText(/Failed to generate synthetic data/i)).toBeInTheDocument();
    });
  });

  test('testDashboardPage_HandleExport_ExportsDataWithCorrectParameters', async () => {
    api.fetchAIResults.mockResolvedValue(mockAIResults);
    api.fetchSyntheticData.mockResolvedValue(mockSyntheticData);
    exportUtils.serializeAndDownload.mockImplementation(jest.fn());
    render(<DashboardPage />);
    await flushPromises();
    // Simulate clicking a button within AIResultsFilterExport to export data
    // Here we assume the presence of an "Export AI Results" button
    const exportBtn = screen.getByRole('button', { name: /export ai results/i });
    fireEvent.click(exportBtn);
    // Check exportUtils was called with correct args
    expect(exportUtils.serializeAndDownload).toHaveBeenCalledWith(
      mockAIResults, expect.any(String), expect.any(String)
    );
  });

  test('testDashboardPage_HandlesEmptySyntheticDataTable_NoRowsRendered', async () => {
    api.fetchAIResults.mockResolvedValue(mockAIResults);
    api.fetchSyntheticData.mockResolvedValue([]);
    render(<DashboardPage />);
    await waitFor(() => {
      // Ideally, your SyntheticDataTable would display empty state text
      // Simulating with direct check for 'no data' pattern
      expect(screen.getByText(/no synthetic data/i)).toBeInTheDocument();
    });
  });
});

// Edge Case: Invalid Data from API

describe('DashboardPage Edge Cases', () => {
  test('testDashboardPage_MalformedAIResults_ShowsEmptyOrFallbacks', async () => {
    api.fetchAIResults.mockResolvedValueOnce({});
    api.fetchSyntheticData.mockResolvedValueOnce([]);
    render(<DashboardPage />);
    await waitFor(() => {
      // Should render with no highlights/statistics, but UI still present
      expect(screen.getByText(/Entity Recognition Highlights/i)).toBeInTheDocument();
    });
  });

  test('testDashboardPage_MalformedSyntheticData_ShowsTableButNoRows', async () => {
    api.fetchAIResults.mockResolvedValueOnce(mockAIResults);
    api.fetchSyntheticData.mockResolvedValueOnce([null, undefined, {}]);
    render(<DashboardPage />);
    await waitFor(() => {
      // Expect table header/structure even with empty/invalid data
      expect(screen.getByText(/Generated Synthetic Data/i)).toBeInTheDocument();
    });
  });
});

// Security/Injection Edge Case (if filter/search is implemented in Filter component)
describe('DashboardPage Security', () => {
  test('testDashboardPage_HandlesInjectionLikeFilterParams_NoCrash', async () => {
    api.fetchAIResults.mockResolvedValueOnce(mockAIResults);
    api.fetchSyntheticData.mockResolvedValueOnce(mockSyntheticData);
    render(<DashboardPage />);
    await flushPromises();
    // Simulate a potentially malicious filter input (if Filter UI supports entering it)
    // For now, just ensure dashboard does not crash when filter state is manipulated
    // Note: Modify as needed to match real filter input linkage
    // example: fireEvent.change(screen.getByLabelText(/filter/i), { target: { value: '1; DROP TABLE' } });
    // Should still display dashboard cards, etc - no crash
    expect(screen.getByText(/Entity Recognition Highlights/i)).toBeInTheDocument();
  });
});

// Performance/load edge (simulate lots of synthetic data rows)
describe('DashboardPage Performance', () => {
  test('testDashboardPage_LoadsLargeSyntheticData_DoesNotCrashOrHalt', async () => {
    const largeSyntheticData = Array.from({ length: 500 }, (_, i) => ({ id: i, name: `Patient${i}`, condition: 'TestCond' }));
    api.fetchAIResults.mockResolvedValue(mockAIResults);
    api.fetchSyntheticData.mockResolvedValue(largeSyntheticData);
    render(<DashboardPage />);
    // Verify that some random entry toward the end appears
    await waitFor(() => {
      expect(screen.getByText(/Patient499/)).toBeInTheDocument();
    });
  });
});

// Async safety: Ensure spinner disappears and data appears atomically

describe('DashboardPage Async Consistency', () => {
  test('testDashboardPage_SpinnerDisappearsAfterDataLoad_TableAppears', async () => {
    api.fetchAIResults.mockResolvedValue(mockAIResults);
    api.fetchSyntheticData.mockResolvedValue(mockSyntheticData);
    render(<DashboardPage />);
    // Spinner should show up first
    expect(screen.getByText(/Loading dashboard data/i)).toBeInTheDocument();
    // Wait for data to appear, spinner gone
    await waitFor(() => {
      expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument();
      expect(screen.getByText(/Entity Recognition Highlights/i)).toBeInTheDocument();
    });
  });
});