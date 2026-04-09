# WhatsApp Chat Analyzer

Production-grade, self-hostable WhatsApp chat analytics platform. Upload a `.txt`
export and get deep analytics — basic stats, temporal patterns, sentiment & topics,
social graphs, composite engagement scores, churn risk, and retention curves.

Built as a clean-room rewrite of an older notebook-based analyzer that dropped all
system events (joins, leaves, group renames) due to a regex that only matched
`user: message` lines. **This parser captures both user messages _and_ system
events**, correctly handles the narrow-no-break-space (`\u202f`) that WhatsApp
actually uses before AM/PM, and streams line-by-line for 100k+ line files.

## Stack

**Backend** FastAPI · Pydantic v2 · Pandas · scikit-learn · NetworkX · TextBlob · ReportLab
**Frontend** Next.js 14 (App Router) · TypeScript · Tailwind · Framer Motion · Recharts · react-force-graph
**Infra** Docker Compose · GitHub Actions

## Quick start

```bash
docker compose up --build
```

Frontend: http://localhost:3000 · Backend API docs: http://localhost:8000/docs

## Manual setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Environment variables

See `.env.example`. Key vars:

| Var | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/analyzer.db` | SQLite path |
| `UPLOAD_DIR` | `./data/uploads` | Where raw uploads live while parsing |
| `SESSION_TTL_HOURS` | `24` | Auto-delete after this many hours |
| `MAX_UPLOAD_SIZE_MB` | `50` | Upload size cap |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Comma-separated allowed origins |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend → backend URL |

## API

All endpoints under `/api/v1/`. Interactive docs at `/docs`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/upload` | Upload `.txt` export, returns `{session_id, status}` |
| `GET` | `/analysis/{sid}/status` | Poll until `done` |
| `GET` | `/analysis/{sid}/overview` | Group + per-user basic stats |
| `GET` | `/analysis/{sid}/users` | Per-user list (paginated) |
| `GET` | `/analysis/{sid}/temporal` | Hourly/daily/weekly/bursts/heatmap |
| `GET` | `/analysis/{sid}/nlp` | Sentiment, LDA topics, words, emojis, URLs |
| `GET` | `/analysis/{sid}/network` | Reply graph nodes/edges + centrality |
| `GET` | `/analysis/{sid}/engagement` | Composite scores, tiers, churn risk |
| `GET` | `/analysis/{sid}/retention` | Survival curve + cohorts |
| `GET` | `/export/{sid}/pdf` | Multi-page PDF report |
| `GET` | `/export/{sid}/csv` | CSV bundle (zipped) |
| `GET` | `/export/{sid}/html` | Standalone offline HTML dashboard |

## Architecture

```
┌──────────────────┐    upload .txt     ┌──────────────────────────┐
│  Next.js 14      │ ─────────────────▶ │  FastAPI                 │
│  Landing + Dash  │                    │  /api/v1                 │
│  Tailwind + FM   │ ◀── JSON/polling ──│  Pydantic v2             │
└──────────────────┘                    │                          │
                                        │  ┌────────────────────┐  │
                                        │  │  parser.py         │  │ ← the critical part
                                        │  └─────────┬──────────┘  │
                                        │            ▼              │
                                        │  ┌────────────────────┐  │
                                        │  │  analysis/*        │  │ ← basic / temporal / nlp
                                        │  │                    │  │   network / engagement / retention
                                        │  └─────────┬──────────┘  │
                                        │            ▼              │
                                        │  ┌────────────────────┐  │
                                        │  │  export/*          │  │ ← pdf / csv / html
                                        │  └────────────────────┘  │
                                        └──────────────────────────┘
```

## Parser guarantees

The parser handles:

- `dd/mm/yy`, `dd/mm/yyyy`, `mm/dd/yy`, `mm/dd/yyyy` (auto-detected)
- 12h and 24h clocks
- `\u202f` (narrow no-break space), `\u00a0` (no-break space), and regular space before AM/PM
- User messages *and* system events (joins, leaves, removes, renames, pins, deletes, encryption notices)
- Tilde-prefixed actors (`~ Username left`)
- Multi-line messages (continuation lines are appended)
- Messages whose content contains colons (`User: check this: https://...`)
- Media omitted, deleted, edited markers
- URL extraction, emoji extraction, mention detection

Run the test suite: `cd backend && pytest -q`. Verified against the sample
`Data/Data.txt`: **258 messages · 186 system events · 72 user messages · 0 parse errors.**

## Security

- UUID4 session IDs, auto-expired after `SESSION_TTL_HOURS`
- Uploads validated by extension, size, and content-preview
- Security headers (CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- All queries via SQLAlchemy ORM — no raw SQL
- Uploaded files deleted from disk after parsing; only derived analysis kept in memory
- No third-party services called — everything runs locally

## License

MIT
