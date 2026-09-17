FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Minimal runtime deps. curl included for the docker-compose healthcheck and
# for diagnostics; jsonschema is used for card validation on POST.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY app /app/app

RUN pip install \
        "fastapi>=0.110,<1" \
        "uvicorn[standard]>=0.27,<1" \
        "elasticsearch>=8.11,<9" \
        "jinja2>=3.1,<4" \
        "pyyaml>=6.0,<7" \
        "jsonschema>=4.21,<5" \
        "python-multipart>=0.0.9,<1"

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=5 \
    CMD curl -fs http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
