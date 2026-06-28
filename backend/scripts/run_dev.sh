#!/usr/bin/env bash
set -e
export SEPARATION_ENGINE=${SEPARATION_ENGINE:-mock}
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
