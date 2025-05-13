FROM python:3.12-slim
ARG LOCKNESSIE_ENVIRONMENT=production
ENV LOCKNESSIE_ENVIRONMENT=${LOCKNESSIE_ENVIRONMENT}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/src
COPY ./src /src
COPY ./README.md /README.md
WORKDIR /src
RUN uv sync