import React from 'react';
import { render, screen } from '@testing-library/react';
import SummaryStatistics from '../../components/SummaryStatistics';

// Test suite for SummaryStatistics component
// Using React Testing Library (official best practice for React components)

describe('SummaryStatistics', () => {
  // Arrange: Utility function to generate mock stats data
  const getMockStats = () => ({
    totalPatients: 1450,
    aiBasedAlerts: 37,
    successfulInterventions: 1329,
    daysActive: 102,
    errorRate: 0.13
  });

  it('renders each statistic in a Col with the correct labels and values', () => {
    // Arrange
    const stats = getMockStats();
    // Act
    render(<SummaryStatistics stats={stats} />);
    // Assert
    // Check all statistic labels are in the document with capitalized spacing (e.g., Total Patients)
    expect(screen.getByText('Total Patients')).toBeInTheDocument();
    expect(screen.getByText('Ai Based Alerts')).toBeInTheDocument();
    expect(screen.getByText('Successful Interventions')).toBeInTheDocument();
    expect(screen.getByText('Days Active')).toBeInTheDocument();
    expect(screen.getByText('Error Rate')).toBeInTheDocument();

    // Check values (formatted correctly)
    expect(screen.getByText('1450')).toBeInTheDocument();
    expect(screen.getByText('37')).toBeInTheDocument();
    expect(screen.getByText('1329')).toBeInTheDocument();
    expect(screen.getByText('102')).toBeInTheDocument();
    expect(screen.getByText('0.13')).toBeInTheDocument();
  });

  it('renders fallback message when stats prop is null', () => {
    // Act
    render(<SummaryStatistics stats={null} />);
    // Assert
    const fallback = screen.getByText(/No statistics available\./i);
    expect(fallback).toBeInTheDocument();
    expect(fallback).toHaveClass('text-muted');
  });

  it('renders fallback message when stats prop is undefined', () => {
    // Act
    render(<SummaryStatistics />);
    // Assert
    expect(screen.getByText(/No statistics available\./i)).toBeInTheDocument();
  });

  it('handles empty stats object gracefully (renders no Cols but not fallback)', () => {
    // Act
    const { container } = render(<SummaryStatistics stats={{}} />);
    // Assert
    // Should not render any value elements
    expect(container.querySelectorAll('.display-4').length).toBe(0);
    // Should render Row, but with no children columns
    expect(container.querySelectorAll('.row').length).toBe(1);
    // Should not show fallback message
    expect(screen.queryByText(/No statistics available\./i)).not.toBeInTheDocument();
  });

  it('renders statistic labels with spaces before uppercase letters', () => {
    // Arrange
    const customStats = { patientsUnderCare: 90 };
    // Act
    render(<SummaryStatistics stats={customStats} />);
    // Assert
    expect(screen.getByText('Patients Under Care')).toBeInTheDocument();
    expect(screen.getByText('90')).toBeInTheDocument();
  });

  it('ensures correct Bootstrap classes are applied to Col and container', () => {
    // Arrange
    const stats = { totalPatients: 12 };
    // Act
    const { container } = render(<SummaryStatistics stats={stats} />);
    // Assert
    // Col should have correct Bootstrap classes
    const col = container.querySelector('.col-sm-6.col-md-4.mb-2');
    expect(col).not.toBeNull();
    // Inner div should have border and p-2 classes
    const panel = col.querySelector('.border.bg-white.rounded.p-2.text-center.h-100');
    expect(panel).not.toBeNull();
  });

  it('matches snapshot for stable rendering', () => {
    // Arrange
    const stats = getMockStats();
    // Act
    const { asFragment } = render(<SummaryStatistics stats={stats} />);
    // Assert
    expect(asFragment()).toMatchSnapshot();
  });

  // Additional edge case
  it('handles numeric keys (edge case) without crashing', () => {
    // Arrange
    const stats = { 123: 456 };
    // Act
    render(<SummaryStatistics stats={stats} />);
    // Assert
    expect(screen.getByText('123')).toBeInTheDocument();
    expect(screen.getByText('456')).toBeInTheDocument();
  });

  // Advanced: security - ensure no XSS injection via stat name
  it('escapes potentially malicious stat names (no HTML injection)', () => {
    // Arrange
    const malicious = { '<img src=x onerror=alert(1)>': 1 };
    // Act
    render(<SummaryStatistics stats={malicious} />);
    // Assert
    // Should render the plain string, not execute it as HTML
    expect(screen.getByText('<img src=x onerror=alert(1)>')).toBeInTheDocument();
  });

});
// End of test suite