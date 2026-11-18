export function getFlaskBaseUrl(): string {
  return (
    process.env.FLASK_API_BASE_URL ||
    process.env.NEXT_PUBLIC_FLASK_API_BASE_URL ||
    "http://127.0.0.1:5000"
  ).replace(/\/$/, "");
}

export async function flaskFetch<T = unknown>(
  path: string,
  init?: RequestInit,
): Promise<{ ok: boolean; status: number; data: T | null; raw: unknown }> {
  const url = `${getFlaskBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  try {
    const res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
    const raw = await res.json().catch(() => null);
    const envelope = raw as { code?: number; data?: T; message?: string } | null;
    const ok = res.ok && envelope?.code === 200;
    return {
      ok,
      status: res.status,
      data: ok ? (envelope?.data ?? null) : null,
      raw,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      data: null,
      raw: error instanceof Error ? error.message : "Flask unreachable",
    };
  }
}
