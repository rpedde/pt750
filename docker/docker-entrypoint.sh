#!/usr/bin/env bash

set -eu

case "$1" in
    labels)
        cd /app
        exec uvicorn pt750.web:app --host=0.0.0.0 --port 5000
        ;;
    *)
        exec "$@"
        ;;
esac
