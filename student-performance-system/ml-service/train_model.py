import os
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dataset import encode_features, load_dataset

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# --------------------------------------------------
# 1. Load Dataset (single source: dataset.py)
# --------------------------------------------------

data, SCHEMA, DATA_PATH = load_dataset()
TARGET = SCHEMA["target"]

print(f"Dataset: {DATA_PATH}")
print(f"Schema: {SCHEMA['name']}, target: {TARGET} (0-{SCHEMA['scale_max']})")
print("Dataset shape:", data.shape)


# --------------------------------------------------
# 2-3. Features / Target (schema-driven, no leakage cols)
# --------------------------------------------------

y = data[TARGET]
X = encode_features(data, SCHEMA)

print(f"\nTarget: {TARGET}")
print("Number of features after encoding:", X.shape[1])


# --------------------------------------------------
# 4. Split Dataset
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining data:", X_train.shape)
print("Testing data:", X_test.shape)


# --------------------------------------------------
# 5. Train Random Forest Model
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed!")


# --------------------------------------------------
# 6. Evaluate Model
# --------------------------------------------------

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)

mse = mean_squared_error(y_test, y_pred)

rmse = mse ** 0.5

r2 = r2_score(y_test, y_pred)


print("\n-----------------------------")
print("MODEL PERFORMANCE")
print("-----------------------------")

print("Mean Absolute Error (MAE):", round(mae, 2))
print("Root Mean Squared Error (RMSE):", round(rmse, 2))
print("R2 Score:", round(r2, 2))


# --------------------------------------------------
# 7. Compare Actual vs Predicted
# --------------------------------------------------

results = pd.DataFrame({
    "Actual Grade": y_test.values,
    "Predicted Grade": y_pred.round(2)
})

print("\nActual vs Predicted Grades:")
print(results.head(10))


# --------------------------------------------------
# 8. Save Model + Feature Names + Schema
# --------------------------------------------------

os.makedirs(MODELS_DIR, exist_ok=True)

joblib.dump(model, os.path.join(MODELS_DIR, "student_performance_model.pkl"))

print("\nModel saved successfully!")
print("Location: models/student_performance_model.pkl")

joblib.dump(
    X.columns.tolist(),
    os.path.join(MODELS_DIR, "feature_columns.pkl")
)

print("Feature columns saved successfully!")
print("Location: models/feature_columns.pkl")

joblib.dump(
    {"schema": SCHEMA["name"], "target": TARGET, "scale_max": SCHEMA["scale_max"]},
    os.path.join(MODELS_DIR, "schema_meta.pkl"),
)

print("Schema meta saved successfully!")
print("Location: models/schema_meta.pkl")
