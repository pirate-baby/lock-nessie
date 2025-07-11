FROM python:3.10
ARG LOCKNESSIE_ENVIRONMENT=release
ENV LOCKNESSIE_ENVIRONMENT=${LOCKNESSIE_ENVIRONMENT}
ARG RELEASE_VERSION=v0.0.0
ENV RELEASE_VERSION=${RELEASE_VERSION}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/app/src
COPY ./src /app/src
COPY ./tests /app/tests
COPY ./README.md /app/README.md
WORKDIR /app/src
RUN uv sync --extra microsoft --dev
CMD ["uv", "run", "pytest", "--it", "../tests"]