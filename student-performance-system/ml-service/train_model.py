import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "student-mat.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# --------------------------------------------------
# 1. Load Dataset
# --------------------------------------------------

data = pd.read_csv(DATA_PATH, sep=";")

print("Dataset loaded successfully!")
print("Dataset shape:", data.shape)


# --------------------------------------------------
# 2. Remove G1 and G2
# --------------------------------------------------

data = data.drop(columns=["G1", "G2"])


# --------------------------------------------------
# 3. Separate Features and Target
# --------------------------------------------------

X = data.drop(columns=["G3"])
y = data["G3"]

print("\nTarget: G3 - Final Grade")


# --------------------------------------------------
# 4. Convert Categorical Data into Numbers
# --------------------------------------------------

X = pd.get_dummies(X, drop_first=True)

print("Number of features after encoding:", X.shape[1])


# --------------------------------------------------
# 5. Split Dataset
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
# 6. Create Random Forest Model
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)


# --------------------------------------------------
# 7. Train Model
# --------------------------------------------------

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed!")


# --------------------------------------------------
# 8. Make Predictions
# --------------------------------------------------

y_pred = model.predict(X_test)


# --------------------------------------------------
# 9. Evaluate Model
# --------------------------------------------------

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
# 10. Compare Actual vs Predicted
# --------------------------------------------------

results = pd.DataFrame({
    "Actual Grade": y_test.values,
    "Predicted Grade": y_pred.round(2)
})

print("\nActual vs Predicted Grades:")
print(results.head(10))


# --------------------------------------------------
# 11. Create models folder
# --------------------------------------------------

os.makedirs(MODELS_DIR, exist_ok=True)


# --------------------------------------------------
# 12. Save Model
# --------------------------------------------------

joblib.dump(model, os.path.join(MODELS_DIR, "student_performance_model.pkl"))

print("\nModel saved successfully!")
print("Location: models/student_performance_model.pkl")


# --------------------------------------------------
# 13. Save Feature Names
# --------------------------------------------------

joblib.dump(
    X.columns.tolist(),
    os.path.join(MODELS_DIR, "feature_columns.pkl")
)

print("Feature columns saved successfully!")
print("Location: models/feature_columns.pkl")