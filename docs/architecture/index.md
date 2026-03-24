# docs/architecture/

## 目的
repo の現在のシステム構成を、AI が読めるドキュメントとして維持する。
build / drift 検知の入力として使う。

## ファイル一覧
| ファイル | 内容 | 状態 |
|---------|------|------|
| `current_system.md` | 現在の主要構成・コンポーネント役割 | 未作成 |
| `module_map.md` | モジュール間の依存関係マップ | 未作成 |
| `agent_execution_flow.md` | エージェント実行フロー | 未作成 |

## 更新ルール
- 実装変更が docs に反映されていない場合は architecture drift 候補として `OPEN_LOOPS.md` に記録する
- 大きな構造変化があった場合は PR に `architecture-drift` ラベルを付ける
