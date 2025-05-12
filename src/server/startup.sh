#!/bin/bash
set -e

RELOAD=""

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode"
    RELOAD="--reload"
else
    echo "Running in production mode"
fi
uv run uvicorn server.main:app $RELOAD --host $NESSIE_OAUTH2_HOST --port $NESSIE_OAUTH2_PORT