FROM python:3.12-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

WORKDIR /code

COPY backend/pyproject.toml backend/poetry.lock* ./
ARG INSTALL_DEV=false
RUN poetry config virtualenvs.create false && \
    if [ "$INSTALL_DEV" = "true" ] ; \
    then poetry install --no-root ; \
    else poetry install --no-root --only main ; \
    fi

COPY backend ./ 

CMD while ! nc -z postgres 5432; do sleep 0.5; done; \
    alembic upgrade head && \
    uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload