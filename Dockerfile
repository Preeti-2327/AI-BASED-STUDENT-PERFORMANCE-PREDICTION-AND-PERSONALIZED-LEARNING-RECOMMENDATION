# ============================================================
# AI-Based Student Performance Prediction & Personalized
# Learning Recommendation — Production Docker image
# ============================================================
# Build (from repository root):
#   docker build -t student-performance .
#
# Run:
#   docker run -d -p 8000:8000 --name student-performance \
#     -e SQLITE_PATH=/app/student-performance-system/student_performance.db \
#     student-performance
#
# The ML model is trained automatically during the image build
# (models/ is git-ignored; training needs the dataset in data/).

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ---- Install Python dependencies (cached layer) ----
COPY student-performance-system/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ---- Copy application source ----
COPY student-performance-system/ /app/student-performance-system/

# ---- Train the ML model (writes models/student_performance_model.pkl) ----
RUN python /app/student-performance-system/ml-service/train_model.py

# ---- Runtime ----
EXPOSE 8000
ENV PORT=8000 \
    FLASK_DEBUG=0 \
    HOST=0.0.0.0

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health', timeout=5).status == 200 else 1)"

# ---- Production WSGI server (gunicorn) ----
# Binds to $PORT (defaults to 8000) — respects injected PORT from PaaS providers.
CMD ["sh", "-c", "gunicorn --chdir /app/student-performance-system/backend --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 wsgi:app"]
