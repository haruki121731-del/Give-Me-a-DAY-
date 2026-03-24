# docs/agents/guardrails.md

**最終更新**: 2026-03-24

---

## 絶対禁止事項（すべてのエージェントに適用）

以下はどのエージェントも、いかなる理由があっても実行してはならない。

| 禁止事項 | 理由 |
|---------|------|
| `main` ブランチへの直接 push | Human が merge 判断を持つ。auto-merge 禁止 |
| `auto-merge` の設定・実行 | PR は必ず Human が review する |
| 新規有料サービスの契約・登録 | 課金は Human のみが判断する |
| API キーを伴う新規サービス接続 | secret 管理は Human が行う |
| 本番環境への無承認変更 | 本番への反映は必ず Human が確認する |
| secrets・認証情報の実値の生成・保存・転記 | セキュリティ規約。漏洩リスク排除 |
| 権限昇格・IAM変更 | Human 承認必須 |
| データ削除（DB・ファイル） | 不可逆操作。Human 確認必須 |

---

## 実行前チェック（すべてのエージェントに適用）

エージェントが何かを実行する前に、以下を確認すること。

1. **これは branch / PR として提出できるか？** → できなければ実行しない
2. **この変更は1PR に収まる粒度か？** → 大きすぎる場合は分割する
3. **事実と推測を区別しているか？** → Observed / Inferred / Proposed で書く
4. **不明点は `UNKNOWN` と書いたか？** → 穴埋めしない
5. **Human が review できる形になっているか？** → diff が読める粒度か

---

## Human Confirm が必要な操作

以下は必ず人間に確認を取ってから実行すること。

- `git push origin main` 相当の操作
- Railway / Supabase などのクラウドサービスの設定変更
- `.env` ファイルへの secrets 実値入力
- 課金・有料プランの変更
- 本番 DB へのマイグレーション実行
- GitHub repository secrets / variables の変更

---

## エージェントの成功基準

この2週間のエージェント評価基準は以下の3点のみ。

1. **build failure が検知できているか** → `scripts/ai/run_build_checks.sh` の結果
2. **architecture drift 候補が可視化されているか** → `OPEN_LOOPS.md` の更新
3. **daily report が毎朝読める形で出ているか** → `docs/reports/daily/YYYY-MM-DD.md` の存在

これ以外の活動は「2週間後のゴール」に直結しない限り後回しにする。
