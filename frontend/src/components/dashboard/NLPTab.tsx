"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";

const COLORS = ["#00d4aa", "#7c3aed", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899"];

export function NLPTab({ nlp }: { nlp: any }) {
  if (!nlp) return <div className="text-white/50">Loading…</div>;
  const words = (nlp.top_words_global || []).slice(0, 25).map(([w, n]: any) => ({ w, n }));
  const emojis = (nlp.top_emojis_global || []).slice(0, 15).map(([e, n]: any) => ({ e, n }));
  const sentiment = Object.entries(nlp.daily_sentiment || {}).map(([d, s]) => ({ d, s }));
  const domainCats = Object.entries(nlp.domain_categories || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Sentiment & language</h1>
        <p className="text-white/50 mt-1">LDA topics, word frequencies, emojis, URL domains.</p>
      </div>

      <Card title="Group sentiment over time">
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={sentiment}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="d" stroke="rgba(255,255,255,0.3)" fontSize={11} />
            <YAxis domain={[-1, 1]} stroke="rgba(255,255,255,0.3)" fontSize={11} />
            <Tooltip contentStyle={tip} />
            <Line type="monotone" dataKey="s" stroke="#7c3aed" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="Top words">
          <ResponsiveContainer width="100%" height={420}>
            <BarChart data={words} layout="vertical">
              <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <YAxis type="category" dataKey="w" stroke="rgba(255,255,255,0.3)" width={100} fontSize={11} />
              <Tooltip contentStyle={tip} />
              <Bar dataKey="n" fill="#00d4aa" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Top emojis">
          <div className="flex flex-wrap gap-3 text-center">
            {emojis.map((e: any) => (
              <div key={e.e} className="glass p-3 min-w-[70px]">
                <div className="text-3xl">{e.e}</div>
                <div className="text-xs text-white/50 mt-1">{e.n}</div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {nlp.topics?.length > 0 && (
        <Card title="Detected topics (LDA)">
          <div className="grid md:grid-cols-2 gap-4">
            {nlp.topics.map((t: any) => (
              <div key={t.id} className="p-4 rounded-lg border border-white/10">
                <div className="text-xs text-brand uppercase mb-2">Topic {t.id}</div>
                <div className="flex flex-wrap gap-1.5">
                  {t.keywords.slice(0, 8).map((k: string) => (
                    <span key={k} className="text-xs bg-white/5 border border-white/10 rounded-full px-2 py-1">{k}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {domainCats.length > 0 && (
        <Card title="Shared URL categories">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={domainCats} dataKey="value" nameKey="name" outerRadius={100} label>
                {domainCats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={tip} />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}

const tip = { background: "#12121a", border: "1px solid rgba(255,255,255,.1)", borderRadius: 8 };
function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="glass p-6"><h2 className="text-lg font-semibold mb-4">{title}</h2>{children}</div>;
}
