import Link from "next/link";
import { getDashboard, getTitles } from "@/lib/api";

function statusBadge(status: string) {
  if (status === "READY") return <span className="badge green">Ready</span>;
  if (status === "BLOCKED") return <span className="badge red">Blocked</span>;
  return <span className="badge amber">In Review</span>;
}

export default async function CourtDeskPage() {
  const [stats, titles] = await Promise.all([getDashboard(), getTitles()]);

  return (
    <main>
      <h1>Court Desk</h1>
      <p style={{ color: "#94a3b8" }}>Release control room — POC slice of CineWeave RAE</p>

      <div className="grid grid-4" style={{ margin: "24px 0" }}>
        <div className="card">
          <div style={{ color: "#94a3b8", fontSize: 13 }}>Ready to Ship</div>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.ready_to_ship}</div>
        </div>
        <div className="card">
          <div style={{ color: "#94a3b8", fontSize: 13 }}>In Review</div>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.in_review}</div>
        </div>
        <div className="card">
          <div style={{ color: "#94a3b8", fontSize: 13 }}>Blocked</div>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.blocked}</div>
        </div>
        <div className="card">
          <div style={{ color: "#94a3b8", fontSize: 13 }}>Pending Human Review</div>
          <div style={{ fontSize: 32, fontWeight: 700 }}>{stats.pending_human_review}</div>
        </div>
      </div>

      <div className="card">
        <h2>Active Titles</h2>
        {titles.length === 0 ? (
          <p>
            No titles yet. <Link href="/ingest">Ingest your first movie clip</Link>.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Languages</th>
                <th>Progress</th>
                <th>Blockers</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {titles.map((title) => (
                <tr key={title.id}>
                  <td>{title.name}</td>
                  <td>
                    {title.source_language.toUpperCase()} → {title.language.toUpperCase()}
                  </td>
                  <td style={{ minWidth: 160 }}>
                    <div className="progress">
                      <span style={{ width: `${title.progress_pct}%` }} />
                    </div>
                    <small>{title.progress_pct}% ({title.segment_count} segments)</small>
                  </td>
                  <td>{title.blockers}</td>
                  <td>{statusBadge(title.status)}</td>
                  <td>
                    <Link href={`/titles/${title.id}`}>Open</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
