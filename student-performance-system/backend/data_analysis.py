import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create graphs folder if it does not exist
os.makedirs("graphs", exist_ok=True)

# Load dataset
data = pd.read_csv("dataset/student-mat.csv", sep=";")

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

sns.histplot(data["G3"], bins=21, kde=True)

plt.title("Distribution of Final Student Grades")
plt.xlabel("Final Grade (G3)")
plt.ylabel("Number of Students")

plt.savefig(
    "graphs/grade_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# 2. Study Time vs Final Grade
# --------------------------------------------------

plt.figure(figsize=(8, 5))

sns.boxplot(
    x="studytime",
    y="G3",
    data=data
)

plt.title("Study Time vs Final Grade")
plt.xlabel("Study Time")
plt.ylabel("Final Grade (G3)")

plt.savefig(
    "graphs/studytime_vs_grade.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# 3. Absences vs Final Grade
# --------------------------------------------------

plt.figure(figsize=(8, 5))

sns.scatterplot(
    x="absences",
    y="G3",
    data=data
)

plt.title("Absences vs Final Grade")
plt.xlabel("Number of Absences")
plt.ylabel("Final Grade (G3)")

plt.savefig(
    "graphs/absences_vs_grade.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# 4. G1 vs G3
# --------------------------------------------------

plt.figure(figsize=(8, 5))

sns.scatterplot(
    x="G1",
    y="G3",
    data=data
)

plt.title("First Period Grade vs Final Grade")
plt.xlabel("G1 - First Period Grade")
plt.ylabel("Final Grade (G3)")

plt.savefig(
    "graphs/g1_vs_g3.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# 5. G2 vs G3
# --------------------------------------------------

plt.figure(figsize=(8, 5))

sns.scatterplot(
    x="G2",
    y="G3",
    data=data
)

plt.title("Second Period Grade vs Final Grade")
plt.xlabel("G2 - Second Period Grade")
plt.ylabel("Final Grade (G3)")

plt.savefig(
    "graphs/g2_vs_g3.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# 6. Correlation Heatmap
# --------------------------------------------------

numeric_data = data.select_dtypes(
    include=["int64", "float64"]
)

correlation = numeric_data.corr()

plt.figure(figsize=(14, 10))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)

plt.title("Correlation Heatmap")

plt.savefig(
    "graphs/correlation_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print("\nAll graphs saved successfully in the 'graphs' folder!")