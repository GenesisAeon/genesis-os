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
  if [[ -d "$REPO_PATH/dist" ]]; then
    echo "Cleaning $REPO_PATH/dist ..."
    if [[ "$DRY_RUN" == true ]]; then
      echo "[dry-run] rm dist/*"
    else
      find "$REPO_PATH/dist" -mindepth 1 ! -name '.gitignore' -delete 2>/dev/null || rm -f "$REPO_PATH/dist"/*
    fi
  fi
  echo "Building in $REPO_PATH ..."
  if [[ "$DRY_RUN" == true ]]; then
    echo "[dry-run] uv build"
  else
    uv build
    ls -la "$REPO_PATH/dist" 2>/dev/null || true
  fi
fi

mapfile -t FILES < <(find "$REPO_PATH/dist" -maxdepth 1 \( -name '*.whl' -o -name '*.tar.gz' \) -type f 2>/dev/null)
if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No .whl or .tar.gz in $REPO_PATH/dist" >&2
  exit 1
fi

echo "Publishing to PyPI: ${FILES[*]##*/}"
if [[ "$DRY_RUN" == true ]]; then
  echo "[dry-run] uv publish ${FILES[*]}"
else
  uv publish "${FILES[@]}"
fi