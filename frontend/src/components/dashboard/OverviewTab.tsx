"use client";
import {
  MessageSquare, Users, Calendar, Image as ImageIcon, Link2, Zap, Smile, Hash,
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid,
} from "recharts";
import { StatCard } from "@/components/ui/stat-card";
import { formatNumber } from "@/lib/utils";

export function OverviewTab({ overview, temporal, loading }: { overview: any; temporal: any; loading: boolean }) {
  if (loading || !overview) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="glass h-28 animate-pulse" />
        ))}
      </div>
    );
  }

  const daily = temporal
    ? Object.entries(temporal.daily).map(([date, n]) => ({ date, n: n as number }))
    : [];
  const topUsers = (overview.top_users || []).slice(0, 10).map((u: any) => ({
    user: u.user.length > 16 ? u.user.slice(0, 14) + "…" : u.user,
    messages: u.messages,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl md:text-4xl font-bold">
          <span className="gradient-text">{overview.metadata.group_name || "Chat"}</span>
        </h1>
        <p className="text-white/50 mt-1 text-sm">
          {overview.metadata.date_range[0]} → {overview.metadata.date_range[1]} · {overview.metadata.detected_format}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Messages" value={formatNumber(overview.total_messages)} icon={MessageSquare} delay={0.0} />
        <StatCard label="Users" value={overview.unique_users} icon={Users} delay={0.05} />
        <StatCard label="Active Days" value={overview.active_days} icon={Calendar} delay={0.1} />
        <StatCard label="Msgs / Day" value={overview.msgs_per_day.toFixed(1)} icon={Zap} delay={0.15} />
        <StatCard label="Words" value={formatNumber(overview.total_words)} icon={Hash} delay={0.2} />
        <StatCard label="Media" value={formatNumber(overview.total_media)} icon={ImageIcon} delay={0.25} />
        <StatCard label="Links" value={formatNumber(overview.total_links)} icon={Link2} delay={0.3} />
        <StatCard label="Emojis" value={formatNumber(overview.total_emojis)} icon={Smile} delay={0.35} />
      </div>

      <div className="glass p-6">
        <h2 className="text-lg font-semibold mb-4">Daily volume</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={daily}>
              <defs>
                <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00d4aa" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#00d4aa" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <Tooltip contentStyle={{ background: "#12121a", border: "1px solid rgba(255,255,255,.1)", borderRadius: 8 }} />
              <Area type="monotone" dataKey="n" stroke="#00d4aa" fill="url(#g)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h2 className="text-lg font-semibold mb-4">Top 10 users</h2>
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={topUsers} layout="vertical">
                <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" stroke="rgba(255,255,255,0.3)" fontSize={11} />
                <YAxis type="category" dataKey="user" stroke="rgba(255,255,255,0.3)" width={110} fontSize={11} />
                <Tooltip contentStyle={{ background: "#12121a", border: "1px solid rgba(255,255,255,.1)", borderRadius: 8 }} />
                <Bar dataKey="messages" fill="#7c3aed" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass p-6">
          <h2 className="text-lg font-semibold mb-4">Activity heatmap</h2>
          <Heatmap matrix={temporal?.heatmap} />
        </div>
      </div>
    </div>
  );
}

function Heatmap({ matrix }: { matrix?: number[][] }) {
  if (!matrix) return <div className="text-white/40 text-sm">Loading…</div>;
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const max = Math.max(1, ...matrix.flat());
  return (
    <div className="overflow-x-auto">
      <div className="grid" style={{ gridTemplateColumns: "auto repeat(24, minmax(18px, 1fr))", gap: 3 }}>
        <div />
        {Array.from({ length: 24 }, (_, h) => (
          <div key={h} className="text-[9px] text-white/30 text-center">{h}</div>
        ))}
        {matrix.map((row, i) => (
          <>
            <div key={`d${i}`} className="text-[10px] text-white/40 pr-2 text-right">{days[i]}</div>
            {row.map((v, h) => (
              <div
                key={`${i}-${h}`}
                title={`${days[i]} ${h}:00 — ${v} msgs`}
                className="rounded-sm"
                style={{
                  background: v > 0 ? `rgba(0,212,170,${0.15 + (v / max) * 0.85})` : "rgba(255,255,255,0.03)",
                  aspectRatio: "1 / 1",
                }}
              />
            ))}
          </>
        ))}
      </div>
    </div>
  );
}
