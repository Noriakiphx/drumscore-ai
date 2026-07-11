#!/bin/zsh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is not installed."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is not installed."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker Desktop is not running."
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Uncommitted changes were found."
  git status --short
  exit 1
fi

git fetch --all --prune
CURRENT_BRANCH="$(git branch --show-current)"
git pull --ff-only origin "$CURRENT_BRANCH"
docker compose up -d --build

for attempt in {1..30}; do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    echo "Backend is healthy."
    docker compose ps
    echo "Update completed."
    echo "Frontend: http://localhost:3000"
    echo "API docs: http://localhost:8000/docs"
    exit 0
  fi
  sleep 2
done

echo "ERROR: Backend health check failed."
docker compose logs --tail=120 backend
exit 1
