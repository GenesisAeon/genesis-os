#!/usr/bin/env bash
#
# Roll out GenesisAeon ecosystem templates (release workflow + governance
# docs) from genesis-os/scripts/templates/ to the other repos listed in
# release_map.yml.
#
# For each target repo this script:
#   1. Clones (or updates) the repo into $WORKDIR
#   2. Creates a branch (default: chore/ecosystem-templates)
#   3. Copies templates into the right locations
#   4. Commits if anything changed
#   5. Pushes the branch (and optionally opens a PR via the GitHub API,
#      if GH_TOKEN is set)
#
# Requires: git, curl (for PR creation), a GitHub token with push access
# to the target repos exported as GH_TOKEN.
#
# Usage:
#   ./scripts/rollout_templates.sh                 # all repos in release_map.yml
#   ./scripts/rollout_templates.sh utac-core sigillin
#   DRY_RUN=1 ./scripts/rollout_templates.sh        # show what would happen
#
set -euo pipefail

ORG="GenesisAeon"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="$ROOT_DIR/scripts/templates"
WORKDIR="${WORKDIR:-/tmp/genesisaeon-rollout}"
BRANCH="${BRANCH:-chore/ecosystem-templates}"
DRY_RUN="${DRY_RUN:-0}"

mkdir -p "$WORKDIR"

if [ "$#" -gt 0 ]; then
  REPOS=("$@")
else
  # Extract top-level keys (repo names) from release_map.yml, skipping
  # genesis-os itself (this is the source of the templates).
  mapfile -t REPOS < <(python3 - "$ROOT_DIR/release_map.yml" <<'EOF'
import sys, yaml
data = yaml.safe_load(open(sys.argv[1]))
for name in data:
    if name != "genesis-os":
        print(name)
EOF
)
fi

echo "[*] Rolling out templates to ${#REPOS[@]} repositories (branch: $BRANCH)"
[ "$DRY_RUN" = "1" ] && echo "[*] DRY_RUN=1 — no pushes will be made"

for repo in "${REPOS[@]}"; do
  echo ""
  echo "=== $repo ==="
  dest="$WORKDIR/$repo"

  if [ -d "$dest/.git" ]; then
    git -C "$dest" fetch origin --quiet
    git -C "$dest" checkout main --quiet 2>/dev/null || git -C "$dest" checkout master --quiet
    git -C "$dest" pull --quiet
  else
    git clone --depth=1 "https://github.com/$ORG/$repo.git" "$dest" --quiet
  fi

  git -C "$dest" checkout -B "$BRANCH" --quiet

  # 1. Release workflow
  mkdir -p "$dest/.github/workflows" "$dest/.github/ISSUE_TEMPLATE"
  cp "$TEMPLATES_DIR/publish.yml" "$dest/.github/workflows/release.yml"

  # 2. Governance docs (only add if missing, never overwrite existing docs)
  for f in RELEASE_GUIDE.md CONTRIBUTING.md; do
    if [ ! -f "$dest/$f" ]; then
      cp "$TEMPLATES_DIR/$f" "$dest/$f"
    fi
  done

  # 3. CHANGELOG stub (only if missing)
  if [ ! -f "$dest/CHANGELOG.md" ]; then
    cp "$TEMPLATES_DIR/CHANGELOG_STUB.md" "$dest/CHANGELOG.md"
  fi

  # 4. Issue / PR templates
  cp "$TEMPLATES_DIR/ISSUE_TEMPLATE/bug_report.md" "$dest/.github/ISSUE_TEMPLATE/bug_report.md"
  cp "$TEMPLATES_DIR/ISSUE_TEMPLATE/feature_request.md" "$dest/.github/ISSUE_TEMPLATE/feature_request.md"
  cp "$TEMPLATES_DIR/PULL_REQUEST_TEMPLATE.md" "$dest/.github/PULL_REQUEST_TEMPLATE.md"

  # 5. zenodo.json (only if missing — fill in placeholders manually afterwards)
  if [ ! -f "$dest/zenodo.json" ]; then
    cp "$TEMPLATES_DIR/zenodo.json" "$dest/zenodo.json"
    sed -i "s/PACKAGE_REPO/$repo/g" "$dest/zenodo.json"
  fi

  if [ -z "$(git -C "$dest" status --porcelain)" ]; then
    echo "  (no changes)"
    continue
  fi

  git -C "$dest" add -A
  git -C "$dest" commit -q -m "chore: adopt GenesisAeon ecosystem release workflow and governance templates"

  if [ "$DRY_RUN" = "1" ]; then
    echo "  [DRY RUN] would push branch $BRANCH and open PR"
    continue
  fi

  git -C "$dest" push -u origin "$BRANCH" --quiet

  if [ -n "${GH_TOKEN:-}" ]; then
    curl -s -X POST \
      -H "Authorization: token $GH_TOKEN" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/$ORG/$repo/pulls" \
      -d "$(python3 -c "import json,sys; print(json.dumps({'title':'chore: adopt GenesisAeon ecosystem release workflow and governance templates','head':sys.argv[1],'base':'main','body':'Rolled out from genesis-os/scripts/templates/ as part of the v1.0.0 release orchestration.'}))" "$BRANCH")" \
      > /dev/null
    echo "  PR opened for $repo"
  else
    echo "  Pushed $BRANCH (set GH_TOKEN to auto-open a PR)"
  fi
done

echo ""
echo "[*] Done."
