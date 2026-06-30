import Link from "next/link";
import { formatTimecode, getTitle } from "@/lib/api";

export default async function TitlePage({ params }: { params: { id: string } }) {
  const title = await getTitle(params.id);
  const flagged = title.segments.filter((s) => s.state === "FLAGGED");

  return (
    <main>
      <h1>{title.name}</h1>
      <p style={{ color: "#94a3b8" }}>
        {title.source_language.toUpperCase()} → {title.language.toUpperCase()} · {title.segment_count} segments ·{" "}
        {title.flagged} flagged for review
      </p>

      <div className="grid grid-4" style={{ margin: "20px 0" }}>
        <div className="card"><div>Accepted</div><strong>{title.accepted}</strong></div>
        <div className="card"><div>Flagged</div><strong>{title.flagged}</strong></div>
        <div className="card"><div>Rejected</div><strong>{title.rejected}</strong></div>
        <div className="card"><div>Status</div><strong>{title.status}</strong></div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h2>Review Queue</h2>
        {flagged.length === 0 ? (
          <p>No flagged segments. Auto-cleared or rejected.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Timecode</th>
                <th>Issue</th>
                <th>Utility</th>
                <th>Dialogue</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {flagged.map((segment) => (
                <tr key={segment.id}>
                  <td>{formatTimecode(segment.start_ms)}</td>
                  <td>{segment.issue_type || "review"}</td>
                  <td>{segment.utility?.toFixed(1)}</td>
                  <td>{segment.dialogue_text.slice(0, 80)}</td>
                  <td>
                    <Link href={`/review/${title.id}/${segment.id}`}>Evidence Room</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>All Segments</h2>
        <table>
          <thead>
            <tr>
              <th>Timecode</th>
              <th>State</th>
              <th>Sync</th>
              <th>Semantic</th>
              <th>Performance</th>
            </tr>
          </thead>
          <tbody>
            {title.segments.map((segment) => (
              <tr key={segment.id}>
                <td>{formatTimecode(segment.start_ms)}</td>
                <td>{segment.state}</td>
                <td>{segment.scores?.sync ?? "-"}</td>
                <td>{segment.scores?.semantic ?? "-"}</td>
                <td>{segment.scores?.performance ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
