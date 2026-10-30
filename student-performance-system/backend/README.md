# Backend — Flask API

Flask REST API + frontend server for the AI Based Student Performance Prediction and Personalized Learning Recommendation system.

## Run

```bash
cd student-performance-system
pip install -r backend/requirements.txt

# 1. Train the ML model (writes models/student_performance_model.pkl)
python ml-service/train_model.py

# 2. Start the Flask backend
python backend/app.py

# Open http://127.0.0.1:5000
```

The API starts even without a trained model — `/predict` then returns a friendly
error telling you to run the training script first.

## Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/` | Prediction form page (serves `frontend/templates/index.html`) |
| GET | `/health` | Liveness / readiness check (JSON) |
| POST | `/predict` | Predict final grade + performance level + recommendations |
| GET | `/history` | List past predictions |
| DELETE | `/history/<id>` | Delete a saved prediction |
| POST | `/api/auth/register` | Register a user (returns `{ token, role, username }`) |
| POST | `/api/auth/login` | Login (returns `{ token, role, username }`) |
| POST | `/api/auth/logout` | Invalidate the current token |

### POST /predict

Request body (UCI Student-Mat schema, target `G3` in 0–20):

```json
{
  "school": "GP", "sex": "F", "age": 17, "address": "U",
  "famsize": "GT3", "Pstatus": "A", "Medu": 3, "Fedu": 3,
  "Mjob": "services", "Fjob": "services", "reason": "course",
  "guardian": "mother", "traveltime": 1, "studytime": 3,
  "failures": 0, "schoolsup": "yes", "famsup": "yes", "paid": "no",
  "activities": "yes", "nursery": "yes", "higher": "yes", "internet": "yes",
  "romantic": "no", "famrel": 4, "freetime": 3, "goout": 3,
  "Dalc": 1, "Walc": 1, "health": 4, "absences": 4
}
```

Response:

```json
{
  "predicted_grade": 12.5,
  "performance_level": "Average",
  "recommendations": ["..."],
  "message": "Prediction generated and saved successfully."
}
```

## Structure

```
backend/
├── app.py            # Flask app: routes, validation, ML wiring, error handlers
├── database.py       # SQLite (default) / MySQL (optional) — predictions, users, etc.
├── check_database.py
├── requirements.txt
├── schema.sql        # full relational schema (MySQL dialect reference)
├── test_api.py       # legacy duplicate — REMOVED (suite lives in tests/)

# Supporting single-source modules (project root: student-performance-system/)
├── ml-service/
│   ├── dataset.py       # dataset loading + schema + encoding (single source)
│   └── recommender.py   # generate_recommendations()
├── models/               # trained model: student_performance_model.pkl, feature_columns.pkl
├── data/student-mat.csv
└── student_performance.db   # SQLite DB (created at project root on startup)

tests/
└── test_api.py       # pytest API suite (Flask test client, no server needed)
```

## Tests

```bash
python backend/app.py        # terminal 1
pytest tests/ -v             # terminal 2 (in-process test client — no server needed)
python backend/check_database.py
```

## Production

Run behind a production WSGI server:

```bash
# from repo root
gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:8000 --workers 2 --timeout 120 wsgi:app

# cross-platform (incl. Windows)
waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

# Docker
docker build -t student-performance .
docker run -d -p 8000:8000 student-performance
```

The app honors `HOST`, `PORT` and `FLASK_DEBUG` env vars. Health check: `GET /health`.
Full guide: `../../DEPLOYMENT.md`.

