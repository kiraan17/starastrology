#!/usr/bin/env bash
# Phase 0 structure verification — no calculation code required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
required=(
  "AGENTS.md"
  "README.md"
  "docs/requirements/BHAVA360-Backend-Requirements-v1.0.md"
  "docs/requirements/PROJECT-CHARTER.md"
  "docs/requirements/REPOSITORY-STRUCTURE.md"
  "docs/requirements/GAP-REPORT.md"
  "docs/status/STATUS-WORKFLOW.md"
  "docs/prompts/P00-lock-project-scope.md"
  "docs/prompts/P02-technique-registry.md"
  "backlog/INITIAL-BACKLOG.md"
  "registry/TECHNIQUE-REGISTRY.md"
  "sources/registers"
  "sources/notes"
  "sources/variants"
  "rules/templates"
  "rules/libraries"
  "specs/calculation"
  "specs/data-model"
  "specs/engines"
  "tests/golden"
  "tests/unit"
  "tests/integration"
  "tests/boundary"
  "expert-reviews"
  "release-notes"
  "console"
  "src"
  "docs/architecture"
  "docs/decisions"
)
missing=0
for path in "${required[@]}"; do
  if [[ ! -e "$ROOT/$path" ]]; then
    echo "MISSING: $path"
    missing=1
  fi
done
if [[ "$missing" -ne 0 ]]; then
  echo "Phase 0 structure check FAILED"
  exit 1
fi
echo "Phase 0 structure check PASSED (${#required[@]} paths)"
