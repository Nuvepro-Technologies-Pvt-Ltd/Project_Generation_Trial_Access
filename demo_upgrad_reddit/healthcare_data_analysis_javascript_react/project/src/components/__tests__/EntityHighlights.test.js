import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import EntityHighlights from '../EntityHighlights';


// Test suite for EntityHighlights component (React, Jest, React Testing Library)
describe('EntityHighlights', () => {
  // Unit test: Renders 'No entities recognized.' when highlights is undefined or empty
  it('should render no-entity message if highlights prop is undefined', () => {
    render(<EntityHighlights highlights={undefined} />);
    expect(screen.getByText('No entities recognized.')).toBeInTheDocument();
  });
  
  it('should render no-entity message if highlights prop is empty array', () => {
    render(<EntityHighlights highlights={[]} />);
    expect(screen.getByText('No entities recognized.')).toBeInTheDocument();
  });

  // Unit test: Render single highlight without confidence
  it('should render single entity highlight without confidence', () => {
    const highlights = [
      { text: 'Aspirin', type: 'Drug' }
    ];
    render(<EntityHighlights highlights={highlights} />);
    // Check text
    expect(screen.getByText('Aspirin')).toBeInTheDocument();
    // Check badge
    expect(screen.getByText('Drug')).toBeInTheDocument();
    // Should not show confidence line
    expect(screen.queryByText(/Confidence/)).toBeNull();
  });

  // Unit test: Render multiple highlights with and without confidence
  it('should render multiple entity highlights, showing confidence where provided', () => {
    const highlights = [
      { text: 'Migraine', type: 'Disease', confidence: 92 },
      { text: 'Paracetamol', type: 'Drug', confidence: 80 },
      { text: 'Cold', type: 'Symptom' } // no confidence
    ];
    render(<EntityHighlights highlights={highlights} />);
    // Check all items rendered
    expect(screen.getByText('Migraine')).toBeInTheDocument();
    expect(screen.getByText('Paracetamol')).toBeInTheDocument();
    expect(screen.getByText('Cold')).toBeInTheDocument();
    // Check all badges
    expect(screen.getByText('Disease')).toBeInTheDocument();
    expect(screen.getByText('Drug')).toBeInTheDocument();
    expect(screen.getByText('Symptom')).toBeInTheDocument();
    // Check confidence displays
    expect(screen.getByText('Confidence: 92%')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 80%')).toBeInTheDocument();
    // Should NOT show for entity without confidence
    expect(screen.queryByText('Confidence: undefined%')).toBeNull();
    // Should not show for entity that lacks confidence
    expect(screen.queryByText(/Confidence:/, {exact: false})).not.toHaveTextContent('Confidence: undefined%');
  });

  // Edge case: Render when entity.text or entity.type is an empty string
  it('should render entity with empty text and type gracefully', () => {
    const highlights = [
      { text: '', type: '', confidence: 50 }
    ];
    render(<EntityHighlights highlights={highlights} />);
    // Rendered item exists (text is empty, badge is empty, confidence present)
    // Expect badge node to be present
    const badgeNode = screen.getByRole('status'); // badges rendered as <span role="status"> in react-bootstrap (if not, fallback below)
    expect(badgeNode || screen.getByText('')).toBeInTheDocument();
    expect(screen.getByText('Confidence: 50%')).toBeInTheDocument();
  });

  // Edge case: Render when entity.confidence = 0
  it('should render entity if confidence is 0', () => {
    const highlights = [
      { text: 'Example', type: 'Type', confidence: 0 }
    ];
    render(<EntityHighlights highlights={highlights} />);
    expect(screen.getByText('Confidence: 0%')).toBeInTheDocument();
  });

  // Error scenario: Malformed highlights array (non-object)
  it('should not crash if an invalid highlight is provided', () => {
    const highlights = [null, undefined, { foo: 'bar' }, 42];
    render(<EntityHighlights highlights={highlights} />);
    // The component may render nothing meaningful, but should at least render empty strings or empty badge
    // Should not throw and at least render as many list items as valid entities
    const listItems = screen.getAllByRole('listitem');
    expect(listItems.length).toBe(highlights.length);
  });

  // Security: Ensure no injection for entity.text/type
  it('should render literals safely without interpreting HTML', () => {
    const highlights = [
      { text: '<img src=x onerror=alert(1)>', type: '<script>alert(1)</script>', confidence: 90 }
    ];
    render(<EntityHighlights highlights={highlights} />);
    // The rendered text should be visible as-is, not interpreted as HTML or script
    expect(screen.getByText('<img src=x onerror=alert(1)>')).toBeInTheDocument();
    expect(screen.getByText('<script>alert(1)</script>')).toBeInTheDocument();
  });
});