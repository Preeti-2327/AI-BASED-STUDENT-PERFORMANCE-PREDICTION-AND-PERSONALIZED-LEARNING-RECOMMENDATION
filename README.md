# 🎓 AI-Based Student Performance Prediction and Personalized Learning Recommendation

An end-to-end machine learning project that **predicts student academic performance** and **recommends personalized learning resources** based on each student's strengths, weaknesses, and study behavior.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Dataset](#-dataset)
- [Methodology](#-methodology)
- [Installation](#-installation)
- [Usage](#-usage)
- [Results](#-results)
- [Testing](#-testing)
- [Database](#-database)
- [Deployment](#-deployment)
- [Future Scope](#-future-scope)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🔍 Overview

Every student learns differently. Traditional one-size-fits-all teaching often fails to identify struggling students early. This project uses **Machine Learning** to:

1. **Predict** a student's final performance (grade / pass-fail / score) from academic and behavioral data.
2. **Identify** students at risk of underperforming.
3. **Recommend** personalized learning paths, topics, and resources to help each student improve.

---

## ✨ Features

- 📊 **Performance Prediction** – Predicts grades/scores using a Random Forest regressor.
- ⚠️ **At-Risk Detection** – Flags students who need early intervention.
- 🎯 **Personalized Recommendations** – Suggests study material and focus areas tailored to each student.
- 📈 **Data Visualization** – Distribution, correlation heatmap, study-time / attendance plots (`graphs/`).
- 🖥️ **Interactive Web App** – Flask + vanilla-JS portals (admin / teacher / student) served by the backend.
- 🔬 **Model Comparison & Reports** – `ml-service/generate_reports.py` writes `ml-service/reports/`.

---

## 🛠 Tech Stack

| Category            | Tools                                             |
| ------------------- | ------------------------------------------------ |
| Language            | Python 3.9+                                       |
| Data Processing     | Pandas, NumPy                                     |
| Machine Learning    | Scikit-learn, Random Forest                      |
| Recommendation      | Rule-based personalized tips (scales with schema) |
| Visualization       | Matplotlib, Seaborn, Plotly                     |
| Web App             | Flask, vanilla JS (no frontend build step)       |
| Database            | SQLite (default) / MySQL (optional)              |
| Environment         | Jupyter Notebook, VS Code                        |

---

## 📁 Project Structure

```
.
├── README.md
└── student-performance-system/
    ├── backend/                 # Flask API + database layer
    │   ├── app.py               # / , /predict, /history, /api/auth/*, /health, errors
    │   ├── database.py          # SQLite (default) / MySQL (optional) data access
    │   ├── check_database.py   # DB sanity check
    │   ├── schema.sql          # full relational schema (MySQL dialect reference)
    │   ├── requirements.txt
    │   └── README.md
    ├── frontend/                # Static front-end served by Flask
    │   ├── templates/          # Jinja2 (base.html, index.html, errors/)
    │   ├── static/             # Flask static (/static/*) — css/js/images
    │   ├── css/, js/, assets/ # standalone portal pages + design assets
    │   ├── admin/, student/, teacher/
    │   ├── index.html, login.html, register.html
    ├── ml-service/              # ML pipeline
    │   ├── dataset.py          # single source of truth (schema + encoding)
    │   ├── train_model.py, predict.py, recommender.py, data_analysis.py
    │   ├── generate_reports.py
    │   ├── notebooks/, reports/, models/, data/
    ├── data/student-mat.csv
    ├── models/                  # trained .pkl artifacts
    ├── tests/test_api.py       # pytest API suite
    ├── graphs/                  # generated EDA charts
    ├── docs/                    # legacy MySQL schema/seed + project brief PDF
    ├── requirements.txt
    └── student_performance.db  # SQLite DB (auto-created)
```

Run (development):

```bash
cd student-performance-system
pip install -r requirements.txt
python ml-service/train_model.py
python backend/app.py
# open http://127.0.0.1:5000
```

Run (production):

```bash
pip install -r student-performance-system/requirements.txt
python student-performance-system/ml-service/train_model.py
gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:8000 --workers 2 --timeout 120 wsgi:app
# cross-platform (incl. Windows): cd student-performance-system/backend && waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

# open http://127.0.0.1:8000
# health: http://127.0.0.1:8000/health
```

---

## 📂 Dataset

- **Source:** UCI Student Performance Dataset (`data/student-mat.csv`, `;` separator, target `G3` 0–20).
- **Records:** 395 students · 33 columns (demographics, academic history, study habits, social factors, `G1`, `G2`, `G3`).
- **Key Features:** study time, absences, failures, family/school support, lifestyle, prior grades.
- **Target:** Final grade (`G3`).

---

## ⚙️ Methodology

```
Data Collection → Data Cleaning → EDA → Feature Engineering
      → Model Training → Evaluation → Recommendation Engine → Deployment
```

1. **Data Preprocessing** – Handling missing values, encoding categorical variables, scaling features.
2. **Exploratory Data Analysis** – Understanding patterns and feature correlations (`ml-service/data_analysis.py` → `graphs/`).
3. **Model Training** – Random Forest (`ml-service/train_model.py`).
4. **Evaluation** – MAE, RMSE, R², ±1/±2 grade-point accuracy (`ml-service/generate_reports.py` → `ml-service/reports/`).
5. **Recommendation Engine** – Maps weak areas to suitable topics, courses, and study strategies.
6. **Deployment** – Flask backend serving the API + multi-role frontend.

---

## 🚀 Installation

```bash
git clone <your-repo>
cd AI-BASED-STUDENT-PERFORMANCE-PREDICTION-AND-PERSONALIZED-LEARNING-RECOMMENDATION

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

---

## 💻 Usage

```bash
# 1. Train the model (writes models/*.pkl)
python ml-service/train_model.py

# 2. Generate EDA charts + reports
python ml-service/data_analysis.py
python ml-service/generate_reports.py

# 3. CLI prediction with default student profile
python ml-service/predict.py

# 4. Start the Flask backend (API + frontend on :5000)
python backend/app.py

# 5. Run the API test suite
pytest tests/ -v

# 6. DB sanity check
python backend/check_database.py
```

Open **http://127.0.0.1:5000** → prediction form · predictions are saved to the DB and listed under `/history`.

---

## 📊 Results

| Model               | MAE | RMSE | R²  |
| ------------------- | --- | ---- | --- |
| Random Forest      | 3.08 | 3.87 | 0.27 |

> R² is modest **by design**: prior-period grades (`G1`/`G2`) are excluded from features to avoid leakage; the model relies on habits / demographics / support.

---

## 🚀 Deployment

The project ships with **production-grade deployment artifacts:

- 🐳 **Docker** — `Dockerfile` + `docker-compose.yml` at the repo root (auto-trains the ML model during build, serves with gunicorn on :8000, built-in healthcheck).
- 🌐 **Render** — `render.yaml` blueprint (build: train model, start: gunicorn, health check: `/health`).
- 🟣 **Heroku / Railway** — root `Procfile` (`web: gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`).

### Quick production run (local / any host)

```bash
pip install -r student-performance-system/requirements.txt
python student-performance-system/ml-service/train_model.py
gunicorn --chdir student-performance-system/backend --bind 0.0.0.0:8000 --workers 2 --timeout 120 wsgi:app
# cross-platform (incl. Windows): cd student-performance-system/backend && waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

# open http://127.0.0.1:8000
# health: http://127.0.0.1:8000/health
```

### Docker

```bash
docker build -t student-performance .
docker run -d -p 8000:8000 -e SQLITE_PATH=/app/student-performance-system/student_performance.db student-performance

# or with compose
docker compose up -d --build
```

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for the full guide (environment variables, Render / Heroku / Railway steps, troubleshooting, verification).

**Live endpoints:** `GET /health`, `GET /`, `POST /predict`, `GET /history`, `DELETE /history/<id>`, `POST /api/auth/*`.

---

## 🔮 Future Scope

- Integration with real-time Learning Management Systems (LMS)
- Deep learning models (LSTM / Neural Networks) for sequential performance tracking
- Explainable AI (SHAP / LIME) to show *why* a prediction was made
- Teacher dashboard with class-level analytics
- Adaptive quizzes and reinforcement-learning-based recommendations
- Mobile application support

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.

---

## ⭐ If you found this project useful, please consider giving it a star!
