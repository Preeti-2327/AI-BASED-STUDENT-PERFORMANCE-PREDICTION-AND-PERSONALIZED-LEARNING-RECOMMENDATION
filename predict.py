import pandas as pd
import joblib

from recommendation import generate_recommendations


# --------------------------------------------------
# 1. Load trained model
# --------------------------------------------------

model = joblib.load(
    "models/student_performance_model.pkl"
)

feature_columns = joblib.load(
    "models/feature_columns.pkl"
)

print("Model loaded successfully!")


# --------------------------------------------------
# 2. Student information
# --------------------------------------------------

student = {
    "school": "GP",
    "sex": "F",
    "age": 17,
    "address": "U",
    "famsize": "GT3",
    "Pstatus": "A",
    "Medu": 3,
    "Fedu": 3,
    "Mjob": "services",
    "Fjob": "services",
    "reason": "course",
    "guardian": "mother",
    "traveltime": 1,
    "studytime": 3,
    "failures": 0,
    "schoolsup": "yes",
    "famsup": "yes",
    "paid": "no",
    "activities": "yes",
    "nursery": "yes",
    "higher": "yes",
    "internet": "yes",
    "romantic": "no",
    "famrel": 4,
    "freetime": 3,
    "goout": 3,
    "Dalc": 1,
    "Walc": 1,
    "health": 4,
    "absences": 4
}


# --------------------------------------------------
# 3. Convert to DataFrame
# --------------------------------------------------

student_df = pd.DataFrame([student])


# --------------------------------------------------
# 4. One-Hot Encoding
# --------------------------------------------------

student_df = pd.get_dummies(
    student_df,
    drop_first=True
)


# --------------------------------------------------
# 5. Match training columns
# --------------------------------------------------

student_df = student_df.reindex(
    columns=feature_columns,
    fill_value=0
)


# --------------------------------------------------
# 6. Predict grade
# --------------------------------------------------

prediction = model.predict(student_df)[0]

prediction = round(prediction, 2)


# --------------------------------------------------
# 7. Determine performance level
# --------------------------------------------------

if prediction < 10:

    level = "Needs Improvement"

elif prediction < 13:

    level = "Average"

elif prediction < 16:

    level = "Good"

else:

    level = "Excellent"


# --------------------------------------------------
# 8. Generate recommendations
# --------------------------------------------------

recommendations = generate_recommendations(
    student,
    prediction
)


# --------------------------------------------------
# 9. Display results
# --------------------------------------------------

print("\n===================================")
print(" STUDENT PERFORMANCE REPORT")
print("===================================")

print("\nPredicted Final Grade:")
print(prediction, "/ 20")

print("\nPerformance Level:")
print(level)

print("\nPersonalized Recommendations:")
print("-----------------------------------")

for i, recommendation in enumerate(
    recommendations,
    start=1
):

    print(f"{i}. {recommendation}")