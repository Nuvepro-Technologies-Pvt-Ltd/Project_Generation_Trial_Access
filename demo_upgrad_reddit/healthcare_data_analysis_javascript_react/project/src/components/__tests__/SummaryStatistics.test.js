import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SummaryStatistics from '../SummaryStatistics';

// Test suite for SummaryStatistics component

// ----- Fixtures and Helpers ----- //
const SAMPLE_STATS = {
  patientCount: 32,
  averageHeartRate: 81,
  abnormalReadings: 5,
};

const EDGE_STATS = {
  zeroValue: 0,
  negativeValue: -5,
  stringValue: 'N/A',
};

const WEIRD_STATS = {
  'dangerous<script>': 14,
  MixedCASE123: 101,
};

const createManyStats = (count = 12, prefix = 'metric') => {
  const many = {};
  for (let i = 1; i <= count; i++) {
    many[`${prefix}${i}`] = i * 10;
  }
  return many;
};

// Custom utility for class-based query assertions
const getElementsByClass = (container, className) =>
  Array.from(container.getElementsByClassName(className));

// ----- Test Cases ----- //
describe('SummaryStatistics', () => {
  it('renders all statistics correctly when props are provided', () => {
    render(<SummaryStatistics stats={SAMPLE_STATS} />);
    expect(screen.getByText('patient Count'), 'Failed to find label for patientCount').toBeInTheDocument();
    expect(screen.getByText('average Heart Rate'), 'Failed to find label for averageHeartRate').toBeInTheDocument();
    expect(screen.getByText('abnormal Readings'), 'Failed to find label for abnormalReadings').toBeInTheDocument();
    expect(screen.getByText('32'), 'Failed to display correct value for patientCount').toBeInTheDocument();
    expect(screen.getByText('81'), 'Failed to display correct value for averageHeartRate').toBeInTheDocument();
    expect(screen.getByText('5'), 'Failed to display correct value for abnormalReadings').toBeInTheDocument();
  });

  it('verifies columns are rendered per statistic', () => {
    const { container } = render(<SummaryStatistics stats={SAMPLE_STATS} />);
    const columns = container.querySelectorAll('.col-md-4, .col-sm-6');
    // At least as many columns as stats keys
    expect(columns.length, `Expected at least ${Object.keys(SAMPLE_STATS).length} columns`).toBeGreaterThanOrEqual(Object.keys(SAMPLE_STATS).length);
    // Each column contains the correct stat label
    Object.keys(SAMPLE_STATS).forEach(stat => {
      const label = stat.replace(/([A-Z])/g, ' $1');
      expect(screen.getByText(label), `Failed to find column for stat '${stat}'`).toBeInTheDocument();
    });
  });

  it('renders "No statistics available." when stats is undefined', () => {
    render(<SummaryStatistics />);
    expect(screen.getByText('No statistics available.'), 'Should display empty-state when stats is undefined').toBeInTheDocument();
  });

  it('renders "No statistics available." when stats is null', () => {
    render(<SummaryStatistics stats={null} />);
    expect(screen.getByText('No statistics available.'), 'Should display empty-state when stats is null').toBeInTheDocument();
  });

  it('renders no statistic elements if stats is an empty object', () => {
    const { container } = render(<SummaryStatistics stats={{}} />);
    // Should render a Row, but no .display-4 elements
    const statElems = getElementsByClass(container, 'display-4');
    expect(statElems.length, 'Should not render any statistic values if stats is empty object').toBe(0);
  });

  it('renders no statistic elements if stats is an empty array', () => {
    const { container } = render(<SummaryStatistics stats={[]} />);
    // Should gracefully handle non-iterable case
    const statElems = getElementsByClass(container, 'display-4');
    expect(statElems.length, 'Should not render any statistic values if stats is empty array').toBe(0);
    expect(screen.queryByText('No statistics available.'), 'Should not show empty-state for array').not.toBeInTheDocument();
  });

  it('renders "No statistics available." if stats is an unexpected non-object type (number)', () => {
    render(<SummaryStatistics stats={42} />);
    expect(screen.getByText('No statistics available.'), 'Should display empty-state for number stats').toBeInTheDocument();
  });

  it('renders "No statistics available." if stats is an unexpected non-object type (string)', () => {
    render(<SummaryStatistics stats={'not-an-object'} />);
    expect(screen.getByText('No statistics available.'), 'Should display empty-state for string stats').toBeInTheDocument();
  });

  it('correctly renders statistics with edge-case values (0, negative, string)', () => {
    render(<SummaryStatistics stats={EDGE_STATS} />);
    expect(screen.getByText('zero Value'), 'Should display label for zeroValue').toBeInTheDocument();
    expect(screen.getByText('0'), 'Should display value for zeroValue').toBeInTheDocument();
    expect(screen.getByText('negative Value'), 'Should display label for negativeValue').toBeInTheDocument();
    expect(screen.getByText('-5'), 'Should display value for negativeValue').toBeInTheDocument();
    expect(screen.getByText('string Value'), 'Should display label for stringValue').toBeInTheDocument();
    expect(screen.getByText('N/A'), 'Should display value for stringValue').toBeInTheDocument();
  });

  it('renders large number of statistics across multiple columns and rows', () => {
    const manyStats = createManyStats(12, 'metric');
    render(<SummaryStatistics stats={manyStats} />);
    Object.keys(manyStats).forEach((metric, idx) => {
      expect(screen.getByText(metric), `Missing metric label '${metric}'`).toBeInTheDocument();
      expect(screen.getByText(`${manyStats[metric]}`), `Missing metric value for '${metric}'`).toBeInTheDocument();
    });
  });

  it('escapes and displays uncommon stat names safely', () => {
    render(<SummaryStatistics stats={WEIRD_STATS} />);
    expect(screen.getByText('dangerous<script>'), 'Failed to display HTML-like stat name safely').toBeInTheDocument();
    expect(screen.getByText('14'), 'Failed to display value for dangerous key').toBeInTheDocument();
    expect(screen.getByText('Mixed C A S E123'), 'Failed to humanize MixedCASE123').toBeInTheDocument();
    expect(screen.getByText('101'), 'Failed to display value for MixedCASE123').toBeInTheDocument();
  });
});