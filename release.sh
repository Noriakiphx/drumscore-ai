#!/bin/zsh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

VERSION_INPUT="${1:-}"
if [ -z "$VERSION_INPUT" ]; then
  echo "Usage: ./release.sh 0.3.0"
  exit 1
fi

VERSION="${VERSION_INPUT#v}"
TAG="v$VERSION"

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Working tree is not clean."
  git status --short
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "ERROR: Tag already exists: $TAG"
  exit 1
fi

echo "$VERSION" > VERSION
git add VERSION
git commit -m "Release $TAG"
git tag -a "$TAG" -m "DrumScore AI $TAG"
git push origin "$CURRENT_BRANCH"
git push origin "$TAG"

echo "Release tag pushed: $TAG"
