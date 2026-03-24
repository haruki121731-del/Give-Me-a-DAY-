#!/usr/bin/env bash
# ops/run.sh — THE single entry point for Give Me a DAY ops.
# Usage:
#   bash ops/run.sh                    # full run
#   bash ops/run.sh --dry-run          # preflight + data collection, no LLM, no push
#   bash ops/run.sh --check-only       # preflight env check only
#   bash ops/run.sh --skip-commit      # run but don't git push
#
# Required env:
#   OPENROUTER_API_KEY  or  ANTHROPIC_API_KEY  (at least one)
# Optional env:
#   SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY     (for run state logging)
#   GITHUB_TOKEN                                (for git push after report)
#
# Exit codes:
#   0  success
#   1  preflight failure (missing required env)
#   2  report generation failed
#   3  unexpected error

set -euo pipefail
trap 'echo ""; echo "❌ ops/run.sh failed at line ${LINENO}. See output above."; exit 3' ERR

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN=false
CHECK_ONLY=false
SKIP_COMMIT=false

for arg in "$@"; do
  case $arg in
    --dry-run)     DRY_RUN=true ;;
    --check-only)  CHECK_ONLY=true ;;
    --skip-commit) SKIP_COMMIT=true ;;
  esac
done

echo "╔══════════════════════════════════════════╗"
echo "║   Give Me a DAY — Ops Run               ║"
echo "╚══════════════════════════════════════════╝"
echo "repo:  ${REPO_ROOT}"
echo "date:  $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "mode:  dry_run=${DRY_RUN}  check_only=${CHECK_ONLY}  skip_commit=${SKIP_COMMIT}"
echo ""

# ══════════════════════════════════════════════
# STEP 1: PREFLIGHT
# ══════════════════════════════════════════════
echo "── PREFLIGHT ──────────────────────────────"
PREFLIGHT_OK=true

check_env() {
  local var="$1" label="$2" required="${3:-false}"
  if [ -n "${!var:-}" ]; then
    echo "  ✅ ${label} (${var})"
  elif [ "${required}" = "true" ]; then
    echo "  ❌ MISSING: ${label} (${var})"
    PREFLIGHT_OK=false
  else
    echo "  ⚠️  optional: ${label} (${var}) — feature disabled"
  fi
}

# LLM: at least one must be set
if [ -n "${OPENROUTER_API_KEY:-}" ] || [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  [ -n "${OPENROUTER_API_KEY:-}" ] && echo "  ✅ LLM via OpenRouter (OPENROUTER_API_KEY)"
  [ -n "${ANTHROPIC_API_KEY:-}" ]  && echo "  ✅ LLM via Anthropic  (ANTHROPIC_API_KEY)"
else
  echo "  ❌ MISSING: at least one of OPENROUTER_API_KEY or ANTHROPIC_API_KEY"
  PREFLIGHT_OK=false
fi

check_env "SUPABASE_URL"              "Supabase URL"              false
check_env "SUPABASE_SERVICE_ROLE_KEY" "Supabase service role key" false
check_env "GITHUB_TOKEN"              "GitHub token (git push)"   false
check_env "FRED_API_KEY"              "FRED macro data"           false
check_env "ANTHROPIC_API_KEY"         "Anthropic (backend LLM)"   false

# Required files
REQUIRED_SCRIPTS=(
  "scripts/ai/run_build_checks.sh"
  "scripts/ai/detect_architecture_drift.sh"
  "scripts/ai/detect_marketing_health.sh"
  "scripts/ai/generate_daily_report.sh"
  "ops/scripts/write_run_state.py"
)
for f in "${REQUIRED_SCRIPTS[@]}"; do
  if [ -f "${REPO_ROOT}/${f}" ]; then
    echo "  ✅ ${f}"
  else
    echo "  ❌ MISSING FILE: ${f}"
    PREFLIGHT_OK=false
  fi
done

if [ "${PREFLIGHT_OK}" = false ]; then
  echo ""
  echo "❌ Preflight failed. Fix the above before running."
  echo "   See .env.ops.example for required variables."
  exit 1
fi

echo ""
echo "  Preflight: ✅ all checks passed"

if [ "${CHECK_ONLY}" = true ]; then
  echo ""
  echo "── CHECK ONLY — done ──────────────────────"
  exit 0
fi

# ══════════════════════════════════════════════
# STEP 2: RUN REPORT GENERATION
# ══════════════════════════════════════════════
echo ""
echo "── REPORT GENERATION ──────────────────────"

REPORT_ARGS=""
[ "${DRY_RUN}" = true ]     && REPORT_ARGS="${REPORT_ARGS} --dry-run"
[ "${SKIP_COMMIT}" = true ] && REPORT_ARGS="${REPORT_ARGS} --skip-commit"

if bash "${REPO_ROOT}/scripts/ai/generate_daily_report.sh" ${REPORT_ARGS}; then
  DATE=$(date -u +"%Y-%m-%d")
  REPORT_PATH="${REPO_ROOT}/docs/reports/daily/${DATE}.md"
  echo ""
  echo "── RESULT ─────────────────────────────────"
  echo "  ✅ Report: ${REPORT_PATH}"
  echo "  size: $(wc -c < "${REPORT_PATH}") bytes"
  echo ""
  echo "── VERIFY ─────────────────────────────────"
  echo "  First 5 lines of report:"
  head -5 "${REPORT_PATH}" | sed 's/^/    /'
  echo ""
  echo "  ✅ ops/run.sh completed successfully"
  exit 0
else
  echo ""
  echo "❌ Report generation failed (exit ${?})."
  exit 2
fi
