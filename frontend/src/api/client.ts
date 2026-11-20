export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

interface ErrorBody {
  error?: {
    message?: string;
    details?: Record<string, string[] | string>;
  };
}

function firstFieldError(details: Record<string, string[] | string> | undefined): string | undefined {
  const entry = details ? Object.entries(details)[0] : undefined;
  if (!entry) return undefined;
  const [field, messages] = entry;
  const text = Array.isArray(messages) ? messages[0] : messages;
  return `${field}: ${text}`;
}

export async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) return undefined as T;

  const data = (await response.json().catch(() => null)) as ErrorBody | T | null;
  if (!response.ok) {
    const errorBody = data as ErrorBody | null;
    const message =
      firstFieldError(errorBody?.error?.details) ?? errorBody?.error?.message ?? `Request failed (${response.status}).`;
    throw new ApiError(response.status, message);
  }
  return data as T;
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong.';
}
