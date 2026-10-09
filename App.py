
from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import sys
import os
import json

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS_DIR = os.path.join(BASE_DIR, "Models")
MODEL_PATH = os.path.join(
    BASE_DIR, "models", "student_performance_model.pkl"
)
FEATURE_PATH = os.path.join(
    BASE_DIR, "models", "feature_columns.pkl"
)

# Allow Flask to find recommendation.py
sys.path.append(MODELS_DIR)

from recommendation import generate_recommendations
from database import get_connection, initialize_database

app = Flask(__name__)

# --------------------------------------------------
# LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURE_PATH)

# Initialize SQLite database
initialize_database()

# Required input fields (30 features)
REQUIRED_FIELDS = [
    "school", "sex", "age", "address", "famsize",
    "Pstatus", "Medu", "Fedu", "Mjob", "Fjob",
    "reason", "guardian", "traveltime", "studytime",
    "failures", "schoolsup", "famsup", "paid",
    "activities", "nursery", "higher", "internet",
    "romantic", "famrel", "freetime", "goout",
    "Dalc", "Walc", "health", "absences"
]

# Allowed values for categorical fields
ALLOWED_VALUES = {
    "school": ["GP", "MS"],
    "sex": ["F", "M"],
    "address": ["U", "R"],
    "famsize": ["GT3", "LE3"],
    "Pstatus": ["T", "A"],
    "Mjob": ["teacher", "health", "services", "at_home", "other"],
    "Fjob": ["teacher", "health", "services", "at_home", "other"],
    "reason": ["home", "reputation", "course", "other"],
    "guardian": ["mother", "father", "other"],
    "schoolsup": ["yes", "no"],
    "famsup": ["yes", "no"],
    "paid": ["yes", "no"],
    "activities": ["yes", "no"],
    "nursery": ["yes", "no"],
    "higher": ["yes", "no"],
    "internet": ["yes", "no"],
    "romantic": ["yes", "no"]
}

# Minimum and maximum values for numeric fields
NUMERIC_RANGES = {
    "age": (15, 22),
    "Medu": (0, 4),
    "Fedu": (0, 4),
    "traveltime": (1, 4),
    "studytime": (1, 4),
    "failures": (0, 3),
    "famrel": (1, 5),
    "freetime": (1, 5),
    "goout": (1, 5),
    "Dalc": (1, 5),
    "Walc": (1, 5),
    "health": (1, 5),
    "absences": (0, 75)
}

# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# PREDICTION API
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    try:
        # 1. Read incoming JSON
        student = request.get_json(silent=True)

        # 2. Validate JSON format
        if not isinstance(student, dict) or not student:
            return jsonify({
                "error": "Please send valid student data as JSON."
            }), 400

        # 3. Check all required fields
        missing_fields = [
            field for field in REQUIRED_FIELDS
            if field not in student
            or student[field] is None
            or (
                isinstance(student[field], str)
                and student[field].strip() == ""
            )
        ]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields.",
                "missing_fields": missing_fields
            }), 400

        # Validate categorical fields
        for field, allowed_values in ALLOWED_VALUES.items():
            value = student[field]

            if not isinstance(value, str) or value not in allowed_values:
                return jsonify({
                    "error": f"Invalid value for '{field}'.",
                    "allowed_values": allowed_values
                }), 400

        # Validate numeric fields
        for field, (minimum, maximum) in NUMERIC_RANGES.items():
            value = student[field]

            # Reject booleans and values that are not integers
            if isinstance(value, bool):
                return jsonify({
                    "error": f"'{field}' must be an integer."
                }), 400

            try:
                number = int(value)
            except (ValueError, TypeError):
                return jsonify({
                    "error": f"'{field}' must be an integer."
                }), 400

            if str(number) != str(value).strip() and not isinstance(value, int):
                return jsonify({
                    "error": f"'{field}' must be a whole number."
                }), 400

            if number < minimum or number > maximum:
                return jsonify({
                    "error": f"'{field}' must be between {minimum} and {maximum}."
                }), 400

            student[field] = number
        # 4. Convert input into a DataFrame
        student_df = pd.DataFrame([student])

        # 5. Encode categorical features
        student_df = pd.get_dummies(
            student_df,
            drop_first=True
        )

        # 6. Match training feature columns
        student_df = student_df.reindex(
            columns=feature_columns,
            fill_value=0
        )

        # 7. Predict final grade
        prediction = float(model.predict(student_df)[0])

        # Keep predicted grade within the dataset's 0–20 range
        prediction = max(0.0, min(20.0, prediction))

        # 8. Determine performance level
        if prediction < 10:
            level = "Needs Improvement"
        elif prediction < 13:
            level = "Average"
        elif prediction < 16:
            level = "Good"
        else:
            level = "Excellent"

        # 9. Generate personalized recommendations
        recommendations = generate_recommendations(
            student,
            prediction
        )

        # 10. Save prediction to SQLite
        connection = get_connection()

        try:
            connection.execute(
                """
                INSERT INTO predictions (
                    student_data,
                    predicted_grade,
                    performance_level,
                    recommendations
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    json.dumps(student),
                    round(prediction, 2),
                    level,
                    json.dumps(recommendations)
                )
            )

            connection.commit()

        finally:
            connection.close()

        # 11. Return results to frontend
        return jsonify({
            "predicted_grade": round(prediction, 2),
            "performance_level": level,
            "recommendations": recommendations,
            "message": "Prediction generated and saved successfully."
        }), 200

    
    except (ValueError, TypeError) as error:
        app.logger.warning("Invalid prediction input: %s", error)
        return jsonify({
            "error": "Invalid input. Please check the student data and try again."
        }), 400

    except Exception:
        app.logger.exception("Prediction failed due to an unexpected server error")
        return jsonify({
            "error": "An unexpected server error occurred. Please try again."
        }), 500


# --------------------------------------------------
# PREDICTION HISTORY API
# --------------------------------------------------


@app.route("/history", methods=["GET"])
def prediction_history():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                student_data,
                predicted_grade,
                performance_level,
                recommendations,
                created_at
            FROM predictions
            ORDER BY id DESC
            """
        ).fetchall()

        history = []

        for row in rows:
            record = dict(row)

            # Convert stored JSON strings back into Python objects
            record["student_data"] = json.loads(record["student_data"])
            record["recommendations"] = json.loads(
                record["recommendations"]
            )

            history.append(record)

        return jsonify({
            "total_records": len(history),
            "history": history
        }), 200

    except Exception:
        app.logger.exception("Could not retrieve prediction history")
        return jsonify({
            "error": "Unable to retrieve prediction history."
        }), 500

    finally:
        connection.close()



@app.route("/history/<int:record_id>", methods=["DELETE"])
def delete_prediction(record_id):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM predictions WHERE id = ?",
            (record_id,)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Prediction record not found."
            }), 404

        return jsonify({
            "message": f"Prediction record {record_id} deleted successfully."
        }), 200

    except Exception:
        app.logger.exception("Could not delete prediction")
        return jsonify({
            "error": "Unable to delete prediction record."
        }), 500

    finally:
        connection.close()
# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)