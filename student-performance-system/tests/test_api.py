"""End-to-end API tests for the AI Student Performance backend.

Run from the project root (``student-performance-system/``):

    pytest tests/ -v

The suite uses the Flask test client, so no server has to be running.
The ML model + SQLite database are used directly (model file ships with the repo).

Note: ``backend/test_api.py`` used to hold a duplicate copy of this script — it
has been removed; this module is now the single source of truth.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app  # noqa: E402

client = app.test_client()


STUDENT = {
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
    "activities": "no",
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
    "absences": 4,
}


# ------------------------------------------------------------
# HEALTH / HOME
# ------------------------------------------------------------
def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_home_page_serves_prediction_form():
    res = client.get("/")
    assert res.status_code == 200
    assert b"predictionForm" in res.data


# ------------------------------------------------------------
# PREDICT
# ------------------------------------------------------------
def test_predict_requires_fields():
    res = client.post("/predict", json={"age": 17})
    assert res.status_code == 400
    body = res.get_json()
    assert body["error"]
    assert body["missing_fields"]
    assert "school" in body["missing_fields"]


def test_predict_rejects_unknown_category():
    bad = dict(STUDENT, school="XX")
    res = client.post("/predict", json=bad)
    assert res.status_code == 400
    assert "school" in res.get_json().get("error", "")


def test_predict_rejects_out_of_range_number():
    bad = dict(STUDENT, age=99)
    res = client.post("/predict", json=bad)
    assert res.status_code == 400
    assert "age" in res.get_json().get("error", "")


def test_predict_success_returns_grade_level_and_recommendations():
    res = client.post("/predict", json=STUDENT)
    assert res.status_code == 200
    body = res.get_json()
    assert "predicted_grade" in body
    assert isinstance(body["predicted_grade"], float)
    assert body["performance_level"] in {
        "Needs Improvement", "Average", "Good", "Excellent",
    }
    assert isinstance(body["recommendations"], list)
    assert body["recommendations"]
    assert "message" in body


# ------------------------------------------------------------
# HISTORY
# ------------------------------------------------------------
def test_history_is_a_list():
    res = client.get("/history")
    assert res.status_code == 200
    body = res.get_json()
    assert "history" in body
    assert isinstance(body["history"], list)


def test_history_delete_roundtrip():
    before = client.get("/history").get_json().get("history") or []
    created = client.post("/predict", json=STUDENT)
    assert created.status_code == 200
    after = client.get("/history").get_json().get("history") or []
    assert len(after) > len(before)

    victim = after[0]
    res = client.delete(f"/history/{victim['id']}")
    assert res.status_code == 200

    follow = client.get("/history").get_json().get("history") or []
    assert victim["id"] not in [r["id"] for r in follow]


# ------------------------------------------------------------
# AUTH
# ------------------------------------------------------------
def test_auth_register_login_logout_flow():
    import time

    email = f"pytest-{int(time.time())}@example.com"
    reg = client.post("/api/auth/register", json={
        "name": "Py Test", "email": email, "password": "test1234", "role": "student",
    })
    assert reg.status_code == 201
    token = reg.get_json()["token"]

    logged_in = client.post("/api/auth/login", json={"email": email, "password": "test1234"})
    assert logged_in.status_code == 200
    assert logged_in.get_json()["token"]

    logout = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 200

    bad = client.post("/api/auth/login", json={"email": email, "password": "wrongpass"})
    assert bad.status_code == 401


def test_auth_register_requires_fields():
    res = client.post("/api/auth/register", json={"name": "", "email": "bad", "password": "x"})
    assert res.status_code == 400
