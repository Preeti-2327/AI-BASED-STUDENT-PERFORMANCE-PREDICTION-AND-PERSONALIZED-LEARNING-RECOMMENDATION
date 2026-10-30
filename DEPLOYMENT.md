# 🚀 Deployment Guide — AI-Based Student Performance Prediction & Personalized Learning Recommendation

Complete, production-oriented deployment instructions for the AI Student Performance
Prediction & Personalized Learning Recommendation system.

The application is a **Flask + Random Forest** service that:

1. Serves the multi-role frontend (Jinja2 templates + vanilla JS) from the same Flask app.
2. Exposes ML API endpoints: `GET /health`, `POST /predict`, `GET /history`, `DELETE /history/<id>`.
3. Exposes auth endpoints: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`.
4. Persists users & predictions (SQLite by default, MySQL optional).

---

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Environment Variables](#-environment-variables)
- [Local Production Run (gunicorn)](#-local-production-run-gunicorn)
- [Docker Deployment](#-docker-deployment)
- [Docker Compose](#-docker-compose)
- [Render](#-render)
- [Heroku](#-heroku)
- [Railway](#-railway)
- [Health Check & Verification](#-health-check--verification)
- [Demo Accounts](#-demo-accounts)
- [Troubleshooting](#-troubleshooting)

---

## 🏗 Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                        Flask App                            │
│  ┌──────────────┐   ┌───────────────────────────────────┐  │
│  │  Frontend    │   │  ML / API Layer                   │  │
│  │  /          ───►│  /predict  (RandomForest + Recommender)│
│  │  static     ───►│  /history                        │  │
│  └──────────────┘   └───────────────────────────────────┘  │
│                                                            │
│  SQLite (default) / MySQL (optional) ← predictions, users   │
└────────────────────────────────────────────────────────────┘
```

- **Web server:** gunicorn (WSGI) — 2 workers, 120 s timeout.
- **App entry:** `student-performance-system/backend/wsgi.py` → `app` object.
- **Model:** `student-performance-system/models/student_performance_model.pkl`
  (+ `feature_columns.pkl`, `schema_meta.pkl`). **Must be trained before serving**
  (training happens automatically in the Docker image / Render build command).

---

## 🔧 Environment Variables

| Variable         | Default                | Description                                                        |
| ---------------- | ---------------------- | ------------------------------------------------------------------ |
| `PORT`           | `5000` (Docker: `8000`) | Port the WSGI server binds to.                                      |
| `HOST`           | `0.0.0.0`              | Interface the Flask dev server binds to (`app.run`).               |
| `FLASK_DEBUG`   | `0`                    | Set to `1`/`true` to enable Flask debug mode (never in production). |
| `SQLITE_PATH`   | `<project>/student_performance.db` | Path to the SQLite DB file.                    |
| `DB_ENGINE`     | `sqlite`               | `sqlite` (default) or `mysql`.                                     |
| `MYSQL_HOST`    | `127.0.0.1`            | MySQL host (required when `DB_ENGINE=mysql`).                     |
| `MYSQL_PORT`    | `3306`                 | MySQL port.                                                        |
| `MYSQL_USER`    | `root`                 | MySQL user.                                                        |
| `MYSQL_PASSWORD`| *(empty)*              | MySQL password.                                                    |
| `MYSQL_DB`      | `student_performance_db` | MySQL database name.                                             |

---

## 💻 Local Production Run (gunicorn)

```bash
# 1. (One-time) create venv + install deps
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r student-performance-system/requirements.txt

# 2. Train the ML model (writes models/student_performance_model.pkl)
python student-performance-system/ml-service/train_model.py

# 3. Start production server
#    Linux / macOS (gunicorn):
gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:8000 --workers 2 --timeout 120 wsgi:app
#    Cross-platform incl. Windows (waitress):
#    cd student-performance-system/backend
#    waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

# 4. Verify
curl http://127.0.0.1:8000/health
# → {"status":"ok","model_loaded":true}

# Open http://127.0.0.1:8000
```

**Docker alternative (same result):**

```bash
docker build -t student-performance .
docker run -d -p 8000:8000 -e SQLITE_PATH=/app/student-performance-system/student_performance.db student-performance
```

---

## 🐳 Docker Deployment

The repository ships a production-ready `Dockerfile` (Python 3.11 slim base,
dependency caching, automatic model training, gunicorn, built-in healthcheck).

### Build & run

```bash
docker build -t student-performance .
docker run -d -p 8000:8000 \
  -e SQLITE_PATH=/app/student-performance-system/student_performance.db \
  --name student-performance \
  student-performance
```

### Docker Compose

```bash
docker compose up -d --build
docker compose logs -f web
docker compose down
```

The container listens on **0.0.0.0:8000** and exposes the health endpoint at
`http://localhost:8000/health`.

### Image details

