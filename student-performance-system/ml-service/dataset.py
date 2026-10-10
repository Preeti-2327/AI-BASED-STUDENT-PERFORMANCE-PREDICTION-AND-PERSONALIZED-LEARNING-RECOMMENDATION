"""Single source of truth for dataset + schema.

Canonical data file: ``data/student-mat.csv`` (project root level).
Fallback mirror: ``ml-service/data/student-mat.csv`` (kept for compat).

Supports TWO schemas and auto-detects which one is on disk:
  - "uci"    : UCI Student-Mat,  target G3 (0-20),  ";" separator
  - "kaggle" : StudentPerformanceFactors.csv, target Exam_Score (0-100), "," separator

Everything (train_model, backend/app, predict, generate_reports,
data_analysis) must import from here — no hardcoded field lists elsewhere.
"""
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_CANDIDATES = [
    os.path.join(BASE_DIR, "data", "student-mat.csv"),
    os.path.join(BASE_DIR, "ml-service", "data", "student-mat.csv"),
    os.path.join(BASE_DIR, "data", "StudentPerformanceFactors.csv"),
    os.path.join(BASE_DIR, "ml-service", "data", "StudentPerformanceFactors.csv"),
]

KAGGLE_SCHEMA = {
    "name": "kaggle",
    "target": "Exam_Score",
    "scale_max": 100,
    "drop_from_features": [],
    "required_fields": [
        "Hours_Studied", "Attendance", "Parental_Involvement",
        "Access_to_Resources", "Extracurricular_Activities", "Sleep_Hours",
        "Previous_Scores", "Motivation_Level", "Internet_Access",
        "Tutoring_Sessions", "Family_Income", "Teacher_Quality",
        "School_Type", "Peer_Influence", "Physical_Activity",
        "Learning_Disabilities", "Parental_Education_Level",
        "Distance_from_Home", "Gender",
    ],
    "numeric_ranges": {
        "Hours_Studied": (0, 50),
        "Attendance": (0, 100),
        "Sleep_Hours": (0, 12),
        "Previous_Scores": (0, 100),
        "Tutoring_Sessions": (0, 20),
    },
    "allowed_values": {
        "Parental_Involvement": ["Low", "Medium", "High"],
        "Access_to_Resources": ["Low", "Medium", "High"],
        "Extracurricular_Activities": ["Yes", "No"],
        "Motivation_Level": ["Low", "Medium", "High"],
        "Internet_Access": ["Yes", "No"],
        "Family_Income": ["Low", "Medium", "High"],
        "Teacher_Quality": ["Low", "Medium", "High"],
        "School_Type": ["Public", "Private"],
        "Peer_Influence": ["Negative", "Neutral", "Positive"],
        "Physical_Activity": ["Low", "Medium", "High"],
        "Learning_Disabilities": ["Yes", "No"],
        "Parental_Education_Level": ["High School", "College", "Postgraduate"],
        "Distance_from_Home": ["Near", "Moderate", "Far"],
        "Gender": ["Male", "Female"],
    },
    # Exam_Score 0-100 thresholds
    "levels": [(60, "Needs Improvement"), (75, "Average"), (90, "Good"), (101, "Excellent")],
}

UCI_SCHEMA = {
    "name": "uci",
    "target": "G3",
    "scale_max": 20,
    "drop_from_features": ["G1", "G2"],
    "required_fields": [
        "school", "sex", "age", "address", "famsize",
        "Pstatus", "Medu", "Fedu", "Mjob", "Fjob",
        "reason", "guardian", "traveltime", "studytime",
        "failures", "schoolsup", "famsup", "paid",
        "activities", "nursery", "higher", "internet",
        "romantic", "famrel", "freetime", "goout",
        "Dalc", "Walc", "health", "absences",
    ],
    "numeric_ranges": {
        "age": (15, 22), "Medu": (0, 4), "Fedu": (0, 4),
        "traveltime": (1, 4), "studytime": (1, 4), "failures": (0, 3),
        "famrel": (1, 5), "freetime": (1, 5), "goout": (1, 5),
        "Dalc": (1, 5), "Walc": (1, 5), "health": (1, 5),
        "absences": (0, 75),
    },
    "allowed_values": {
        "school": ["GP", "MS"], "sex": ["F", "M"],
        "address": ["U", "R"], "famsize": ["GT3", "LE3"],
        "Pstatus": ["T", "A"],
        "Mjob": ["teacher", "health", "services", "at_home", "other"],
        "Fjob": ["teacher", "health", "services", "at_home", "other"],
        "reason": ["home", "reputation", "course", "other"],
        "guardian": ["mother", "father", "other"],
        "schoolsup": ["yes", "no"], "famsup": ["yes", "no"],
        "paid": ["yes", "no"], "activities": ["yes", "no"],
        "nursery": ["yes", "no"], "higher": ["yes", "no"],
        "internet": ["yes", "no"], "romantic": ["yes", "no"],
    },
    # G3 0-20 thresholds (existing behavior, unchanged)
    "levels": [(10, "Needs Improvement"), (13, "Average"), (16, "Good"), (21, "Excellent")],
}


def find_data_file():
    for path in DATA_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "No dataset found. Put the CSV at data/student-mat.csv "
        f"(checked: {DATA_CANDIDATES})"
    )


def detect_schema(df):
    """Pick schema from actual columns on disk — never assume."""
    cols = set(df.columns)
    if "Exam_Score" in cols:
        return KAGGLE_SCHEMA
    if "G3" in cols:
        return UCI_SCHEMA
    raise ValueError(
        f"Unknown dataset schema. Columns: {sorted(cols)}. "
        "Expected 'G3' (UCI) or 'Exam_Score' (Kaggle)."
    )


def load_dataset():
    """Returns (df, schema, data_path). Auto sep: ';' for UCI, ',' for Kaggle."""
    path = find_data_file()
    df = pd.read_csv(path, sep=";")
    if len(df.columns) < 2:  # probably comma-separated (Kaggle)
        df = pd.read_csv(path, sep=",")
    schema = detect_schema(df)
    return df, schema, path


def level_for(score, schema):
    for cutoff, level in schema["levels"]:
        if score < cutoff:
            return level
    return schema["levels"][-1][1]


def encode_features(df, schema, feature_columns=None):
    """One-hot encode + align to training columns (shared train/serve logic)."""
    drop = [c for c in schema["drop_from_features"] if c in df.columns]
    X = df.drop(columns=drop + [schema["target"]], errors="ignore")
    X = pd.get_dummies(X, drop_first=True)
    if feature_columns is not None:
        X = X.reindex(columns=feature_columns, fill_value=0)
    return X
