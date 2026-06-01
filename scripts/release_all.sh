#!/usr/bin/env bash
# GenesisAeon — Release All Packages
#
# Läuft LOKAL auf deiner Maschine (nicht in CI).
# Taggt alle Repos mit v1.0.0 und pusht → GitHub Actions published zu PyPI.
#
# Voraussetzungen:
#   - git konfiguriert mit SSH-Zugang zu github.com/GenesisAeon
#   - Alle Repos geclont unter $BASE_DIR
#   - GitHub Environment "PYPITOKEN" mit Secret PYPI_API_TOKEN gesetzt
#   - publish.yml Workflow in jedem Repo unter .github/workflows/
#
# Usage:
#   chmod +x scripts/release_all.sh
#   ./scripts/release_all.sh                    # Dry-run (zeigt was passiert)
#   ./scripts/release_all.sh --execute          # Wirklich tagen + pushen
#   ./scripts/release_all.sh --execute --package P32   # Nur ein Paket
#   ./scripts/release_all.sh --execute --from P31      # Ab P31 aufwärts

set -euo pipefail

# ─── Konfiguration ────────────────────────────────────────────────────────────

BASE_DIR="${GENESISAEON_DIR:-$HOME/GenesisAeon}"
ORG="GenesisAeon"
TEMPLATE_DIR="$(dirname "$0")/templates"
DRY_RUN=true
ONLY_PACKAGE=""
FROM_PACKAGE=0

# unified-mandala bekommt eine eigene Versionsnummer
MANDALA_VERSION="20.0.0"
DEFAULT_VERSION="1.0.0"

# ─── Package-Liste P17–P40 ────────────────────────────────────────────────────

declare -A PACKAGES=(
    [17]="cygnus-jet-utac"
    [18]="amoc-utac"
    [19]="amazon-utac"
    [20]="neural-avalanche-utac"
    [21]="solar-flare-utac"
    [22]="sandpile-utac"
    [23]="seismic-utac"
    [24]="quantum-genesis"
    [25]="cellular-genesis"
    [26]="spiking-aeon"
    [27]="theta-resonance"
    [28]="epi-sigillin"
    [29]="hikari-ledger"
    [30]="diffusive-routing"
    [31]="vrig-cosmological"
    [32]="beta-clustering-utac"
    [33]="implosive-origin-utac"
    [34]="afet-tensions"
    [35]="phaethon-chimera"
    [36]="sa-sv-duality"
    [37]="eml-utac-bridge"
    [38]="phi-scaling-validator"
    [39]="genesis-scope"
    [40]="HexaAgent"
)

# Core-Repos (kein P-Nummer, eigene Versionen)
CORE_REPOS=(
    "genesis-os:1.0.0"
    "unified-mandala:20.0.0"
    "utac-core:1.0.0"
    "sigillin:1.0.0"
    "diamond-setup:1.0.0"
    "aeon-shell:1.0.0"
    "mirror-machine:1.0.0"
    "entropy-governance:1.0.0"
    "entropy-table:1.0.0"
    "aeon-fraktalurs:1.0.0"
    "aeon-resoecho:1.0.0"
    "universums-sim:1.0.0"
)

# ─── Argument Parsing ─────────────────────────────────────────────────────────

for arg in "$@"; do
    case $arg in
        --execute)   DRY_RUN=false ;;
        --package=*) ONLY_PACKAGE="${arg#*=}" ;;
        --from=*)    FROM_PACKAGE="${arg#*=}" ;;
        --help)
            echo "Usage: $0 [--execute] [--package=P32] [--from=P31]"
            exit 0
            ;;
    esac
done

# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()     { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()   { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()  { echo -e "${RED}[ERROR]${NC} $*"; }
dry()    { echo -e "${YELLOW}[DRY]${NC}   would run: $*"; }

run() {
    if $DRY_RUN; then
        dry "$*"
    else
        eval "$*"
    fi
}

bump_version() {
    local repo_dir="$1"
    local version="$2"
    local changed=false

    # pyproject.toml (hatchling / setuptools / flit style)
    local pyproject="$repo_dir/pyproject.toml"
    if [[ -f "$pyproject" ]]; then
        local current
        current=$(grep -m1 '^version' "$pyproject" | sed 's/.*= *"\(.*\)"/\1/' || echo "")
        if [[ "$current" != "$version" ]]; then
            if $DRY_RUN; then
                dry "sed: $pyproject  version = \"$current\" → \"$version\""
            else
                sed -i "s/^version = \".*\"/version = \"$version\"/" "$pyproject"
                ok "pyproject.toml bumped: $current → $version"
            fi
            changed=true
        fi
    fi

    # __init__.py __version__ = "x.y.z"
    local init
    init=$(find "$repo_dir/src" "$repo_dir" -maxdepth 3 -name "__init__.py" 2>/dev/null | head -5)
    for f in $init; do
        if grep -q '__version__' "$f"; then
            if $DRY_RUN; then
                dry "sed: $f  __version__ → \"$version\""
            else
                sed -i "s/__version__ = \".*\"/__version__ = \"$version\"/" "$f"
                ok "__init__.py bumped: $f"
            fi
            changed=true
        fi
    done

    if $changed && ! $DRY_RUN; then
        git -C "$repo_dir" add -u
        git -C "$repo_dir" diff --cached --quiet || \
            git -C "$repo_dir" commit -m "chore: bump version to $version for 1.0.0 release"
    fi
}

