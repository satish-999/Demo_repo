"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  API_BASE,
  formatTimecode,
  getTitle,
  scoreColor,
  submitDecision,
  type Segment,
  type TitleDetail,
} from "@/lib/api";

function wordDiff(original: string | null, dubbed: string) {
  if (!original) return <p>{dubbed}</p>;
  const o = original.split(/\s+/);
  const d = dubbed.split(/\s+/);
  const max = Math.max(o.length, d.length);
  const nodes = [];
  for (let i = 0; i < max; i++) {
    const ow = o[i];
    const dw = d[i];
    if (ow === dw) nodes.push(<span key={i}>{dw} </span>);
    else {
      if (ow) nodes.push(<del key={`o${i}`}>{ow} </del>);
      if (dw) nodes.push(<ins key={`d${i}`}>{dw} </ins>);
    }
  }
  return <p className="diff">{nodes}</p>;
}

export default function EvidenceRoomPage({
  params,
}: {
  params: { titleId: string; segmentId: string };
}) {
  const router = useRouter();
  const [title, setTitle] = useState<TitleDetail | null>(null);
  const [segment, setSegment] = useState<Segment | null>(null);
  const [rationale, setRationale] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTitle(params.titleId).then((t) => {
      setTitle(t);
      setSegment(t.segments.find((s) => s.id === params.segmentId) || null);
    });
  }, [params.titleId, params.segmentId]);

  const videoSrc = useMemo(() => {
    if (!title?.video_path) return null;
    return `${API_BASE}/api/v1/media/${title.id}/video`;
  }, [title]);

  async function decide(decision: "ACCEPT" | "REJECT") {
    if (!segment || !rationale.trim()) {
      setError("Please enter a rationale");
      return;
    }
    setError(null);
    await submitDecision(segment.id, decision, rationale);
    router.push(`/titles/${params.titleId}`);
  }

  if (!title || !segment) return <p>Loading evidence...</p>;

  const scores = [
    ["Sync", segment.scores?.sync],
    ["Semantic", segment.scores?.semantic],
    ["Performance", segment.scores?.performance],
    ["Continuity", segment.scores?.continuity],
  ] as const;

  return (
    <main>
      <h1>Evidence Room</h1>
      <p style={{ color: "#94a3b8" }}>
        {title.name} · {formatTimecode(segment.start_ms)} – {formatTimecode(segment.end_ms)} · {segment.issue_type}
      </p>

      <div className="grid grid-2">
        <div className="card">
          <h3>Segment window</h3>
          {title.video_path && videoSrc ? (
            <video
              controls
              style={{ width: "100%", borderRadius: 8, background: "#000" }}
              src={videoSrc}
              onLoadedMetadata={(e) => {
                const el = e.currentTarget;
                if (segment) el.currentTime = Math.max(0, segment.start_ms / 1000 - 1);
              }}
            />
          ) : (
            <p>No video attached. Audio/SRT scoring still ran on subtitle timing.</p>
          )}
          <p>
            <strong>Drift estimate:</strong> {segment.scores?.drift_ms ?? "n/a"} ms
          </p>
        </div>

        <div className="card">
          <h3>Axis scores</h3>
          {scores.map(([label, value]) => (
            <div key={label} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>{label}</span>
                <span>{value ?? "-"}</span>
              </div>
              <div className="score-bar">
                <span style={{ width: `${value ?? 0}%`, background: scoreColor(value) }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>Original script line</h3>
          <p>{segment.script_line || "No script provided for this cue."}</p>
        </div>
        <div className="card">
          <h3>Dubbed transcript diff</h3>
          {wordDiff(segment.script_line, segment.dialogue_text)}
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3>Reviewer decision</h3>
        <div className="field">
          <label>Rationale</label>
          <textarea rows={3} value={rationale} onChange={(e) => setRationale(e.target.value)} />
        </div>
        {error && <p style={{ color: "#fca5a5" }}>{error}</p>}
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn green" onClick={() => decide("ACCEPT")}>Accept</button>
          <button className="btn red" onClick={() => decide("REJECT")}>Reject</button>
        </div>
      </div>
    </main>
  );
}
