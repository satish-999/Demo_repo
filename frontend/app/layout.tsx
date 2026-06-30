import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CineWeave RAE",
  description: "Governance scoring for dubbed film content",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <nav className="nav">
            <strong style={{ marginRight: 24 }}>CineWeave RAE</strong>
            <a href="/">Court Desk</a>
            <a href="/ingest">Ingest Title</a>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