install_workflow() {
    local repo_dir="$1"
    local workflow_src="$TEMPLATE_DIR/publish.yml"
    local workflow_dst="$repo_dir/.github/workflows/publish.yml"

    if [[ ! -f "$workflow_src" ]]; then
        warn "Template not found: $workflow_src"
        return 1
    fi

    run "mkdir -p '$repo_dir/.github/workflows'"
    if [[ ! -f "$workflow_dst" ]]; then
        run "cp '$workflow_src' '$workflow_dst'"
        run "cd '$repo_dir' && git add .github/workflows/publish.yml && git commit -m 'ci: add PyPI publish workflow (PYPITOKEN environment)'"
        ok "Workflow installed in $repo_dir"
    else
        log "Workflow already exists in $repo_dir — skipping"
    fi
}

tag_and_push() {
    local repo_dir="$1"
    local version="$2"
    local tag="v${version}"

    log "Processing $repo_dir → $tag"

    if [[ ! -d "$repo_dir/.git" ]]; then
        error "Not a git repo: $repo_dir"
        return 1
    fi

    # Check if tag already exists
    if git -C "$repo_dir" tag -l "$tag" | grep -q "$tag"; then
        warn "$tag already exists in $repo_dir — skipping"
        return 0
    fi

    bump_version "$repo_dir" "$version"
    install_workflow "$repo_dir"

    run "cd '$repo_dir' && git tag -a '$tag' -m 'Release $tag — GenesisAeon 1.0.0 milestone'"
    run "cd '$repo_dir' && git push origin main --tags"
    ok "Tagged + pushed: $repo_dir @ $tag"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  GenesisAeon Release Script — $(date +%Y-%m-%d)"
if $DRY_RUN; then
    echo "  MODE: DRY RUN (use --execute to actually tag+push)"
else
    echo "  MODE: EXECUTE — tagging and pushing to GitHub"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [[ ! -d "$BASE_DIR" ]]; then
    error "Base directory not found: $BASE_DIR"
    error "Set GENESISAEON_DIR env var to your local GenesisAeon clone directory."
    error "Example: export GENESISAEON_DIR=\$HOME/repos/GenesisAeon"
    exit 1
fi

# Release domain packages P17–P40
SUCCESS=0
SKIPPED=0
FAILED=0

for pid in $(echo "${!PACKAGES[@]}" | tr ' ' '\n' | sort -n); do
    repo="${PACKAGES[$pid]}"

    # Filter by --package or --from
    if [[ -n "$ONLY_PACKAGE" ]]; then
        [[ "P${pid}" == "$ONLY_PACKAGE" || "$pid" == "$ONLY_PACKAGE" ]] || continue
    elif [[ $FROM_PACKAGE -gt 0 ]]; then
        [[ $pid -ge $FROM_PACKAGE ]] || continue
    fi

    repo_dir="$BASE_DIR/$repo"

    if [[ ! -d "$repo_dir" ]]; then
        warn "Repo not cloned locally: $repo_dir"
        warn "  → git clone git@github.com:$ORG/$repo.git $repo_dir"
        ((SKIPPED++)) || true
        continue
    fi

    if tag_and_push "$repo_dir" "$DEFAULT_VERSION"; then
        ((SUCCESS++)) || true
    else
        ((FAILED++)) || true
    fi
done

# Release core repos (if no --package filter)
if [[ -z "$ONLY_PACKAGE" ]]; then
    echo ""
    log "Core repositories..."
    for entry in "${CORE_REPOS[@]}"; do
        repo="${entry%%:*}"
        version="${entry##*:}"
        repo_dir="$BASE_DIR/$repo"

        if [[ ! -d "$repo_dir" ]]; then
            warn "Not cloned locally: $repo_dir"
            ((SKIPPED++)) || true
            continue
        fi

        if tag_and_push "$repo_dir" "$version"; then
            ((SUCCESS++)) || true
        else
            ((FAILED++)) || true
        fi
    done
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Results: ✅ $SUCCESS tagged   ⏭  $SKIPPED skipped   ❌ $FAILED failed"
if $DRY_RUN; then
    echo ""
    echo "  → Run with --execute to apply"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""
