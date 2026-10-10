# Model Evaluation — Student Performance (G3)

Generated: 2026-10-10T03:15:05.295423+00:00

- Model: `RandomForestRegressor(n_estimators=200, random_state=42)`
- Features: **39** (one-hot, `drop_first=True`; excluded ['G1', 'G2'])
- Split: train **316** / test **79** (`test_size=0.2`, `random_state=42`)
- Retrained this run: **False**

## Metrics (test set)

| Metric | Value | Meaning |
|---|---|---|
| MAE | 3.082 | avg. grade-point error |
| RMSE | 3.869 | penalizes large errors |
| R² | 0.27 | variance explained |
| Within ±1 pt | 0.19 | share of predictions |
| Within ±2 pt | 0.392 | share of predictions |

## Top 5 features

| Feature | Importance |
|---|---|
| absences | 0.1904 |
| failures | 0.1452 |
| health | 0.0522 |
| goout | 0.0517 |
| age | 0.0414 |

## Sample actual vs predicted

| Actual | Predicted |
|---|---|
| 10 | 9.68 |
| 12 | 9.72 |
| 5 | 10.1 |
| 10 | 12.29 |
| 9 | 9.98 |
| 13 | 8.85 |
| 18 | 14.34 |
| 6 | 11.36 |
| 0 | 10.71 |
| 14 | 12.22 |

Artifacts: `models/student_performance_model.pkl`, `models/feature_columns.pkl`.
