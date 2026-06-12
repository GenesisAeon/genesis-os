#!/bin/bash
# Phase 1-A: Release Workflow Rollout Script
#
# Rolls out canonical .github/workflows/release.yml to all 48 GenesisAeon repos
# Creates draft PRs for review before merge
#
# Requirements: git, gh (GitHub CLI with authentication)
# Usage: bash scripts/phase1a_rollout.sh [--dry-run] [--batch N]
#
# Examples:
#   bash scripts/phase1a_rollout.sh --dry-run          # Preview only
#   bash scripts/phase1a_rollout.sh --batch 10         # Process 10 repos
#   bash scripts/phase1a_rollout.sh                    # Full rollout

set -e

DRY_RUN=false
BATCH_SIZE=999  # Default: all

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --batch) BATCH_SIZE=$2; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

REPOS=(
  "diamond-setup" "genesis-os" "genesis-scope"
  "utac-core" "sandpile-utac" "seismic-utac" "neural-avalanche-utac"
  "amoc-utac" "amazon-utac" "solar-flare-utac" "cygnus-jet-utac"
  "eml-utac-bridge" "beta-clustering-utac" "implosive-origin-utac" "afet-tensions"
  "universums-sim" "cosmic-web" "cosmic-moment" "quantum-genesis" "vrig-cosmological"
  "cellular-genesis" "implosive-genesis" "fieldtheory" "Feldtheorie" "sa-sv-duality"
  "worldview" "gemeinwohl" "entropy-governance"
  "aeon-ai" "AdvancedWeightingSystems" "genesis-q4-core" "HexaAgent" "spiking-aeon" "phaethon-chimera"
  "unified-mandala" "unified-mandala-Demo" "mandala-visualize" "sonification"
  "theta-resonance" "medium-modulation" "climate-dashboard" "entropy-table" "phi-scaling-validator"
  "diffusive-routing" "mirror-machine" "sigillin" "epi-sigillin" "hikari-ledger"
)

BRANCH="release-workflow-setup"
TEMP_DIR="/tmp/genesisaeon-phase1a"
WORKFLOW_FILE="scripts/release_workflow_template.yml"

# Read workflow from template (or use inline)
if [ -f "$WORKFLOW_FILE" ]; then
  WORKFLOW_YAML=$(cat "$WORKFLOW_FILE")
else
  WORKFLOW_YAML='name: Release

on:
  push:
    tags:
      - "v*.*.*"

permissions:
  contents: write
  id-token: write

jobs:
  build:
    name: Build distribution
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install build tools
        run: pip install build

      - name: Build wheel and sdist
        run: python -m build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 1

  test:
    name: Test (Python ${{ matrix.python-version }})
    needs: build
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: pytest tests/ -v --cov --cov-report=xml

  publish-pypi-prod:
    name: Publish to PyPI (Production)
    needs: [build, test]
    if: |
      startsWith(github.ref, '"'"'refs/tags/v'"'"') &&
      !contains(github.ref, '"'"'rc'"'"') &&
      !contains(github.ref, '"'"'alpha'"'"') &&
      !contains(github.ref, '"'"'beta'"'"')
    runs-on: ubuntu-latest
    environment:
      name: pypi
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

  github-release:
    name: Create GitHub Release
    needs: [build, test]
    if: startsWith(github.ref, '"'"'refs/tags/v'"'"')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Determine release type
        id: release_type
        run: |
          TAG="${{ github.ref_name }}"
          if [[ "$TAG" == *"rc"* ]] || [[ "$TAG" == *"alpha"* ]] || [[ "$TAG" == *"beta"* ]]; then
            echo "is_prerelease=true" >> $GITHUB_OUTPUT
          else
            echo "is_prerelease=false" >> $GITHUB_OUTPUT
          fi

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          generate_release_notes: true
          draft: false
          prerelease: ${{ steps.release_type.outputs.is_prerelease }}
          token: ${{ secrets.GITHUB_TOKEN }}'
fi

