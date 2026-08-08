#---- Builder ----
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir poetry==1.8.3
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt
#---- Runtime ----
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY src ./src
COPY config ./config
ENTRYPOINT "python", "-m", "adaptive_engine.api.main"
