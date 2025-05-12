FROM python:3.12-slim
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}
ENV NESSIE_OAUTH2_PORT=8000
ENV NESSIE_OAUTH2_HOST=0.0.0.0
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONPATH=/src/server:/src/server
WORKDIR /src/server
#RUN uv sync
ENTRYPOINT ["/bin/bash", "startup.sh"]