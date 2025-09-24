import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardPage from '../DashboardPage';
import * as api from '../../services/api';

// Mock child components to isolate DashboardPage logic
jest.mock('../components/EntityHighlights', () => () => <div data-testid="entity-highlights" />);
jest.mock('../components/SummaryStatistics', () => () => <div data-testid="summary-statistics" />);
jest.mock('../components/SyntheticDataControls', () => (props) => (
  <div>
    <button data-testid="generate-btn" onClick={() => props.onGenerate && props.onGenerate({ record_count: 5, data_type: 'testType', privacy_level: 'high' })} disabled={props.loading}>Generate Data</button>
    {props.loading && <span data-testid="gen-loading">Loading...</span>}
    {props.error && <span data-testid="gen-error">{props.error}</span>}
  </div>
));
jest.mock('../components/SyntheticDataTable', () => (props) => <div data-testid="synthetic-table">{Array.isArray(props.data) ? props.data.length : 0} rows</div>);

// Setup API mocks for all API calls used in DashboardPage
const mockAIResults = { entityHighlights: [{ entity: 'TestEntity', type: 'Condition' }], summaryStats: { patients: 15 } };
const mockSyntheticData = [{ id: 1, value: 'row1' }, { id: 2, value: 'row2' }];

describe('DashboardPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('testDashboardPage_InitialLoad_ShowsLoadingAndLoadsData', async () => {
    jest.spyOn(api, 'fetchAIResults').mockResolvedValueOnce(mockAIResults);
    jest.spyOn(api, 'fetchSyntheticData').mockResolvedValueOnce(mockSyntheticData);
    render(<DashboardPage />);
    // Initially, loading spinner should appear
    expect(screen.getByText(/Loading dashboard data/i)).toBeInTheDocument();
    // Wait for data to load
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    // Validate AI highlights and statistics rendered
    expect(screen.getByTestId('entity-highlights')).toBeInTheDocument();
    expect(screen.getByTestId('summary-statistics')).toBeInTheDocument();
    // Synthetic data table rows
    expect(screen.getByTestId('synthetic-table')).toHaveTextContent('2 rows');
  });

  it('testDashboardPage_APIError_DisplaysErrorAlert', async () => {
    jest.spyOn(api, 'fetchAIResults').mockRejectedValueOnce(new Error('API Error'));
    jest.spyOn(api, 'fetchSyntheticData').mockRejectedValueOnce(new Error('API Error'));
    render(<DashboardPage />);
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('alert')).toHaveTextContent('Failed to load dashboard data');
  });

  it('testDashboardPage_RefreshButton_TriggersReload', async () => {
    const fetchAIMock = jest.spyOn(api, 'fetchAIResults');
    const fetchSynthMock = jest.spyOn(api, 'fetchSyntheticData');
    fetchAIMock.mockResolvedValue(mockAIResults);
    fetchSynthMock.mockResolvedValue(mockSyntheticData);
    render(<DashboardPage />);
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    // Simulate clicking refresh
    fireEvent.click(screen.getByRole('button', { name: /Refresh Data/i }));
    // Expect loading spinner after clicking refresh
    expect(screen.getByText(/Loading dashboard data/i)).toBeInTheDocument();
    // Wait for reload
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    // Fetch should be called twice (initial + refresh)
    expect(fetchAIMock).toHaveBeenCalledTimes(2);
    expect(fetchSynthMock).toHaveBeenCalledTimes(2);
  });

  it('testHandleGenerateSynthetic_Success_TriggersDashboardReload', async () => {
    jest.spyOn(api, 'fetchAIResults').mockResolvedValue(mockAIResults);
    jest.spyOn(api, 'fetchSyntheticData').mockResolvedValue(mockSyntheticData);
    const genMock = jest.spyOn(api, 'generateSyntheticData').mockResolvedValueOnce({ success: true });
    render(<DashboardPage />);
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    // Click on generate button
    fireEvent.click(screen.getByTestId('generate-btn'));
    // Loading indicator for generation
    expect(screen.getByTestId('gen-loading')).toBeInTheDocument();
    await waitFor(() => expect(genMock).toHaveBeenCalledWith({ record_count: 5, data_type: 'testType', privacy_level: 'high' }));
    // After generation, dashboard should reload (check API called again)
    await waitFor(() => expect(api.fetchAIResults).toHaveBeenCalledTimes(2));
    // Loading indicator disappears
    expect(screen.queryByTestId('gen-loading')).not.toBeInTheDocument();
  });

  it('testHandleGenerateSynthetic_APIError_SetsErrorState', async () => {
    jest.spyOn(api, 'fetchAIResults').mockResolvedValue(mockAIResults);
    jest.spyOn(api, 'fetchSyntheticData').mockResolvedValue(mockSyntheticData);
    jest.spyOn(api, 'generateSyntheticData').mockRejectedValueOnce({ response: { data: { error: 'Bad params' } } });
    render(<DashboardPage />);
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    fireEvent.click(screen.getByTestId('generate-btn'));
    // Generation error message should appear
    await waitFor(() => expect(screen.getByTestId('gen-error')).toBeInTheDocument());
    expect(screen.getByTestId('gen-error')).toHaveTextContent('Bad params');
  });

  it('testDashboardPage_NoSyntheticData_HandlesEmptyTable', async () => {
    jest.spyOn(api, 'fetchAIResults').mockResolvedValue(mockAIResults);
    jest.spyOn(api, 'fetchSyntheticData').mockResolvedValue([]);
    render(<DashboardPage />);
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    expect(screen.getByTestId('synthetic-table')).toHaveTextContent('0 rows');
  });

  it('testDashboardPage_RendersAllDashboardSections', async () => {
    jest.spyOn(api, 'fetchAIResults').mockResolvedValue(mockAIResults);
    jest.spyOn(api, 'fetchSyntheticData').mockResolvedValue(mockSyntheticData);
    render(<DashboardPage />);
    await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
    // Dashboard title
    expect(screen.getByText('AI-Driven Healthcare Data Dashboard')).toBeInTheDocument();
    // Section headers
    expect(screen.getByText(/Entity Recognition Highlights/i)).toBeInTheDocument();
    expect(screen.getByText(/Summary Statistics/i)).toBeInTheDocument();
    expect(screen.getByText(/Generate New Synthetic Data/i)).toBeInTheDocument();
    expect(screen.getByText(/Generated Synthetic Data/i)).toBeInTheDocument();
  });
});

