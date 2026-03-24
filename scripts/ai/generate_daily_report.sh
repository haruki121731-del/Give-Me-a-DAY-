#!/usr/bin/env bash
# scripts/ai/generate_daily_report.sh
#
# Role    : GENERATION ONLY.
#           Reads collected system data → calls LLM → writes report file.
#           Does NOT collect data, commit, or write to Supabase.
#           Those are the responsibility of ops/run.sh.
#
# Input   : /tmp/gmd_build.md        (written by ops/run.sh)
#           /tmp/gmd_drift.md        (written by ops/run.sh)
#           /tmp/gmd_marketing.md    (written by ops/run.sh)
#           ${REPO_ROOT}/OPEN_LOOPS.md
#
# Output  : docs/reports/daily/YYYY-MM-DD.md
#
# Usage   : bash scripts/ai/generate_daily_report.sh [--dry-run]
#
# Env (required): OPENROUTER_API_KEY  or  ANTHROPIC_API_KEY  (at least one)
#
# Exit codes:
#   0  report file written to REPORT_PATH
#   1  required env vars not set (ops/run.sh preflight should prevent this)
#
# PROVIDER FALLBACK POLICY
# ─────────────────────────────────────────────────────────────────────
# Primary  : OpenRouter   (OPENROUTER_API_KEY)
# Fallback : Anthropic direct API  (ANTHROPIC_API_KEY)
# Final    : data-only template    (raw data, no LLM)
#
# Trigger for fallback (OpenRouter → Anthropic):
#   Any response that does NOT contain a 'choices' key in JSON.
#   This covers: 402 Insufficient Credits, 429 Rate Limit,
#   5xx Server Errors, network timeout (curl fails), JSON parse error.
#
# Trigger for final fallback (→ data template):
#   Anthropic response does NOT contain type='message'.
#   Covers: 401 auth error, 429, 5xx, network failure.
#
# WHAT MUST NEVER BE WRITTEN TO THE REPORT FILE:
#   - Raw JSON objects: {"error": {...}}
#   - Lines starting with "ERROR:"
#   - Empty content
#   Enforced by the fallback chain below. Validated externally by ops/run.sh.
# ─────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATE=$(date -u +"%Y-%m-%d")
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
REPORT_PATH="${REPO_ROOT}/docs/reports/daily/${DATE}.md"
DRY_RUN=false

for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
  esac
done

echo "=== Daily Report Generator — ${TIMESTAMP} ==="
echo "mode: dry_run=${DRY_RUN}"
echo ""

# ─── Env check ──────────────────────────────────────────────────────
HAS_OPENROUTER=false
HAS_ANTHROPIC=false
[ -n "${OPENROUTER_API_KEY:-}" ] && HAS_OPENROUTER=true && echo "  LLM: OpenRouter present"
[ -n "${ANTHROPIC_API_KEY:-}" ]  && HAS_ANTHROPIC=true  && echo "  LLM: Anthropic present"

if [ "${HAS_OPENROUTER}" = false ] && [ "${HAS_ANTHROPIC}" = false ]; then
  echo "ERROR: OPENROUTER_API_KEY or ANTHROPIC_API_KEY must be set."
  exit 1
fi

# ─── Read collected data ─────────────────────────────────────────────
# /tmp/gmd_*.md are written by ops/run.sh before calling this script.
BUILD_RESULT=$(cat /tmp/gmd_build.md       2>/dev/null || echo "UNKNOWN — /tmp/gmd_build.md not found")
DRIFT_RESULT=$(cat /tmp/gmd_drift.md       2>/dev/null || echo "UNKNOWN — /tmp/gmd_drift.md not found")
MARKETING_RESULT=$(cat /tmp/gmd_marketing.md 2>/dev/null || echo "UNKNOWN — /tmp/gmd_marketing.md not found")
OPEN_HIGH=$(grep -A2 "| High" "${REPO_ROOT}/OPEN_LOOPS.md" 2>/dev/null | head -20 \
            || echo "OPEN_LOOPS.md に High 優先度なし")

# Machine-readable status tokens for Supabase (read by ops/run.sh after this script exits)
DRIFT_OVERALL=$(grep "^- overall:" /tmp/gmd_drift.md 2>/dev/null \
                | head -1 | awk -F': ' '{print $2}' || echo "unknown")
MARKETING_OVERALL=$(grep "^- overall:" /tmp/gmd_marketing.md 2>/dev/null \
                    | head -1 | awk -F': ' '{print $2}' || echo "unknown")
BUILD_TOKEN=$(grep -q "✅ success" /tmp/gmd_build.md 2>/dev/null && echo "success" || echo "fail")

# Export for ops/run.sh to read via subshell (ops/run.sh calls this in subprocess,
# so write tokens to a sidecar file instead of relying on exported vars)
mkdir -p /tmp/gmd_meta
echo "${BUILD_TOKEN}"       > /tmp/gmd_meta/build_status
echo "${DRIFT_OVERALL}"     > /tmp/gmd_meta/drift_status
echo "${MARKETING_OVERALL}" > /tmp/gmd_meta/marketing_status

# ─── Dry-run: skip LLM ──────────────────────────────────────────────
if [ "${DRY_RUN}" = true ]; then
  echo "4. [DRY RUN] skipping LLM — writing data-only report"
  mkdir -p "$(dirname "${REPORT_PATH}")"
  cat > "${REPORT_PATH}" << DRYEOF
