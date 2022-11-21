# Base Stage
FROM python:3.9-slim AS base

RUN apt-get update -qq && \
    apt-get upgrade -qq -y && \
    apt-get install -qq -y gettext-base \
    default-libmysqlclient-dev && \
    apt-get autoremove -y -qq && \
    apt-get autoclean -y -qq


# Build stage
FROM base AS build-stage

WORKDIR /build
# Copy requirements list from the host
COPY requirements.txt /build

ENV PATH="/opt/venv/bin:$PATH"
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip wheel && \
    pip wheel --requirement=requirements.txt --wheel-dir=wheels && \
    pip install --no-deps wheels/*.whl && \
    rm -rf wheels *.egg-info

COPY ./app /app
COPY ./.env /app/

# Runtime stage
FROM base AS runtime-stage

# Copy installed libraries and app from the build stage
COPY --from=build-stage /opt/venv /opt/venv
COPY --from=build-stage /app /app

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

CMD ["python", "main.py"]