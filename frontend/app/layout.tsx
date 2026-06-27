import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CineWeave RAE POC",
  description: "Proof-of-concept governance scoring for dubbed content",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <nav className="nav">
            <a href="/">Court Desk</a>
            <a href="/ingest">Ingest Title</a>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
