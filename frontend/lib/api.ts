import { getDefaultApiBase } from "./backend";

export const API_BASE = getDefaultApiBase();

export type TitleSummary = {
  id: string;
  name: string;
  language: string;
  source_language: string;
  status: string;
  segment_count: number;
  accepted: number;
  flagged: number;
  rejected: number;
  progress_pct: number;
  blockers: number;
  updated_at: string | null;
};

export type Segment = {
  id: string;
  title_id: string;
  start_ms: number;
  end_ms: number;
  speaker: string | null;
  dialogue_text: string;
  script_line: string | null;
  state: string;
  issue_type: string | null;
  scores: {
    sync?: number;
    semantic?: number;
    performance?: number;
    continuity?: number;
    drift_ms?: number;
  } | null;
  utility: number | null;
  rejection_reason: string | null;
  reviewer_rationale: string | null;
};

export type TitleDetail = TitleSummary & {
  video_path: string | null;
  audio_path: string | null;
  srt_path: string | null;
  script_path: string | null;
  segments: Segment[];
};

export type DashboardStats = {
  ready_to_ship: number;
  in_review: number;
  blocked: number;
  pending_human_review: number;
};

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const getDashboard = () => api<DashboardStats>("/api/v1/dashboard");
export const getTitles = () => api<TitleSummary[]>("/api/v1/titles");
export const getTitle = (id: string) => api<TitleDetail>(`/api/v1/titles/${id}`);
export const getReviewQueue = (titleId: string) => api<Segment[]>(`/api/v1/titles/${titleId}/review-queue`);

export async function ingestByPath(body: {
  title_name: string;
  language: string;
  source_language: string;
  video_path?: string;
  audio_path?: string;
  srt_path: string;
  script_path?: string;
}) {
  return api<TitleDetail>("/api/v1/titles/ingest", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function submitDecision(segmentId: string, decision: "ACCEPT" | "REJECT", rationale: string) {
  return api<Segment>(`/api/v1/segments/${segmentId}/decision`, {
    method: "POST",
    body: JSON.stringify({ decision, rationale }),
  });
}

export function formatTimecode(ms: number): string {
  const totalSec = Math.floor(ms / 1000);
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  const milli = ms % 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(milli).padStart(3, "0")}`;
}

export function scoreColor(score: number | undefined): string {
  if (score === undefined) return "#94a3b8";
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#f59e0b";
  return "#ef4444";
}
