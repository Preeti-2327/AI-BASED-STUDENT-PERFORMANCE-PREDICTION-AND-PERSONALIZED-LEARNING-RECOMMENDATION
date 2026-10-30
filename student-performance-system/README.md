# AI Based Student Performance Prediction and Personalized Learning Recommendation

Single well-structured Flask + ML project. Dataset: `data/student-mat.csv` (UCI Student-Mat, target G3 0–20).

## Structure

```
student-performance-system/
├── backend/
│   ├── app.py              # Flask API: / , /predict, /history, /api/auth/*, /health, errors
│   ├── database.py         # SQLite (default) / MySQL (optional) data access
│   ├── check_database.py   # DB sanity check
│   ├── schema.sql          # relational schema reference
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── templates/          # Jinja2 (base.html, index.html, errors/)
│   ├── static/             # Flask static served at /static/
│   ├── css/ js/ assets/    # portal pages + design assets
│   ├── admin/ student/ teacher/   # role pages
│   ├── index.html, login.html, register.html
├── ml-service/
│   ├── dataset.py          # single source of truth (schema + encoding)
│   ├── train_model.py      # train RandomForest -> models/
│   ├── predict.py          # CLI test prediction
│   ├── recommender.py      # generate_recommendations()
│   ├── data_analysis.py    # EDA -> graphs/
│   ├── generate_reports.py # reports -> ml-service/reports/
│   ├── notebooks/ reports/ models/ data/
├── data/student-mat.csv
├── models/                 # .pkl after training
├── tests/test_api.py       # pytest API suite
├── graphs/                 # generated EDA charts
├── docs/                   # legacy MySQL schema/seed + project brief PDF
├── requirements.txt
└── student_performance.db # SQLite DB (auto-created at startup)
```

## Run

```bash
cd student-performance-system
pip install -r requirements.txt

python ml-service/train_model.py
python backend/app.py
# open http://127.0.0.1:5000

python ml-service/predict.py
python ml-service/data_analysis.py
python ml-service/generate_reports.py
pytest tests/ -v
python backend/check_database.py
```

## Deployment

Production serving is wired through:

- `backend/wsgi.py` — WSGI entry point (exposes the Flask `app`).
- `backend/app.py` — honors `HOST`, `PORT`, `FLASK_DEBUG` env vars.
- `Dockerfile` / `docker-compose.yml` — container deployment (auto-trains the model during build, gunicorn server, `/health` healthcheck).
- `render.yaml` — Render deploy blueprint. `Procfile` — Heroku / Railway start command.

```bash
# gunicorn (Linux / macOS)
gunicorn --chdir backend --bind 0.0.0.0:8000 --workers 2 --timeout 120 wsgi:app

# waitress (cross-platform, incl. Windows)
waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

# Docker
docker build -t student-performance .
docker run -d -p 8000:8000 student-performance
```

Health check: `GET /health` → `{"status":"ok","model_loaded":true}`

## Database

- Default: **SQLite** file at `student-performance-system/student_performance.db`
  (`SQLITE_PATH` env override). Engine switch: `DB_ENGINE=mysql` with `MYSQL_*` env vars.
- Full relational schema (users / teachers / subjects / students / predictions / habits / attendance):
  `backend/schema.sql` (MySQL dialect) + auto-created SQLite schema in `backend/database.py`.

## Notes

- `ml-service/dataset.py` is the single source of truth for dataset + field encoding
  (auto-detects UCI `G3` vs Kaggle `Exam_Score` schema).
- Frontend pages under `frontend/<role>/`, `frontend/login.html`, `frontend/register.html`
  use plain relative asset paths; Jinja pages under `frontend/templates/` use `url_for('static', ...)`.
