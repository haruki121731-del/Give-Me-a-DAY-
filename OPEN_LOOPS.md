# OPEN_LOOPS.md

**最終更新**: 2026-03-24

---

## フォーマット
```
| ID | カテゴリ | 内容 | 優先度 | 担当 | 追加日 |
```

---

## 現在のオープンループ

| ID | カテゴリ | 内容 | 優先度 | 担当 | 追加日 |
|----|---------|------|-------|------|-------|
| OL-001 | CI/CD | `.github/workflows/pr-build.yml` 未作成。build failure 自動検知ゼロ | High | Claude | 2026-03-24 |
| OL-002 | Docs | `docs/architecture/current_system.md` 未作成。AI が repo 構造を読む場所がない | High | Claude | 2026-03-24 |
| OL-003 | Docs | `docs/agents/ownership.md` / `guardrails.md` 未作成 | Medium | Claude | 2026-03-24 |
| OL-004 | Docs | `docs/reports/daily/_template.md` 未作成 | Medium | Claude | 2026-03-24 |
| OL-005 | Infra | Railway project 未設定。daily report 自動生成ゼロ | Medium | Human | 2026-03-24 |
| OL-006 | Infra | Supabase project 未設定。run state 保存ゼロ | Low | Human | 2026-03-24 |
| OL-007 | Code | `origin/main` より 2 commits 先行（未 push） | Medium | Human | 2026-03-24 |
| OL-008 | Code | 未ステージ変更 4 ファイル（llm/client.py, goal_intake.py, ApprovalPage.tsx, implementation_status.md） | Medium | Human | 2026-03-24 |
| OL-009 | Test | LLM ライブテスト未実施（ANTHROPIC_API_KEY 未設定環境ではフォールバック動作） | High | Human | 2026-03-24 |
| OL-010 | Ops | OpenHands GitHub Action 未設定。issue→PR loop なし | Medium | Human | 2026-03-24 |

---

## クローズ済み

| ID | 内容 | クローズ日 | 理由 |
|----|------|---------|------|
| — | — | — | — |
