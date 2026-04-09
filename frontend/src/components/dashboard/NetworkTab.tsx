"use client";
import dynamic from "next/dynamic";
import { useMemo } from "react";

const ForceGraph = dynamic(() => import("react-force-graph-2d"), { ssr: false });

const PALETTE = ["#00d4aa", "#7c3aed", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899", "#10b981"];

export function NetworkTab({ network }: { network: any }) {
  const data = useMemo(() => {
    if (!network) return { nodes: [], links: [] };
    return {
      nodes: network.nodes.map((n: any) => ({
        id: n.id,
        val: Math.max(2, Math.sqrt(n.size || 1)),
        color: PALETTE[(n.community || 0) % PALETTE.length],
      })),
      links: network.edges.map((e: any) => ({ source: e.source, target: e.target, value: e.weight })),
    };
  }, [network]);

  if (!network) return <div className="text-white/50">Loading…</div>;

  const rankByPR = Object.entries(network.centrality || {})
    .map(([user, m]: any) => ({ user, ...m }))
    .sort((a: any, b: any) => b.pagerank - a.pagerank)
    .slice(0, 10);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Social network</h1>
        <p className="text-white/50 mt-1">
          {network.nodes.length} nodes · {network.edges.length} edges ·{" "}
          {network.threads?.total_threads || 0} threads detected
        </p>
      </div>

      <div className="glass p-2 h-[520px]">
        {typeof window !== "undefined" && (
          // @ts-ignore
          <ForceGraph
            graphData={data}
            nodeLabel="id"
            linkColor={() => "rgba(255,255,255,0.15)"}
            backgroundColor="transparent"
            nodeRelSize={5}
            linkWidth={(l: any) => Math.min(4, Math.log2(l.value + 1))}
          />
        )}
      </div>

      <div className="glass p-6">
        <h2 className="text-lg font-semibold mb-4">Top 10 by PageRank</h2>
        <table className="w-full text-sm">
          <thead className="text-xs uppercase text-white/50">
            <tr><th className="text-left p-2">User</th><th className="text-right p-2">PageRank</th><th className="text-right p-2">In</th><th className="text-right p-2">Out</th></tr>
          </thead>
          <tbody>
            {rankByPR.map((r: any) => (
              <tr key={r.user} className="border-t border-white/5">
                <td className="p-2">{r.user}</td>
                <td className="p-2 text-right">{r.pagerank}</td>
                <td className="p-2 text-right">{r.in_degree}</td>
                <td className="p-2 text-right">{r.out_degree}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
