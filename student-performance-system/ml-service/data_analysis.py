import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from dataset import load_dataset

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create graphs folder if it does not exist
os.makedirs(os.path.join(BASE_DIR, "graphs"), exist_ok=True)

# Load dataset from single source of truth (dataset.py)
data, SCHEMA, DATA_PATH = load_dataset()
TARGET = SCHEMA["target"]
LEVELS = SCHEMA.get("levels", [])
CUT_OFFS = [c for c, _ in LEVELS]
LO = min(0, float(data[TARGET].min())) if len(data) else 0

print(f"Dataset: {DATA_PATH} (schema={SCHEMA['name']}, target={TARGET})")
print("Dataset loaded successfully!")

print("\nFirst 5 rows:")
print(data.head())

print("\nDataset Shape:")
print(data.shape)

print("\nColumn Names:")
print(data.columns.tolist())

print("\nMissing Values:")
print(data.isnull().sum())

print("\nStatistical Summary:")
print(data.describe())


# --------------------------------------------------
# 1. Distribution of Final Grades
# --------------------------------------------------

plt.figure(figsize=(8, 5))

bins = [LO - 1e-6] + sorted(set(CUT_OFFS)) + [float(data[TARGET].max()) + 1]

sns.histplot(
    data=data[TARGET],
    bins=bins,
    kde=True,
)

plt.title(f"Distribution of Final Student Grades ({TARGET})")
plt.xlabel(f"Final Grade ({TARGET})")
plt.ylabel("Number of Students")

plt.savefig(
    os.path.join(BASE_DIR, "graphs", "grade_distribution.png"),
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# 2. Study Time vs Final Grade
# --------------------------------------------------

study_col = "studytime" if "studytime" in data.columns else "Hours_Studied"

plt.figure(figsize=(8, 5))

sns.boxplot(
    x=study_col,
    y=TARGET,
    data=data,
)

plt.title(f"Study Time vs Final Grade")
plt.xlabel("Study Time")
plt.ylabel(f"Final Grade ({TARGET})")

plt.savefig(
    os.path.join(BASE_DIR, "graphs", "studytime_vs_grade.png"),
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# 3. Absences / Attendance vs Final Grade
# --------------------------------------------------

att_col = "absences" if "absences" in data.columns else "Attendance"

plt.figure(figsize=(8, 5))

sns.scatterplot(
    x=att_col,
    y=TARGET,
    data=data,
)

plt.title("Absences vs Final Grade")
plt.xlabel("Number of Absences")
plt.ylabel(f"Final Grade ({TARGET})")

plt.savefig(
    os.path.join(BASE_DIR, "graphs", "absences_vs_grade.png"),
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# --------------------------------------------------
# 4. Prior-period grades vs Final Grade (UCI only)
# --------------------------------------------------

for prior_col, label in (("G1", "First Period Grade"), ("G2", "Second Period Grade")):
    if prior_col not in data.columns:
        continue

    plt.figure(figsize=(8, 5))

    sns.scatterplot(
        x=prior_col,
        y=TARGET,
        data=data,
    )

    plt.title(f"{label} vs Final Grade")
    plt.xlabel(prior_col)
    plt.ylabel(f"Final Grade ({TARGET})")

    plt.savefig(
        os.path.join(BASE_DIR, "graphs", f"{prior_col.lower()}_vs_{TARGET.lower()}.png"),
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


# --------------------------------------------------
# 5. Correlation Heatmap
# --------------------------------------------------

numeric_data = data.select_dtypes(include=["int64", "float64"])

correlation = numeric_data.corr()

plt.figure(figsize=(14, 10))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
)

plt.title("Correlation Heatmap")

plt.savefig(
    os.path.join(BASE_DIR, "graphs", "correlation_heatmap.png"),
    dpi=300,
    bbox_inches="tight",
)

plt.close()


print("\nAll graphs saved successfully in the 'graphs' folder!")
