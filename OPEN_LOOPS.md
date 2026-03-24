# OPEN_LOOPS.md

**最終更新**: 2026-03-24 (Session 2 完了後)

---

## フォーマット
```
| ID | カテゴリ | 内容 | 優先度 | 担当 | 追加日 |
```

---

## 現在のオープンループ

| ID | カテゴリ | 内容 | 優先度 | 担当 | 追加日 |
|----|---------|------|-------|------|-------|
| OL-009 | Test | LLM ライブテスト未実施（ANTHROPIC_API_KEY 未設定環境ではフォールバック動作） | High | Human | 2026-03-24 |
| OL-010 | Ops | OpenHands GitHub Action 未設定。issue→PR loop なし（Day 10 タスク） | Medium | Human | 2026-03-24 |
| OL-011 | Infra | GitHub Secrets に `ANTHROPIC_API_KEY` / `FRED_API_KEY` / `OPENROUTER_API_KEY` が未設定。CI が full green にならない | High | Human | 2026-03-24 |
| OL-012 | Infra | Railway project 未設定。`generate_daily_report.sh` の cron 実行ができない（Day 12 タスク） | Medium | Human | 2026-03-24 |
| OL-013 | Infra | Supabase project 未設定。`run_state_schema.sql` の適用と env vars 設定が必要（Day 13 タスク） | Medium | Human | 2026-03-24 |
| OL-014 | Code | main に未 push コミット 2 件・未ステージ変更 4 ファイルが残存 | Medium | Human | 2026-03-24 |

---

## クローズ済み

| ID | 内容 | クローズ日 | 理由 |
|----|------|---------|------|
| OL-001 | `.github/workflows/pr-build.yml` 未作成 | 2026-03-24 | PR #7 merge 済み |
| OL-002 | `docs/architecture/current_system.md` 未作成 | 2026-03-24 | PR #8 merge 済み |
| OL-003 | `docs/agents/ownership.md` / `guardrails.md` 未作成 | 2026-03-24 | PR #9 merge 済み |
| OL-004 | `docs/reports/daily/_template.md` 未作成 | 2026-03-24 | PR #10 merge 済み |
| OL-005 | docs/ フォルダ構造なし | 2026-03-24 | PR #6 merge 済み |
| OL-006 | `scripts/ai/` なし | 2026-03-24 | PR #6, #11, #12, #13 で追加 |
| OL-007 | origin/main より 2 commits 先行 | — | Human判断待ち（変わらず） |
| OL-008 | 未ステージ変更 4 ファイル | — | OL-014 として継続 |
