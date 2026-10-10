import os
import sys

import joblib
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset import encode_features, level_for, load_dataset
from recommender import generate_recommendations


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------
# 1. Load trained model + schema
# --------------------------------------------------

model = joblib.load(
    os.path.join(BASE_DIR, "models", "student_performance_model.pkl")
)

feature_columns = joblib.load(
    os.path.join(BASE_DIR, "models", "feature_columns.pkl")
)

_, SCHEMA, DATA_PATH = load_dataset()
SCALE_MAX = SCHEMA["scale_max"]

print(f"Model loaded successfully! (schema={SCHEMA['name']}, target={SCHEMA['target']})")


# --------------------------------------------------
# 2. Student information (schema defaults from dataset)
# --------------------------------------------------

if SCHEMA["name"] == "kaggle":
    student = {
        "Hours_Studied": 20, "Attendance": 85, "Parental_Involvement": "Medium",
        "Access_to_Resources": "Medium", "Extracurricular_Activities": "Yes",
        "Sleep_Hours": 7, "Previous_Scores": 70, "Motivation_Level": "Medium",
        "Internet_Access": "Yes", "Tutoring_Sessions": 1, "Family_Income": "Medium",
        "Teacher_Quality": "Medium", "School_Type": "Public",
        "Peer_Influence": "Neutral", "Physical_Activity": "Medium",
        "Learning_Disabilities": "No", "Parental_Education_Level": "College",
        "Distance_from_Home": "Moderate", "Gender": "Female",
    }
else:
    student = {
        "school": "GP", "sex": "F", "age": 17, "address": "U",
        "famsize": "GT3", "Pstatus": "A", "Medu": 3, "Fedu": 3,
        "Mjob": "services", "Fjob": "services", "reason": "course",
        "guardian": "mother", "traveltime": 1, "studytime": 3,
        "failures": 0, "schoolsup": "yes", "famsup": "yes", "paid": "no",
        "activities": "yes", "nursery": "yes", "higher": "yes",
        "internet": "yes", "romantic": "no", "famrel": 4, "freetime": 3,
        "goout": 3, "Dalc": 1, "Walc": 1, "health": 4, "absences": 4,
    }


# --------------------------------------------------
# 3-5. Encode (shared logic) + predict
# --------------------------------------------------

student_df = encode_features(pd.DataFrame([student]), SCHEMA, feature_columns)

prediction = model.predict(student_df)[0]

prediction = round(max(0.0, min(float(SCALE_MAX), float(prediction))), 2)


# --------------------------------------------------
# 6. Level + recommendations
# --------------------------------------------------

level = level_for(prediction, SCHEMA)

recommendations = generate_recommendations(
    student,
    prediction,
    scale_max=SCALE_MAX,
    level=level
)


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("\n===================================")
print(" STUDENT PERFORMANCE REPORT")
print("===================================")

print("\nPredicted Final Grade:")
print(prediction, f"/ {SCALE_MAX}")

print("\nPerformance Level:")
print(level)

print("\nPersonalized Recommendations:")
print("-----------------------------------")

for i, recommendation in enumerate(
    recommendations,
    start=1
):

    print(f"{i}. {recommendation}")
