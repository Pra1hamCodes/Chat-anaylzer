"""Self-contained standalone HTML dashboard."""
from __future__ import annotations

import html
import json
from datetime import datetime

from app.storage.repository import SessionRecord


def render(rec: SessionRecord) -> str:
    ov = rec.overview
    meta = ov.metadata
    temporal = rec.temporal
    nl = rec.nlp

    payload = {
        "group": meta.group_name or "Unknown Group",
        "date_range": [str(meta.date_range[0]), str(meta.date_range[1])],
        "generated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "kpis": {
            "Total Messages": ov.total_messages,
            "User Messages": ov.total_user_messages,
            "System Events": meta.total_system_events,
            "Users": ov.unique_users,
            "Active Days": ov.active_days,
            "Msgs/Day": round(ov.msgs_per_day, 1),
            "Media": ov.total_media,
            "Links": ov.total_links,
        },
        "top_users": [(u.model_dump() if hasattr(u, "model_dump") else u.dict()) for u in ov.top_users[:20]],
        "hourly": temporal.hourly,
        "daily": temporal.daily,
        "by_dow": temporal.by_day_of_week,
        "heatmap": temporal.heatmap,
        "top_words": nl.top_words_global[:50],
        "top_emojis": nl.top_emojis_global[:20],
    }
    data_json = json.dumps(payload, default=str)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>WhatsApp Chat Analysis — {html.escape(payload['group'])}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
 body {{ font-family: system-ui, -apple-system, sans-serif; background: #0a0a0f; color: #eee;
        margin: 0; padding: 2rem; }}
 h1 {{ font-size: 2rem; margin: 0 0 .2rem; background: linear-gradient(90deg,#00d4aa,#7c3aed);
       -webkit-background-clip: text; color: transparent; }}
 .sub {{ opacity: .6; font-size: .9rem; margin-bottom: 2rem; }}
 .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
             gap: 1rem; margin-bottom: 2rem; }}
 .kpi {{ background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
        padding: 1rem; border-radius: .75rem; backdrop-filter: blur(12px); }}
 .kpi .label {{ font-size: .75rem; text-transform: uppercase; opacity: .6; letter-spacing: .05em; }}
 .kpi .val {{ font-size: 1.8rem; font-weight: 700; margin-top: .3rem; }}
 .chart {{ background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.08);
          padding: 1rem; border-radius: .75rem; margin-bottom: 1.2rem; }}
 table {{ width: 100%; border-collapse: collapse; }}
 th, td {{ text-align: left; padding: .4rem .6rem; border-bottom: 1px solid rgba(255,255,255,.08); font-size: .9rem; }}
 th {{ color: #7c3aed; }}
</style>
</head>
<body>
<h1>WhatsApp Chat Analysis</h1>
<div class="sub">{html.escape(payload['group'])} · {payload['date_range'][0]} → {payload['date_range'][1]}</div>
<div class="kpi-grid" id="kpis"></div>
<div class="chart" id="hourly"></div>
<div class="chart" id="daily"></div>
<div class="chart" id="dow"></div>
<div class="chart" id="topusers"></div>
<h2>Top Words</h2>
<div class="chart" id="words"></div>
<h2>Top Emojis</h2>
<div class="chart" id="emojis"></div>

<script>
const data = {data_json};
const kpiEl = document.getElementById('kpis');
for (const [k, v] of Object.entries(data.kpis)) {{
  const el = document.createElement('div');
  el.className = 'kpi';
  el.innerHTML = `<div class="label">${{k}}</div><div class="val">${{v}}</div>`;
  kpiEl.appendChild(el);
}}
const layout = {{ paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: {{ color: '#eee' }}, margin: {{ t: 30, l: 50, r: 20, b: 50 }} }};

Plotly.newPlot('hourly',
  [{{ x: Object.keys(data.hourly), y: Object.values(data.hourly), type:'bar',
      marker:{{color:'#00d4aa'}} }}],
  {{...layout, title:'Messages by hour'}}, {{responsive:true}});

Plotly.newPlot('daily',
  [{{ x: Object.keys(data.daily), y: Object.values(data.daily), type:'scatter',
      fill:'tozeroy', line:{{color:'#7c3aed'}} }}],
  {{...layout, title:'Daily volume'}}, {{responsive:true}});

Plotly.newPlot('dow',
  [{{ x: Object.keys(data.by_dow), y: Object.values(data.by_dow), type:'bar',
      marker:{{color:'#7c3aed'}} }}],
  {{...layout, title:'By day of week'}}, {{responsive:true}});

Plotly.newPlot('topusers',
  [{{ x: data.top_users.map(u=>u.messages), y: data.top_users.map(u=>u.user), type:'bar', orientation:'h',
      marker:{{color:'#00d4aa'}} }}],
  {{...layout, title:'Top users', height: 500}}, {{responsive:true}});

Plotly.newPlot('words',
  [{{ x: data.top_words.map(w=>w[1]), y: data.top_words.map(w=>w[0]), type:'bar', orientation:'h' }}],
  {{...layout, height: 700}}, {{responsive:true}});

Plotly.newPlot('emojis',
  [{{ x: data.top_emojis.map(e=>e[0]), y: data.top_emojis.map(e=>e[1]), type:'bar',
      marker:{{color:'#7c3aed'}} }}],
  layout, {{responsive:true}});
</script>
</body>
</html>"""
