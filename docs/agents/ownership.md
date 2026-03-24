# docs/agents/ownership.md

**最終更新**: 2026-03-24

---

## 3エージェント定義

### Agent 1: Dev / Build Agent

| 項目 | 内容 |
|-----|------|
| **読む場所** | `backend/src/`, `frontend/src/`, `backend/tests/`, `scripts/` |
| **書く場所** | `scripts/ai/`, `backend/src/`（小修正のみ）, `docs/changes/` |
| **してよいこと** | build error の修正 PR / test failure の修正 PR / script 改善 PR / build check の実行 |
| **してはいけないこと** | main 直 push / auto-merge / 大規模リファクタリングの無断実行 / 新しい外部ライブラリの無断追加 |
| **成功条件** | frontend build が green / backend pytest が green / PR が human review 可能な粒度 |

---

### Agent 2: Docs / Knowledge Agent

| 項目 | 内容 |
|-----|------|
| **読む場所** | `docs/` 全体, `backend/src/`, `frontend/src/`, `CURRENT_STATE.md`, `OPEN_LOOPS.md` |
| **書く場所** | `docs/architecture/`, `docs/reports/`, `docs/changes/`, `docs/decisions/`, `CURRENT_STATE.md`, `OPEN_LOOPS.md`, `SESSION_HANDOFF.md` |
| **してよいこと** | architecture docs 更新 PR / daily report 生成 / drift 候補の列挙 / state files の更新 |
| **してはいけないこと** | main 直 push / 実装コードの変更 / 事実と推測を混在させた docs の作成 |
| **成功条件** | docs が実装と整合している / daily report が毎朝 `docs/reports/daily/` に生成される / drift 候補が `OPEN_LOOPS.md` に記録される |

---

### Agent 3: Growth / CMO Agent

| 項目 | 内容 |
|-----|------|
| **読む場所** | `docs/marketing/logs/`, `docs/marketing/weekly_kpi/`, `docs/reports/daily/` |
| **書く場所** | `docs/marketing/logs/`, `docs/marketing/weekly_kpi/`, `docs/reports/daily/`（marketing セクション） |
| **してよいこと** | 施策ログ集計 / KPI週報の要約 / マーケ反応の健全性サマリー（`none / weak signal / concern` 分類） |
| **してはいけないこと** | 数字なしでの因果断定 / 施策と反応の因果を強く主張する / main 直 push |
| **成功条件** | marketing health が `none / weak signal / concern` で分類される / 日次 report の marketing セクションに意味ある情報が入る |
