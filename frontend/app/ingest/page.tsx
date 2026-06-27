"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function IngestPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"upload" | "path">("upload");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const form = new FormData(e.currentTarget);

    try {
      if (mode === "upload") {
        const body = new FormData();
        body.append("title_name", String(form.get("title_name")));
        body.append("language", String(form.get("language")));
        body.append("source_language", String(form.get("source_language")));
        const srt = form.get("srt") as File;
        const video = form.get("video") as File;
        const audio = form.get("audio") as File;
        const script = form.get("script") as File;
        if (!srt?.size) throw new Error("SRT file is required");
        body.append("srt", srt);
        if (video?.size) body.append("video", video);
        if (audio?.size) body.append("audio", audio);
        if (script?.size) body.append("script", script);

        const res = await fetch(`${API_BASE}/api/v1/titles/ingest/upload`, {
          method: "POST",
          body,
        });
        if (!res.ok) throw new Error(await res.text());
        const title = await res.json();
        router.push(`/titles/${title.id}`);
      } else {
        const res = await fetch(`${API_BASE}/api/v1/titles/ingest`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title_name: form.get("title_name"),
            language: form.get("language"),
            source_language: form.get("source_language"),
            video_path: form.get("video_path") || undefined,
            audio_path: form.get("audio_path") || undefined,
            srt_path: form.get("srt_path"),
            script_path: form.get("script_path") || undefined,
          }),
        });
        if (!res.ok) throw new Error(await res.text());
        const title = await res.json();
        router.push(`/titles/${title.id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingest failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Ingest Title</h1>
      <p style={{ color: "#94a3b8" }}>
        Upload a short clip from a released movie: video/audio + SRT subtitles. Optional script improves semantic scoring.
      </p>

      <div style={{ marginBottom: 16 }}>
        <button className="btn" style={{ marginRight: 8 }} onClick={() => setMode("upload")}>
          Upload files
        </button>
        <button className="btn" onClick={() => setMode("path")}>
          Local file paths
        </button>
      </div>

      <form className="card" onSubmit={onSubmit}>
        <div className="field">
          <label>Title name</label>
          <input name="title_name" required placeholder="Pushpa 2 Hindi Dub Sample" />
        </div>
        <div className="grid grid-2">
          <div className="field">
            <label>Source language</label>
            <input name="source_language" defaultValue="te" />
          </div>
          <div className="field">
            <label>Target language (scored)</label>
            <input name="language" defaultValue="hi" />
          </div>
        </div>

        {mode === "upload" ? (
          <>
            <div className="field">
              <label>SRT subtitles (required)</label>
              <input name="srt" type="file" accept=".srt" required />
            </div>
            <div className="field">
              <label>Video file (optional)</label>
              <input name="video" type="file" accept="video/*" />
            </div>
            <div className="field">
              <label>Audio file (optional, improves sync/performance scoring)</label>
              <input name="audio" type="file" accept="audio/*" />
            </div>
            <div className="field">
              <label>Original script (optional)</label>
              <input name="script" type="file" accept=".txt,.srt" />
            </div>
          </>
        ) : (
          <>
            <div className="field">
              <label>SRT path (required)</label>
              <input name="srt_path" required placeholder="/path/to/subtitles.srt" />
            </div>
            <div className="field">
              <label>Video path</label>
              <input name="video_path" placeholder="/path/to/film.mp4" />
            </div>
            <div className="field">
              <label>Audio path</label>
              <input name="audio_path" placeholder="/path/to/audio.wav" />
            </div>
            <div className="field">
              <label>Script path</label>
              <input name="script_path" placeholder="/path/to/script.txt" />
            </div>
          </>
        )}

        {error && <p style={{ color: "#fca5a5" }}>{error}</p>}
        <button className="btn primary" type="submit" disabled={loading}>
          {loading ? "Scoring..." : "Submit for Scoring"}
        </button>
      </form>
    </main>
  );
}