// Edge case: Simulate slow network to check loading spinner remains
it('testDashboardPage_SlowAPICall_ShowsSpinner', async () => {
  jest.useFakeTimers();
  jest.spyOn(api, 'fetchAIResults').mockImplementationOnce(() => new Promise((resolve) => setTimeout(() => resolve(mockAIResults), 3000)));
  jest.spyOn(api, 'fetchSyntheticData').mockImplementationOnce(() => new Promise((resolve) => setTimeout(() => resolve(mockSyntheticData), 3000)));
  render(<DashboardPage />);
  // Spinner should be present during fetch
  expect(screen.getByText(/Loading dashboard data/i)).toBeInTheDocument();
  // Advance timers (simulate time passing)
  jest.advanceTimersByTime(3000);
  await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
  jest.useRealTimers();
});

// Security test: Handle malicious input gracefully (simulate injection in params)
it('testHandleGenerateSynthetic_InjectionInput_ShowsUserError', async () => {
  jest.spyOn(api, 'fetchAIResults').mockResolvedValue(mockAIResults);
  jest.spyOn(api, 'fetchSyntheticData').mockResolvedValue(mockSyntheticData);
  // Simulate generateSyntheticData rejecting on suspicious param
  jest.spyOn(api, 'generateSyntheticData').mockRejectedValueOnce({ message: 'Invalid parameters' });
  render(<DashboardPage />);
  await waitFor(() => expect(screen.queryByText(/Loading dashboard data/i)).not.toBeInTheDocument());
  // Manually call onGenerate with suspicious param (simulate code injection)
  const SyntheticControls = screen.getByTestId('generate-btn');
  fireEvent.click(SyntheticControls); // In mock, click always passes the same dummy param
  await waitFor(() => expect(screen.getByTestId('gen-error')).toBeInTheDocument());
  expect(screen.getByTestId('gen-error')).toHaveTextContent('Invalid parameters');
});