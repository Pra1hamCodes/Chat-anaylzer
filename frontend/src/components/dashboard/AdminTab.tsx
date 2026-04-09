"use client";
import { AlertTriangle, Ghost, Users, TrendingUp } from "lucide-react";
import { StatCard } from "@/components/ui/stat-card";

export function AdminTab({ engagement, retention }: { engagement: any; retention: any }) {
  if (!engagement) return <div className="text-white/50">Loading…</div>;

  const tierCounts: Record<string, number> = {};
  for (const t of Object.values(engagement.tiers || {})) {
    tierCounts[t as string] = (tierCounts[t as string] || 0) + 1;
  }

  const topScored = Object.entries(engagement.scores || {})
    .map(([user, s]: any) => ({ user, ...s }))
    .sort((a, b) => b.overall - a.overall)
    .slice(0, 15);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Engagement & retention</h1>
        <p className="text-white/50 mt-1">Composite engagement scores, member tiers, churn risk.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Churn risk" value={engagement.churn_risk.length} icon={AlertTriangle} />
        <StatCard label="Ghost members" value={engagement.ghost_members.length} icon={Ghost} />
        <StatCard label="Bounce rate" value={`${engagement.bounce_rate}%`} icon={TrendingUp} />
        <StatCard label="Scored users" value={Object.keys(engagement.scores).length} icon={Users} />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass p-6">
          <h2 className="text-lg font-semibold mb-4">Member tiers</h2>
          <div className="space-y-2">
            {Object.entries(tierCounts).map(([tier, n]) => (
              <div key={tier} className="flex items-center gap-3">
                <div className="w-24 text-sm text-white/60">{tier}</div>
                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-brand to-brand-purple" style={{
                    width: `${(n / Math.max(1, ...Object.values(tierCounts))) * 100}%`
                  }} />
                </div>
                <div className="w-10 text-right text-sm">{n}</div>
              </div>
            ))}
          </div>
        </div>

        {retention?.survival_curve && (
          <div className="glass p-6">
            <h2 className="text-lg font-semibold mb-4">Retention curve</h2>
            <div className="space-y-2">
              {Object.entries(retention.survival_curve).map(([k, v]: any) => (
                <div key={k} className="flex items-center gap-3">
                  <div className="w-16 text-sm text-white/60">{k}</div>
                  <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-brand" style={{ width: `${v}%` }} />
                  </div>
                  <div className="w-12 text-right text-sm">{v}%</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="glass p-6">
        <h2 className="text-lg font-semibold mb-4">Top engagement scores</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase text-white/50">
              <tr>
                <th className="text-left p-2">User</th>
                <th className="text-right p-2">Overall</th>
                <th className="text-right p-2">Msg Freq</th>
                <th className="text-right p-2">Consistency</th>
                <th className="text-right p-2">Response</th>
                <th className="text-right p-2">Content</th>
                <th className="text-center p-2">Tier</th>
              </tr>
            </thead>
            <tbody>
              {topScored.map((r: any) => (
                <tr key={r.user} className="border-t border-white/5">
                  <td className="p-2 truncate max-w-[200px]">{r.user}</td>
                  <td className="p-2 text-right font-semibold text-brand">{r.overall}</td>
                  <td className="p-2 text-right">{r.message_frequency_score}</td>
                  <td className="p-2 text-right">{r.consistency_score}</td>
                  <td className="p-2 text-right">{r.response_score}</td>
                  <td className="p-2 text-right">{r.content_score}</td>
                  <td className="p-2 text-center text-xs text-white/50">
                    {engagement.tiers[r.user]}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {engagement.churn_risk.length > 0 && (
        <div className="glass p-6">
          <h2 className="text-lg font-semibold mb-4 text-red-400">Churn risk members</h2>
          <div className="flex flex-wrap gap-2">
            {engagement.churn_risk.map((u: string) => (
              <span key={u} className="text-xs bg-red-500/10 border border-red-500/20 rounded-full px-3 py-1">
                {u}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
