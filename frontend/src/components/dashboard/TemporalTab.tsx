"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

export function TemporalTab({ temporal }: { temporal: any }) {
  if (!temporal) return <div className="text-white/50">Loading…</div>;
  const hourly = Object.entries(temporal.hourly).map(([h, n]) => ({ h, n }));
  const dow = Object.entries(temporal.by_day_of_week).map(([d, n]) => ({ d: d.slice(0, 3), n }));
  const daily = Object.entries(temporal.daily).map(([d, n]) => ({ d, n }));
  const cum = Object.entries(temporal.cumulative).map(([d, n]) => ({ d, n }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Timeline & patterns</h1>
        <p className="text-white/50 mt-1">
          Busiest hour: <span className="text-brand font-semibold">{temporal.busiest_hour}:00</span> · Busiest day:{" "}
          <span className="text-brand font-semibold">{temporal.busiest_day_name}</span>
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card title="Messages by hour">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={hourly}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="h" stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <Tooltip contentStyle={tip} />
              <Bar dataKey="n" fill="#00d4aa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="By day of week">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={dow}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="d" stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} />
              <Tooltip contentStyle={tip} />
              <Bar dataKey="n" fill="#7c3aed" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Cumulative growth">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={cum}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="d" stroke="rgba(255,255,255,0.3)" fontSize={11} />
            <YAxis stroke="rgba(255,255,255,0.3)" fontSize={11} />
            <Tooltip contentStyle={tip} />
            <Line type="monotone" dataKey="n" stroke="#00d4aa" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {temporal.bursts?.length > 0 && (
        <Card title={`Bursts detected (${temporal.bursts.length})`}>
          <ul className="divide-y divide-white/5 text-sm">
            {temporal.bursts.slice(0, 10).map((b: any) => (
              <li key={b.date} className="py-2 flex justify-between">
                <span>{b.date}</span>
                <span className="text-brand">{b.messages} msgs (z={b.zscore})</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

const tip = { background: "#12121a", border: "1px solid rgba(255,255,255,.1)", borderRadius: 8 };
function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="glass p-6">
      <h2 className="text-lg font-semibold mb-4">{title}</h2>
      {children}
    </div>
  );
}
