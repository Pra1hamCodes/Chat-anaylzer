"use client";
import { useMemo, useState } from "react";
import { Search } from "lucide-react";

export function UsersTab({ overview }: { overview: any }) {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<"messages" | "words" | "active_days">("messages");

  const users = useMemo(() => {
    if (!overview) return [];
    let rows = [...overview.top_users];
    if (q) rows = rows.filter((u: any) => u.user.toLowerCase().includes(q.toLowerCase()));
    rows.sort((a: any, b: any) => b[sort] - a[sort]);
    return rows;
  }, [overview, q, sort]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-bold">Users</h1>
        <p className="text-white/50 mt-1">Per-user breakdown, sortable & searchable.</p>
      </div>
      <div className="glass p-4 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search users"
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-brand/50"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as any)}
          className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm"
        >
          <option value="messages">Sort: messages</option>
          <option value="words">Sort: words</option>
          <option value="active_days">Sort: active days</option>
        </select>
      </div>

      <div className="glass overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-white/60 text-xs uppercase">
            <tr className="border-b border-white/5">
              <th className="text-left p-3">#</th>
              <th className="text-left p-3">User</th>
              <th className="text-right p-3">Messages</th>
              <th className="text-right p-3">Words</th>
              <th className="text-right p-3">Media</th>
              <th className="text-right p-3">Links</th>
              <th className="text-right p-3">Active Days</th>
              <th className="text-right p-3">% of total</th>
              <th className="text-center p-3">Top Emoji</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u: any, i: number) => (
              <tr key={u.user} className="border-b border-white/5 hover:bg-white/[0.02]">
                <td className="p-3 text-white/40">{i + 1}</td>
                <td className="p-3 font-medium truncate max-w-[220px]">{u.user}</td>
                <td className="p-3 text-right">{u.messages}</td>
                <td className="p-3 text-right">{u.words}</td>
                <td className="p-3 text-right">{u.media}</td>
                <td className="p-3 text-right">{u.links}</td>
                <td className="p-3 text-right">{u.active_days}</td>
                <td className="p-3 text-right">{u.pct_of_total.toFixed(1)}%</td>
                <td className="p-3 text-center text-lg">{u.top_emoji || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
