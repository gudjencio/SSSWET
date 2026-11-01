FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY core/pyproject.toml /app/core/pyproject.toml
COPY core/ssswet_core /app/core/ssswet_core
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir /app/core

EXPOSE 10000
CMD ["sh", "-c", "ssswet-local --host 0.0.0.0 --port ${PORT:-10000} --database ${SSSWET_DATABASE:-/var/data/ssswet.sqlite3} --orders-database ${SSSWET_ORDERS_DATABASE:-/var/data/orders.sqlite3}"]
