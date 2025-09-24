import React from 'react';
import { render, screen, within } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import EntityHighlights from '../EntityHighlights';

// __tests__/EntityHighlights.test.js
// ARRANGE - ACT - ASSERT structure covering all functional, edge, and accessibility scenarios for EntityHighlights

describe('EntityHighlights component', () => {
  // Utility for building highlights with data-testid for robust queries
  function makeHighlights(list) {
    return list.map(e => e && { ...e });
  }

  it('renders muted text when highlights prop is undefined', () => {
    render(<EntityHighlights highlights={undefined} />);
    expect(screen.getByText('No entities recognized.')).toBeInTheDocument();
  });

  it('renders muted text when highlights is an empty array', () => {
    render(<EntityHighlights highlights={[]} />);
    expect(screen.getByText('No entities recognized.')).toBeInTheDocument();
  });

  it('displays entity text, type badge, and confidence value', () => {
    const highlights = makeHighlights([
      { text: 'Hypertension', type: 'Condition', confidence: 98 }
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const item = screen.getByText('Hypertension').closest('li');
    expect(item).toBeInTheDocument();
    expect(within(item).getByText('Condition')).toBeInTheDocument();
    expect(within(item).getByText(/Confidence: 98%/)).toBeInTheDocument();
  });

  it('correctly displays multiple entities with and without confidence fields', () => {
    const highlights = makeHighlights([
      { text: 'Ibuprofen', type: 'Medication', confidence: 85 },
      { text: 'Headache', type: 'Symptom' }
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const ibuprofenItem = screen.getByText('Ibuprofen').closest('li');
    expect(within(ibuprofenItem).getByText('Medication')).toBeInTheDocument();
    expect(within(ibuprofenItem).getByText(/Confidence: 85%/)).toBeInTheDocument();
    const headacheItem = screen.getByText('Headache').closest('li');
    expect(within(headacheItem).getByText('Symptom')).toBeInTheDocument();
    expect(within(headacheItem).queryByText(/Confidence:/)).toBeNull();
  });

  it('handles highlights containing null and undefined elements gracefully (renders fallback if emptied)', () => {
    const highlights = makeHighlights([null, undefined, undefined]);
    render(<EntityHighlights highlights={highlights} />);
    expect(screen.getByText('No entities recognized.')).toBeInTheDocument();
  });

  it('handles highlights with valid and null/undefined elements, filtering them', () => {
    const highlights = makeHighlights([
      null, { text: 'Diabetes', type: 'Condition', confidence: 90 }, undefined
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const item = screen.getByText('Diabetes').closest('li');
    expect(item).toBeInTheDocument();
    expect(within(item).getByText('Condition')).toBeInTheDocument();
    expect(within(item).getByText(/Confidence: 90%/)).toBeInTheDocument();
  });

  it('renders entities even with empty text or type', () => {
    const highlights = makeHighlights([
      { text: '', type: '', confidence: 75 }
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const listItems = screen.getAllByRole('listitem');
    expect(listItems.length).toBe(1);
    // Badge with empty content exists
    const badge = within(listItems[0]).getByTestId('entity-type-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('');
    expect(within(listItems[0]).getByText(/Confidence: 75%/)).toBeInTheDocument();
  });

  it('casts non-string type (number) to string in badge', () => {
    const highlights = makeHighlights([{ text: 'Fever', type: 1234 }]);
    render(<EntityHighlights highlights={highlights} />);
    const item = screen.getByText('Fever').closest('li');
    const badge = within(item).getByTestId('entity-type-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('1234');
  });

  it('renders 100 entities without crashing', () => {
    const highlights = makeHighlights(Array.from({ length: 100 }, (_, i) => ({ text: `Entity${i + 1}`, type: 'Type', confidence: i % 2 === 0 ? 99 : undefined })));
    render(<EntityHighlights highlights={highlights} />);
    expect(screen.getByText('Entity1')).toBeInTheDocument();
    expect(screen.getByText('Entity100')).toBeInTheDocument();
    expect(screen.getAllByTestId('entity-type-badge').length).toBe(100);
  });

  // (OPTIONAL) Basic render performance measurement
  it('renders 100 entities within reasonable time (basic performance check)', () => {
    const highlights = makeHighlights(Array.from({ length: 100 }, (_, i) => ({ text: `E${i}`, type: 'T', confidence: 88 })));
    const start = performance.now ? performance.now() : Date.now();
    render(<EntityHighlights highlights={highlights} />);
    const end = performance.now ? performance.now() : Date.now();
    expect(end - start).toBeLessThan(1000); // 1 second threshold
  });

  // Accessibility checks
  it('renders list with accessible list and listitem roles', () => {
    const highlights = makeHighlights([
      { text: 'Migraine', type: 'Condition', confidence: 75 }
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const list = screen.getByRole('list');
    expect(list).toBeInTheDocument();
    const items = within(list).getAllByRole('listitem');
    expect(items.length).toBe(1);
  });

  it('each badge is announced to assistive tech via aria-label', () => {
    const highlights = makeHighlights([
      { text: 'Cough', type: 'Symptom' }
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const badge = screen.getByTestId('entity-type-badge');
    expect(badge).toHaveAttribute('aria-label', 'Entity type: Symptom');
  });

  // (OPTIONAL) Keyboard navigation - ensures tabbable list items
  it('all main clickable elements are tabbable', () => {
    // Here, none are anchor or button, so check that the rendered list items do not interfere with tab order.
    const highlights = makeHighlights([
      { text: 'Asthma', type: 'Condition' },
      { text: 'Albuterol', type: 'Medication' }
    ]);
    render(<EntityHighlights highlights={highlights} />);
    const items = screen.getAllByRole('listitem');
    items.forEach(item => {
      expect(item.tabIndex).toBe(-1); // Not interactive
    });
  });
});