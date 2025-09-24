import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SummaryStatistics from '../SummaryStatistics';

// Test suite for the SummaryStatistics component
// Framework: Jest with React Testing Library

describe('SummaryStatistics', () => {
  /*
    Unit Test: Render with valid statistics props
    This ensures all keys and values are rendered correctly.
  */
  it('renders all statistics keys and values provided in props', () => {
    const stats = {
      patientsSeen: 24,
      avgWaitTime: '5 min',
      fastestDischarge: '8 min'
    };
    render(<SummaryStatistics stats={stats} />);

    // Assert keys (label formatting checks)
    expect(screen.getByText('patients Seen')).toBeInTheDocument();
    expect(screen.getByText('avg Wait Time')).toBeInTheDocument();
    expect(screen.getByText('fastest Discharge')).toBeInTheDocument();
    // Assert values
    expect(screen.getByText('24')).toBeInTheDocument();
    expect(screen.getByText('5 min')).toBeInTheDocument();
    expect(screen.getByText('8 min')).toBeInTheDocument();
    // Assert correct number of statistics rendered
    expect(screen.getAllByTestId('stat-col').length).toBe(Object.keys(stats).length);
  });

  /*
    Edge case: Render when stats is undefined.
    Should show 'No statistics available.'
  */
  it('renders message when stats is undefined', () => {
    render(<SummaryStatistics stats={undefined} />);
    expect(screen.getByText('No statistics available.')).toBeInTheDocument();
  });

  /*
    Edge case: Render when stats is null.
    Should show 'No statistics available.'
  */
  it('renders message when stats is null', () => {
    render(<SummaryStatistics stats={null} />);
    expect(screen.getByText('No statistics available.')).toBeInTheDocument();
  });

  /*
    Edge case: Render when stats is an empty object.
    Should not crash and simply render no columns.
  */
  it('renders nothing when stats is empty object', () => {
    render(<SummaryStatistics stats={{}} />);
    // The Row should be present
    expect(screen.getByTestId('stats-row')).toBeInTheDocument();
    // There should be no statistic columns
    expect(screen.queryAllByTestId('stat-col').length).toBe(0);
    // There should not be the fallback message
    expect(screen.queryByText('No statistics available.')).not.toBeInTheDocument();
  });

  /*
    Error scenario: Non-object stats (unexpected input type)
    Should show 'No statistics available.'
  */
  it('renders message if stats prop is not an object', () => {
    render(<SummaryStatistics stats={12345} />);
    expect(screen.getByText('No statistics available.')).toBeInTheDocument();
    render(<SummaryStatistics stats={['foo', 'bar']} />);
    expect(screen.getByText('No statistics available.')).toBeInTheDocument();
    render(<SummaryStatistics stats={true} />);
    expect(screen.getByText('No statistics available.')).toBeInTheDocument();
  });

  /*
    Integration test: Large number of statistics (performance, dynamic rendering)
  */
  it('renders multiple statistics (performance, dynamic test)', () => {
    const largeStats = {};
    for (let i = 1; i <= 15; i++) {
      largeStats[`stat${i}`] = i * 100;
    }
    render(<SummaryStatistics stats={largeStats} />);
    // All stats should be rendered
    for (let i = 1; i <= 15; i++) {
      expect(screen.getByText(`stat${i}`)).toBeInTheDocument();
      expect(screen.getByText(`${i * 100}`)).toBeInTheDocument();
    }
    expect(screen.getAllByTestId('stat-col').length).toBe(Object.keys(largeStats).length);
  });

  /*
    Security/robustness test: Stat key includes special characters
    Should not break and should display key
  */
  it('renders statistic key with special characters', () => {
    const specialStats = { 'avgBloodO2-Level%': 98 };
    render(<SummaryStatistics stats={specialStats} />);
    // Label should remain readable
    expect(screen.getByText('avg Blood O2-Level%')).toBeInTheDocument();
    expect(screen.getByText('98')).toBeInTheDocument();
  });

  /*
    Test: labels with various cases/numbers/spaces/format
  */
  it('formats keys into labels correctly (case/number edge cases)', () => {
    const stats = {
      ALLOUTPUT: 1,
      alloutput: 2,
      LeadingCaps: 3,
      'has  space': 4,
      numberInKey1: 5,
      _underscoreKey: 6
    };
    render(<SummaryStatistics stats={stats} />);
    expect(screen.getByText('A L L O U T P U T')).toBeInTheDocument();
    expect(screen.getByText('alloutput')).toBeInTheDocument();
    expect(screen.getByText('Leading Caps')).toBeInTheDocument();
    expect(screen.getByText('has  space')).toBeInTheDocument();
    expect(screen.getByText('number In Key1')).toBeInTheDocument();
    expect(screen.getByText('_underscore Key')).toBeInTheDocument();
  });

  /*
    Snapshot regression test: Structure remains unchanged
  */
  it('matches snapshot with typical statistics', () => {
    const stats = {
      temperature: '37°C',
      heartRate: 72
    };
    const { container } = render(<SummaryStatistics stats={stats} />);
    expect(container).toMatchSnapshot();
  });
});