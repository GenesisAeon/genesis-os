#!/usr/bin/env bash
# Publish current package to PyPI via uv (loads token from local .env).
#
# Usage:
#   ./scripts/publish_pypi.sh
#   ./scripts/publish_pypi.sh /path/to/amoc-utac
#   ./scripts/publish_pypi.sh --dry-run
#
# Token lookup: UV_PUBLISH_TOKEN / PYPI_API_TOKEN, then .env in repo,
# genesis-os/.env, or $GENESISAEON_DIR/.env

set -euo pipefail

REPO_PATH="$(pwd)"
DRY_RUN=false
SKIP_BUILD=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --skip-build) SKIP_BUILD=true; shift ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--skip-build] [REPO_PATH]"
      exit 0
      ;;
    *)
      REPO_PATH="$(cd "$1" && pwd)"
      shift
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENESIS_OS="$(cd "$SCRIPT_DIR/.." && pwd)"
MANDALA_ROOT="${GENESISAEON_DIR:-$(dirname "$GENESIS_OS")}"
SECRETS_FILE="${GENESISAEON_SECRETS:-$GENESIS_OS/.env}"

load_dotenv() {
  local file="$1"
  [[ -f "$file" ]] || return 1
  set -a
  # shellcheck disable=SC1090
  source <(grep -v '^\s*#' "$file" | grep -v '^\s*$' | sed 's/\r$//')
  set +a
  echo "Loaded secrets from $file"
  return 0
}

if [[ -z "${UV_PUBLISH_TOKEN:-}" && -z "${PYPI_API_TOKEN:-}" ]]; then
  load_dotenv "$REPO_PATH/.env" \
    || load_dotenv "$SECRETS_FILE" \
    || load_dotenv "$MANDALA_ROOT/.env" \
    || {
      echo "No PyPI token. Create $GENESIS_OS/.env from .env.example" >&2
      exit 1
    }
fi

export UV_PUBLISH_TOKEN="${UV_PUBLISH_TOKEN:-${PYPI_API_TOKEN:-}}"
if [[ -z "$UV_PUBLISH_TOKEN" || "$UV_PUBLISH_TOKEN" == *"..."* ]]; then
  echo "UV_PUBLISH_TOKEN empty or placeholder — edit .env" >&2
  exit 1
fi

[[ -f "$REPO_PATH/pyproject.toml" ]] || {
  echo "No pyproject.toml in $REPO_PATH" >&2
  exit 1
}

cd "$REPO_PATH"

if [[ "$SKIP_BUILD" == false ]]; then
  echo "Building in $REPO_PATH ..."
  if [[ "$DRY_RUN" == true ]]; then
    echo "[dry-run] uv build"
  else
    uv build
  fi
fi

echo "Publishing to PyPI ..."
if [[ "$DRY_RUN" == true ]]; then
  echo "[dry-run] uv publish (token loaded)"
else
  uv publish
fi