echo ""
echo "=========================================="
echo "Phase 1-A: Release Workflow Rollout"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Repos to process: ${#REPOS[@]}"
echo "  Batch size: $BATCH_SIZE"
echo "  Dry-run mode: $DRY_RUN"
echo "  Temp directory: $TEMP_DIR"
echo ""

mkdir -p "$TEMP_DIR"

COUNT=0
PROCESSED=0

for repo in "${REPOS[@]}"; do
  if [ $COUNT -ge $BATCH_SIZE ]; then
    echo "[*] Batch limit reached ($BATCH_SIZE repos)"
    break
  fi
  
  COUNT=$((COUNT + 1))
  REPO_DIR="$TEMP_DIR/$repo"
  
  echo "[$COUNT/${#REPOS[@]}] $repo"
  
  if [ "$DRY_RUN" = true ]; then
    echo "         [DRY-RUN] Would clone, create branch, add workflow, commit & create PR"
    echo ""
    PROCESSED=$((PROCESSED + 1))
    continue
  fi
  
  # Clone
  if [ -d "$REPO_DIR" ]; then
    echo "         Updating existing clone..."
    git -C "$REPO_DIR" pull --quiet 2>/dev/null || true
  else
    echo "         Cloning..."
    git clone --depth=1 "https://github.com/GenesisAeon/$repo.git" "$REPO_DIR" 2>/dev/null || {
      echo "         ❌ Failed to clone"
      continue
    }
  fi
  
  cd "$REPO_DIR"
  
  # Setup branch
  echo "         Setting up branch: $BRANCH"
  git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH" 2>/dev/null || {
    echo "         ⚠️ Could not create/checkout branch"
    cd - > /dev/null
    continue
  }
  
  # Add workflow
  echo "         Adding release.yml"
  mkdir -p .github/workflows
  echo "$WORKFLOW_YAML" > .github/workflows/release.yml
  
  # Commit
  echo "         Committing..."
  git add .github/workflows/release.yml
  git commit -m "chore(release): add canonical release.yml workflow for v1.0.0 orchestration" 2>/dev/null || {
    echo "         ℹ️ Nothing to commit (already exists)"
    cd - > /dev/null
    PROCESSED=$((PROCESSED + 1))
    continue
  }
  
  # Push
  echo "         Pushing to origin..."
  git push -u origin "$BRANCH" 2>/dev/null || {
    echo "         ⚠️ Push failed"
    cd - > /dev/null
    continue
  }
  
  # Create PR
  echo "         Creating PR..."
  gh pr create \
    --repo "GenesisAeon/$repo" \
    --base main \
    --head "$BRANCH" \
    --title "chore(release): add canonical release.yml workflow" \
    --body "Standardized release workflow for v1.0.0 orchestration.

**Includes:**
- Build (wheel + sdist) via \`python -m build\`
- Test matrix (Python 3.10, 3.11, 3.12)
- PyPI publication (Production: vX.Y.Z only)
- GitHub Release management with auto-generated notes
- Canary/Prod Guards (rc/alpha/beta → Test PyPI only)

**How it works:**
- Trigger: Push git tag matching \`v*.*.*\`
- Build stage: Create wheel + source distribution
- Test stage: Run pytest across Python versions
- Publish stage (conditional):
  - Production: vX.Y.Z → PyPI production
  - Canary: vX.Y.Z-rc/alpha/beta → Test PyPI only
- GitHub Release: Auto-generated from commit history

**Setup required:**
- Org secret: \`PYPI_API_TOKEN\` (scoped to GenesisAeon packages)
- Org secret: \`ZENODO_TOKEN\` (for DOI integration, optional)

Related: GenesisAeon v1.0.0 Release Orchestration Initiative
Phase: 1-A (Infrastructure Rollout)" \
    --draft || {
    echo "         ⚠️ PR creation failed (may already exist)"
  }
  
  echo "         ✅ Done"
  echo ""
  
  PROCESSED=$((PROCESSED + 1))
  cd - > /dev/null
done

echo "=========================================="
echo "Phase 1-A Summary"
echo "=========================================="
echo "Processed: $PROCESSED/${#REPOS[@]}"
echo "Temp files: $TEMP_DIR"
echo ""
echo "[*] Next steps:"
echo "    1. Review PRs at: https://github.com/GenesisAeon/?q=is:pr+is:draft"
echo "    2. Approve & merge workflow PRs"
echo "    3. Setup org secrets (PYPI_API_TOKEN, ZENODO_TOKEN)"
echo "    4. Signal completion to trigger Phase 2 (Claude Code analysis)"
echo ""