- Base image: `python:3.11-slim`
- Installs `student-performance-system/requirements.txt` (+ gunicorn).
- Copies the full `student-performance-system/` source tree.
- Runs `ml-service/train_model.py` during build → model artifacts are baked in.
- `EXPOSE 8000`, `ENV PORT=8000`, `FLASK_DEBUG=0`.
- Gunicorn: `--workers 2 --timeout 120 wsgi:app`.
- Docker `HEALTHCHECK` hits `GET /health`.

---

## 🌐 Render

The repo includes `render.yaml` (Infrastructure-as-Code blueprint):

1. Push the repo to GitHub.
2. In Render → **New → Blueprint** → select this repository.
3. Render reads `render.yaml`, builds and deploys automatically.
4. After deploy: open the generated URL and verify `GET /health`.

Manual equivalent:

- **Runtime:** Python
- **Root directory:** `student-performance-system`
- **Build command:** `pip install -r requirements.txt && python ml-service/train_model.py`
- **Start command:** `gunicorn --chdir backend --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`
- **Health check path:** `/health`
- **Python version:** `3.11.9`
- **Port:** `10000` (Render assigns; the app reads `$PORT`)

---

## 🟣 Heroku

Uses the root `Procfile`:

```
web: gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
```

```bash
heroku create <your-app-name>
heroku stack:set container        # if deploying the Dockerfile-based app
# or for classic buildpack deploys:
# heroku buildpacks:add heroku/python
git push heroku main
```

Set at least one config var:

```bash
heroku config:set PORT=5000 SQLITE_PATH=/app/student_performance.db
```

---

## 🚂 Railway

Railway auto-detects a `Procfile` / `Dockerfile`. Simplest path:

1. Create a new Railway project → **Deploy from GitHub**.
2. Railway detects the repo → uses `Dockerfile` if present (Railway prefers
   Dockerfile when detected).
3. Set environment variables if using MySQL externally; defaults work with SQLite.

Start command (Railway injects `$PORT`):

```
gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
```

---

## 🪂 Fly.io

The repo includes `fly.toml` (Docker-based deployment):

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login + create app
fly auth login
fly apps create student-performance

# Deploy
fly deploy

# Open
fly open
```

The app listens on port 8000 (`[http_service] internal_port = 8000`), health check path defaults to `/health`.

---

## ✅ Health Check & Verification

After any deployment, verify:

```bash
# 1. Health / readiness
curl -f http://localhost:8000/health
# → {"status":"ok","model_loaded":true}

# 2. Frontend prediction page
curl -f http://localhost:8000/

# 3. End-to-end prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "school": "GP", "sex": "F", "age": 17, "address": "U",
  "famsize": "GT3", "Pstatus": "A", "Medu": 3, "Fedu": 3,
  "Mjob": "services", "Fjob": "services", "reason": "course",
  "guardian": "mother", "traveltime": 1, "studytime": 3,
  "failures": 0, "schoolsup": "yes", "famsup": "yes", "paid": "no",
  "activities": "no", "nursery": "yes", "higher": "yes", "internet": "yes",
  "romantic": "no", "famrel": 4, "freetime": 3, "goout": 3,
  "Dalc": 1, "Walc": 1, "health": 4, "absences": 4
}
JSON
```

Expected response: `200` with `predicted_grade`, `performance_level`,
`recommendations` and `message`.

Run the automated suite as a final smoke test:

```bash
pytest student-performance-system/tests/ -v
```

---

## 👥 Demo Accounts

| Role    | Email                | Password   |
| ------- | -------------------- | ---------- |
| Admin   | `admin@school.edu`  | `admin123` |
| Teacher | `meera@school.edu`  | `teacher123` |
| Student | `student@example.com`| `student123` |

---

## 🛠 Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `WARNING: Model not found` on boot | Run `python ml-service/train_model.py` (Docker: training runs automatically). |
| `WARNING: dataset not found` | Place `data/student-mat.csv` at project root. |
| 500 on `/predict` | Check server logs; model + dataset must be present. |
| Auth 401 / fallback to demo mode | Backend running? Login uses `/api/auth/*` — verify `BACKEND_URL` in `frontend/js/config.js`. |
| SQLite locked | Single gunicorn worker usage is default here (`--workers 2` OK for demo; raise `--workers 1` for heavy write load. |
| Port already in use | Change `$PORT` / `--bind` accordingly. |
| MySQL connection errors | Set `DB_ENGINE=mysql` + `MYSQL_*` vars; ensure `mysql` server running & schema applied (`backend/schema.sql`). |

---

## 🔮 Next Steps (planned production upgrades)

- Real-time LMS integration / API keys.
- Deep learning (LSTM) & SHAP explainability.
- Kubernetes / multi-service orchestration (ML inference sidecar).
- TLS termination / reverse proxy (nginx / Traefik) in front of gunicorn.