<!-- DRY RUN — generated at ${TIMESTAMP} — no LLM call made -->
# Daily Report — ${DATE} (dry run)

## Build Check
${BUILD_RESULT}

## Architecture Drift
${DRIFT_RESULT}

## Marketing Health
${MARKETING_RESULT}

## Open Loops (High)
${OPEN_HIGH}
DRYEOF
  echo "   Written: ${REPORT_PATH}"
  echo ""
  echo "=== Done (dry run) ==="
  exit 0
fi

# ─── LLM call ───────────────────────────────────────────────────────
echo "4. Calling LLM..."

SYSTEM_PROMPT="あなたは Give Me a DAY プロジェクトの Docs / Knowledge Agent です。以下のルールに従って daily report を生成してください。- 推測を事実として書かない。事実がなければ UNKNOWN と書く - build / drift / marketing の3項目を必ず埋める - 箇条書きで簡潔に - 日本語で書く - 出力は markdown のみ（前置き不要）"

USER_PROMPT="以下の情報を使って、${DATE} の daily report を生成してください。

# Build Check 結果
${BUILD_RESULT}

# Architecture Drift 結果
${DRIFT_RESULT}

# Marketing Health 結果
${MARKETING_RESULT}

# Open Loops (High 優先度)
${OPEN_HIGH}

7見出し構造で生成: 全体要約 / 今週の変化 / 進捗(表) / Build Failure / Architecture Drift候補 / マーケ反応 / 次に見るべき点(3つ)"

SYSTEM_ESC=$(echo "$SYSTEM_PROMPT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
USER_ESC=$(echo "$USER_PROMPT"     | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

REPORT_CONTENT=""
LLM_ERROR=""

# Primary: OpenRouter
if [ "${HAS_OPENROUTER}" = true ]; then
  RAW=$(curl -s --max-time 30 -X POST \
    -H "Authorization: Bearer ${OPENROUTER_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "HTTP-Referer: https://github.com/haruki121731-del/Give-Me-a-DAY-" \
    https://openrouter.ai/api/v1/chat/completions \
    -d "{\"model\":\"anthropic/claude-haiku-4-5\",\"messages\":[{\"role\":\"system\",\"content\":${SYSTEM_ESC}},{\"role\":\"user\",\"content\":${USER_ESC}}],\"max_tokens\":2000}" \
    2>/dev/null || echo '{"error":{"message":"curl failed"}}')

  HAS_CHOICES=$(echo "$RAW" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print('yes' if 'choices' in d else 'no')" \
    2>/dev/null || echo "no")
  if [ "${HAS_CHOICES}" = "yes" ]; then
    REPORT_CONTENT=$(echo "$RAW" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])")
    echo "   ✅ OpenRouter OK"
  else
    LLM_ERROR=$(echo "$RAW" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','unknown error'))" \
      2>/dev/null || echo "parse error")
    echo "   ⚠️ OpenRouter failed: ${LLM_ERROR}"
  fi
fi

# Fallback: Anthropic direct API
if [ -z "${REPORT_CONTENT}" ] && [ "${HAS_ANTHROPIC}" = true ]; then
  echo "   Trying Anthropic API fallback..."
  RAW=$(curl -s --max-time 30 -X POST \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -H "Content-Type: application/json" \
    https://api.anthropic.com/v1/messages \
    -d "{\"model\":\"claude-haiku-4-5-20251001\",\"max_tokens\":2000,\"system\":${SYSTEM_ESC},\"messages\":[{\"role\":\"user\",\"content\":${USER_ESC}}]}" \
    2>/dev/null || echo '{"type":"error","error":{"message":"curl failed"}}')

  HAS_CONTENT=$(echo "$RAW" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('type')=='message' else 'no')" \
    2>/dev/null || echo "no")
  if [ "${HAS_CONTENT}" = "yes" ]; then
    REPORT_CONTENT=$(echo "$RAW" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d['content'][0]['text'])")
    echo "   ✅ Anthropic API OK"
  else
    LLM_ERROR=$(echo "$RAW" | python3 -c \
      "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','unknown'))" \
      2>/dev/null || echo "parse error")
    echo "   ⚠️ Anthropic API failed: ${LLM_ERROR}"
  fi
fi

# Final fallback: data-only template
# Never writes JSON, never starts with "ERROR:", always has ## sections.
if [ -z "${REPORT_CONTENT}" ]; then
  echo "   ⚠️ All LLM calls failed — writing data-only fallback"
  echo "   LLM error: ${LLM_ERROR}"
  REPORT_CONTENT="# Daily Report — ${DATE}

> ⚠️ LLM unavailable. Error recorded: ${LLM_ERROR}

## Build
${BUILD_RESULT}

## Drift
${DRIFT_RESULT}

## Marketing
${MARKETING_RESULT}

## Open Loops (High)
${OPEN_HIGH}"
fi

# ─── Write report ────────────────────────────────────────────────────
mkdir -p "$(dirname "${REPORT_PATH}")"
{
  echo "<!-- generated by scripts/ai/generate_daily_report.sh at ${TIMESTAMP} -->"
  echo "${REPORT_CONTENT}"
} > "${REPORT_PATH}"

echo "5. Report written: ${REPORT_PATH}"
echo ""
echo "=== Done ==="
