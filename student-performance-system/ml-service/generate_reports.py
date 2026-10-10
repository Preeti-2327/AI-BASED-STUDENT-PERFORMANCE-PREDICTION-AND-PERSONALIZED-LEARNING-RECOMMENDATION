"""Generate industry-standard ML reports for ml-service/reports/.

Run:  python ml-service/generate_reports.py
Reads: data/student-mat.csv + models/*.pkl (trains if missing)
Writes:
  reports/model_evaluation.json   machine-readable metrics
  reports/model_evaluation.md     human-readable model card
  reports/eda_summary.json        dataset profile
  reports/eda_summary.md          dataset profile (readable)
  reports/feature_importance.csv  ranked features
  reports/README.md               folder contract (idempotent)
"""
import json
import os
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset import detect_schema, encode_features, level_for, load_dataset

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "student-mat.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
MODEL_PATH = os.path.join(MODELS_DIR, "student_performance_model.pkl")
FEATURES_PATH = os.path.join(MODELS_DIR, "feature_columns.pkl")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data():
    df, _, _ = load_dataset()
    return df


def eda_summary(df):
    schema = detect_schema(df)
    target = schema["target"]
    scale_max = schema["scale_max"]
    numeric = df.select_dtypes(include="number")
    cutoffs = [c for c, _ in schema["levels"]]
    lo = min(0, float(df[target].min()))
    bins = [lo - 1e-6] + cutoffs
    labels = [lvl for _, lvl in schema["levels"]]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": schema["name"],
        "dataset": "student-mat.csv" if schema["name"] == "uci" else "StudentPerformanceFactors.csv",
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "missing_total": int(df.isnull().sum().sum()),
        "missing_by_column": {c: int(v) for c, v in df.isnull().sum().items() if int(v) > 0},
        "duplicates": int(df.duplicated().sum()),
        "target": {
            "name": target,
            "mean": round(float(df[target].mean()), 3),
            "median": round(float(df[target].median()), 3),
            "std": round(float(df[target].std()), 3),
            "min": float(df[target].min()),
            "max": float(df[target].max()),
            "scale_max": scale_max,
        },
        "level_distribution": {
            level: int(n)
            for level, n in pd.cut(
                df[target], bins=bins, labels=labels,
            ).value_counts().items()
        },
        "numeric_describe": {
            c: {k: round(float(v), 3) for k, v in stats.items()}
            for c, stats in numeric.describe().to_dict().items()
        },
        f"top_abs_corr_with_{target}": {
            k: round(float(v), 3)
            for k, v in numeric.corr(numeric_only=True)[target]
            .abs().sort_values(ascending=False).head(8).items()
        },
    }
    return summary


def train_or_load():
    df = load_data()
    schema = detect_schema(df)
    y = df[schema["target"]]
    X = encode_features(df, schema)
    feature_names = X.columns.tolist()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    if os.path.exists(MODEL_PATH) and os.path.exists(FEATURES_PATH):
        model = joblib.load(MODEL_PATH)
        saved_features = joblib.load(FEATURES_PATH)
        if list(saved_features) == feature_names:
            return model, X_train, X_test, y_train, y_test, feature_names, False
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(feature_names, FEATURES_PATH)
    return model, X_train, X_test, y_train, y_test, feature_names, True


