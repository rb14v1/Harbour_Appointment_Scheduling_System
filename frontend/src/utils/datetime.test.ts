import { describe, expect, it } from 'vitest';
import { addMinutesToLocalInput, isOnQuarterHour, toLocalInputValue, fromLocalInputValue } from './datetime';

describe('datetime helpers', () => {
  it('adds minutes to a datetime-local value', () => {
    expect(addMinutesToLocalInput('2026-11-20T09:00', 60)).toBe('2026-11-20T10:00');
    expect(addMinutesToLocalInput('2026-11-20T23:45', 30)).toBe('2026-11-21T00:15');
  });

  it('round-trips between local input values and ISO timestamps', () => {
    const iso = fromLocalInputValue('2026-11-20T14:30');
    expect(toLocalInputValue(iso)).toBe('2026-11-20T14:30');
  });

  it('detects quarter-hour boundaries', () => {
    expect(isOnQuarterHour('2026-11-20T09:15')).toBe(true);
    expect(isOnQuarterHour('2026-11-20T09:10')).toBe(false);
  });
});
