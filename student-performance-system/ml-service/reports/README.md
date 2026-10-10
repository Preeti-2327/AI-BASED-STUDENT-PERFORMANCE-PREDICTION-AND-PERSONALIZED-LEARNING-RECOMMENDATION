# Reports — `ml-service/reports/`

Auto-generated, reproducible ML reports. Never hand-edit the generated files —
regenerate with:

```bash
python ml-service/generate_reports.py
```

## Files

| File | What | Format |
|---|---|---|
| `model_evaluation.json` | Test metrics (MAE/RMSE/R², ±1/±2pt accuracy), split info, sample predictions | machine-readable |
| `model_evaluation.md` | Model card: config, metrics table, top-5 features, sample table | human-readable |
| `eda_summary.json` | Dataset profile: shape, missing, target stats, level distribution, top correlations | machine-readable |
| `eda_summary.md` | Same profile as readable tables | human-readable |
| `feature_importance.csv` | All one-hot features ranked by RandomForest importance | CSV |

## Key facts (regenerate to refresh)

- Dataset: `data/student-mat.csv` (UCI Student-Mat), target **G3 (0–20)**.
- Model: `RandomForestRegressor(n_estimators=200, random_state=42)`.
- **G1/G2 excluded** from features to avoid leakage (prior-period grades would inflate scores).
- Split: `test_size=0.2, random_state=42`.
- Charts live in `graphs/` (via `ml-service/data_analysis.py`), not duplicated here.

## Latest run (2026-10-10)

- MAE **3.08**, RMSE **3.87**, R² **0.27** — honest baseline without G1/G2.
- R² is modest *by design*: without prior grades the model relies on habits/demographics only. Keep G1/G2 out of training for early-warning use; if you need higher R² for final-term forecasting, train a separate `G1+G2` variant and document it as such.