def evaluate(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(mean_squared_error(y_test, y_pred) ** 0.5)
    r2 = float(r2_score(y_test, y_pred))
    residuals = (y_test.values - y_pred)
    within_1 = float((abs(residuals) <= 1.0).mean())
    within_2 = float((abs(residuals) <= 2.0).mean())
    sample = pd.DataFrame({"actual": y_test.values, "predicted": y_pred.round(2)}).head(10)
    return {
        "mae": round(mae, 3), "rmse": round(rmse, 3), "r2": round(r2, 3),
        "within_1pt": round(within_1, 3), "within_2pt": round(within_2, 3),
        "n_test": int(len(y_test)),
        "sample_actual_vs_predicted": sample.to_dict(orient="records"),
    }


def main():
    df = load_data()
    schema = detect_schema(df)
    target = schema["target"]
    eda = eda_summary(df)
    model, X_train, X_test, y_train, y_test, features, retrained = train_or_load()
    metrics = evaluate(model, X_test, y_test)
    metrics["retrained_this_run"] = retrained
    metrics["generated_at"] = datetime.now(timezone.utc).isoformat()
    metrics["model"] = "RandomForestRegressor(n_estimators=200, random_state=42)"
    metrics["schema"] = schema["name"]
    metrics["target"] = target
    metrics["features_excluded"] = schema["drop_from_features"]
    metrics["n_features"] = len(features)
    metrics["train_size"] = int(len(X_train))

    fi = pd.DataFrame(
        {"feature": features, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    fi_path = os.path.join(REPORTS_DIR, "feature_importance.csv")
    fi.to_csv(fi_path, index=False)

    with open(os.path.join(REPORTS_DIR, "eda_summary.json"), "w", encoding="utf-8") as f:
        json.dump(eda, f, indent=2)
    with open(os.path.join(REPORTS_DIR, "model_evaluation.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    top5 = fi.head(5).to_dict(orient="records")
    corr_key = f"top_abs_corr_with_{target}"
    with open(os.path.join(REPORTS_DIR, "eda_summary.md"), "w", encoding="utf-8") as f:
        f.write(f"# EDA Summary — {target}\n\n")
        f.write(f"Generated: {eda['generated_at']}\n\n")
        f.write(f"- Rows: **{eda['rows']}**, Columns: **{eda['columns']}**\n")
        f.write(f"- Missing values: **{eda['missing_total']}**, Duplicates: **{eda['duplicates']}**\n")
        t = eda["target"]
        f.write(f"- Target {target}: mean **{t['mean']}**, median **{t['median']}**, std **{t['std']}**, range **{t['min']}–{t['max']}**\n\n")
        f.write(f"## Level distribution ({target} → level)\n\n")
        f.write("| Level | Count |\n|---|---|\n")
        for lvl, n in eda["level_distribution"].items():
            f.write(f"| {lvl} | {n} |\n")
        f.write(f"\n## Top absolute correlations with {target}\n\n")
        f.write("| Feature | |corr| |\n|---|---|\n")
        for k, v in eda.get(corr_key, {}).items():
            f.write(f"| {k} | {v} |\n")
        f.write("\nSource: canonical dataset via `ml-service/dataset.py`. Charts: `graphs/` via `ml-service/data_analysis.py`.\n")

    with open(os.path.join(REPORTS_DIR, "model_evaluation.md"), "w", encoding="utf-8") as f:
        f.write(f"# Model Evaluation — Student Performance ({target})\n\n")
        f.write(f"Generated: {metrics['generated_at']}\n\n")
        f.write(f"- Model: `{metrics['model']}`\n")
        f.write(f"- Features: **{metrics['n_features']}** (one-hot, `drop_first=True`; excluded {metrics['features_excluded'] or 'nothing'})\n")
        f.write(f"- Split: train **{metrics['train_size']}** / test **{metrics['n_test']}** (`test_size=0.2`, `random_state=42`)\n")
        f.write(f"- Retrained this run: **{retrained}**\n\n")
        f.write("## Metrics (test set)\n\n")
        f.write("| Metric | Value | Meaning |\n|---|---|---|\n")
        f.write(f"| MAE | {metrics['mae']} | avg. grade-point error |\n")
        f.write(f"| RMSE | {metrics['rmse']} | penalizes large errors |\n")
        f.write(f"| R² | {metrics['r2']} | variance explained |\n")
        f.write(f"| Within ±1 pt | {metrics['within_1pt']} | share of predictions |\n")
        f.write(f"| Within ±2 pt | {metrics['within_2pt']} | share of predictions |\n")
        f.write("\n## Top 5 features\n\n")
        f.write("| Feature | Importance |\n|---|---|\n")
        for r in top5:
            f.write(f"| {r['feature']} | {round(float(r['importance']), 4)} |\n")
        f.write("\n## Sample actual vs predicted\n\n")
        f.write("| Actual | Predicted |\n|---|---|\n")
        for r in metrics["sample_actual_vs_predicted"]:
            f.write(f"| {r['actual']} | {r['predicted']} |\n")
        f.write("\nArtifacts: `models/student_performance_model.pkl`, `models/feature_columns.pkl`.\n")

    print("Reports written to ml-service/reports/:")
    for name in ["model_evaluation.json", "model_evaluation.md", "eda_summary.json",
                 "eda_summary.md", "feature_importance.csv"]:
        print(" -", name, f"({os.path.getsize(os.path.join(REPORTS_DIR, name))} bytes)")
    print(f"MAE={metrics['mae']} RMSE={metrics['rmse']} R2={metrics['r2']}")


if __name__ == "__main__":
    main()
