FROM python:3.12-slim
ARG LOCKNESSIE_ENVIRONMENT=production
ENV LOCKNESSIE_ENVIRONMENT=${LOCKNESSIE_ENVIRONMENT}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/app/src
COPY ./src /app/src
COPY ./README.md /app/README.md
WORKDIR /app/src
ENTRYPOINT ["uv", "run", "locknessie", "server"]