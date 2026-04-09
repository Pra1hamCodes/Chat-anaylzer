"use client";
import { FileText, FileSpreadsheet, Globe } from "lucide-react";
import { exportUrl } from "@/lib/api";

const OPTIONS = [
  { fmt: "pdf" as const, icon: FileText, title: "PDF Report", desc: "Multi-page branded report with charts, tables and key metrics. Great for sharing." },
  { fmt: "csv" as const, icon: FileSpreadsheet, title: "CSV Bundle", desc: "ZIP containing messages, user stats, and daily volume CSVs." },
  { fmt: "html" as const, icon: Globe, title: "Interactive HTML", desc: "Standalone dashboard with embedded Plotly charts. Works offline." },
];

export function ExportTab({ sessionId }: { sessionId: string }) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Export</h1>
        <p className="text-white/50 mt-1">Download your analysis in multiple formats.</p>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {OPTIONS.map((o) => (
          <a
            key={o.fmt}
            href={exportUrl(sessionId, o.fmt)}
            target="_blank"
            rel="noopener noreferrer"
            className="glass p-6 hover:border-brand/50 transition-all group"
          >
            <div className="inline-flex w-12 h-12 items-center justify-center rounded-xl bg-brand/10 mb-4 group-hover:scale-110 transition-transform">
              <o.icon className="w-6 h-6 text-brand" />
            </div>
            <h3 className="text-lg font-semibold mb-2">{o.title}</h3>
            <p className="text-sm text-white/60 mb-4">{o.desc}</p>
            <span className="text-sm text-brand">Download →</span>
          </a>
        ))}
      </div>
    </div>
  );
}
