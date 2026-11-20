import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import StatusBadge from './StatusBadge';

describe('StatusBadge', () => {
  it('renders the readable label for each status', () => {
    const { rerender } = render(<StatusBadge status="scheduled" />);
    expect(screen.getByText('Scheduled')).toHaveClass('badge-scheduled');

    rerender(<StatusBadge status="cancelled" />);
    expect(screen.getByText('Cancelled')).toHaveClass('badge-cancelled');
  });
});
