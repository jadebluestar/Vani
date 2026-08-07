# ---- builder: compile/install dependencies into an isolated prefix ----
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- runtime: slim final image, no compiler/build toolchain ----
FROM python:3.12-slim

RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY main.py .
COPY app/ ./app/

# /data is where docker-compose mounts a named volume for the SQLite fallback
# db (VANI_DB_PATH) — pre-create it with appuser ownership so a non-root
# container can still write to it.
RUN mkdir -p /data && chown -R appuser:appuser /app /data
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
