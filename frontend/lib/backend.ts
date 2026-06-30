/** Backend URL candidates — tried in order until one responds. */
const CANDIDATES = [
  process.env.NEXT_PUBLIC_API_URL,
  "http://127.0.0.1:8000",
  "http://localhost:8000",
].filter((value): value is string => Boolean(value));

let cachedBase: string | null = null;

export function getDefaultApiBase(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
}

export async function resolveApiBase(): Promise<string | null> {
  if (cachedBase) return cachedBase;

  for (const base of CANDIDATES.length ? CANDIDATES : [getDefaultApiBase()]) {
    try {
      const res = await fetch(`${base}/api/v1/health`, { cache: "no-store" });
      if (res.ok) {
        cachedBase = base;
        return base;
      }
    } catch {
      // try next candidate
    }
  }
  return null;
}

export function apiUrl(path: string, base?: string): string {
  const root = base ?? getDefaultApiBase();
  return `${root}${path}`;
}
