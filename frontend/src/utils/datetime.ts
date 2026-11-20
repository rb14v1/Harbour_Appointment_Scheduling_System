const pad = (value: number) => String(value).padStart(2, '0');

/** Formats a Date as the value expected by <input type="datetime-local"> (local time). */
export function formatLocalInput(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/** Converts an ISO timestamp from the API into a datetime-local value. */
export function toLocalInputValue(iso: string): string {
  return formatLocalInput(new Date(iso));
}

/** Converts a datetime-local value (local time) into an ISO timestamp with offset. */
export function fromLocalInputValue(value: string): string {
  return new Date(value).toISOString();
}

export function addMinutesToLocalInput(value: string, minutes: number): string {
  const date = new Date(value);
  date.setMinutes(date.getMinutes() + minutes);
  return formatLocalInput(date);
}

export function isOnQuarterHour(value: string): boolean {
  return new Date(value).getMinutes() % 15 === 0;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString(undefined, { timeStyle: 'short' });
}
