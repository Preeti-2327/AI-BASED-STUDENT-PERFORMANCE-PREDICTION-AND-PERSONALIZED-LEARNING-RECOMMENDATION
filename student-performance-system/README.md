# AI Based Student Performance Prediction and Personalized Learning Recommendation

Single well-structured Flask + ML project. Dataset: `data/student-mat.csv` (UCI Student-Mat, target G3 0–20).

## Structure

```
student-performance-system/
├── backend/
│   ├── app.py              # Flask API: / , /predict, /history
│   └── database.py         # SQLite (student_performance.db)
├── frontend/
│   ├── templates/index.html    # working prediction form
│   ├── static/css/style.css
│   ├── static/js/script.js
│   ├── index.html, login.html, register.html
│   ├── admin/ student/ teacher/  # role pages
│   ├── css/ js/ assets/
├── ml-service/
│   ├── train_model.py      # train RandomForest -> models/
│   ├── predict.py          # CLI test prediction
│   ├── recommender.py      # generate_recommendations()
│   ├── data_analysis.py    # EDA -> graphs/
│   ├── data/README.txt notebooks/ reports/
├── data/student-mat.csv
├── models/                 # .pkl after training
├── tests/test_api.py
├── graphs/
├── docs/
│   ├── Student_Performance_Project_Detail.pdf
│   ├── legacy_mysql_schema.sql / legacy_mysql_seed.sql (old MySQL reference)
├── requirements.txt
```

## Run

```bash
cd student-performance-system
pip install -r requirements.txt
python ml-service/train_model.py
python backend/app.py
# open http://127.0.0.1:5000
python tests/test_api.py   # API smoke test (needs server running)
python ml-service/predict.py
python ml-service/data_analysis.py
```
