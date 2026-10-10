
from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import sys
import os
import json

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR, "models", "student_performance_model.pkl"
)
FEATURE_PATH = os.path.join(
    BASE_DIR, "models", "feature_columns.pkl"
)

# Allow imports from backend/ and ml-service/
sys.path.append(os.path.join(BASE_DIR, "ml-service"))
sys.path.append(os.path.join(BASE_DIR, "backend"))

from recommender import generate_recommendations
from dataset import encode_features, level_for, load_dataset
from database import get_connection, initialize_database

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static"),
)

# --------------------------------------------------
# LOAD MACHINE LEARNING MODEL
# --------------------------------------------------

model = None
feature_columns = None

if os.path.exists(MODEL_PATH) and os.path.exists(FEATURE_PATH):
    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_PATH)
else:
    print(f"WARNING: Model not found. Train first: python ml-service/train_model.py")
    print(f"  Expected: {MODEL_PATH}")
    print(f"  Expected: {FEATURE_PATH}")

# Initialize SQLite database
initialize_database()

# Schema comes from the dataset file on disk (dataset.py) — single source.
# UCI → 30 fields, target G3 (0-20). Kaggle → 19 fields, target Exam_Score (0-100).
try:
    _df_probe, SCHEMA, DATA_PATH = load_dataset()
    del _df_probe
except Exception as exc:
    print(f"WARNING: dataset not found ({exc}). Put CSV at data/student-mat.csv")
    from dataset import UCI_SCHEMA as SCHEMA
    DATA_PATH = None

REQUIRED_FIELDS = SCHEMA["required_fields"]

# Allowed values for categorical fields
ALLOWED_VALUES = SCHEMA["allowed_values"]

# Minimum and maximum values for numeric fields
NUMERIC_RANGES = SCHEMA["numeric_ranges"]

TARGET_NAME = SCHEMA["target"]
SCALE_MAX = SCHEMA["scale_max"]

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
        if model is None or feature_columns is None:
            return jsonify({
                "error": "Model not trained yet. Run: python ml-service/train_model.py"
            }), 500

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
        # 4. Convert input into a DataFrame (shared train/serve encoding)
        student_df = encode_features(
            pd.DataFrame([student]), SCHEMA, feature_columns
        )

        # 7. Predict final grade
        prediction = float(model.predict(student_df)[0])

        # Keep predicted grade within the dataset scale
        prediction = max(0.0, min(float(SCALE_MAX), prediction))

        # 8. Determine performance level (schema thresholds)
        level = level_for(prediction, SCHEMA)

        # 9. Generate personalized recommendations
        recommendations = generate_recommendations(
            student,
            prediction,
            scale_max=SCALE_MAX,
            level=level
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
# ERROR PAGES
# --------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)