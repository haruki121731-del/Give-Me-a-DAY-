-- ops/schemas/run_state_schema.sql
-- Purpose: give-me-a-day の AI 実行ログを Supabase に記録するスキーマ
-- Apply: Supabase SQL Editor でそのまま実行する

-- run_logs テーブル
CREATE TABLE IF NOT EXISTS run_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id          TEXT NOT NULL UNIQUE,
  agent_type      TEXT NOT NULL CHECK (agent_type IN ('dev_build', 'docs_knowledge', 'growth_cmo', 'daily_report')),
  started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at     TIMESTAMPTZ,
  status          TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'fail', 'skipped')),
  report_path     TEXT,
  build_result    TEXT CHECK (build_result IN ('success', 'fail', 'skip', 'unknown')),
  drift_status    TEXT CHECK (drift_status IN ('none', 'weak_signal', 'concern', 'unknown')),
  marketing_health TEXT CHECK (marketing_health IN ('none', 'weak_signal', 'concern', 'unknown')),
  cost_estimate   NUMERIC(10, 6),
  error_message   TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_run_logs_started_at ON run_logs (started_at DESC);
CREATE INDEX IF NOT EXISTS idx_run_logs_agent_type ON run_logs (agent_type);
CREATE INDEX IF NOT EXISTS idx_run_logs_status ON run_logs (status);

-- Row Level Security（read は全員、write は service role のみ）
ALTER TABLE run_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public read" ON run_logs
  FOR SELECT USING (true);

CREATE POLICY "service role insert" ON run_logs
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- コメント
COMMENT ON TABLE run_logs IS 'Give Me a DAY AI エージェントの実行ログ。daily report / build check / drift check の結果を記録する。';
COMMENT ON COLUMN run_logs.run_id IS '実行ごとのユニーク ID。YYYY-MM-DD_agent_type 形式を推奨。';
COMMENT ON COLUMN run_logs.agent_type IS 'dev_build / docs_knowledge / growth_cmo / daily_report';
COMMENT ON COLUMN run_logs.cost_estimate IS 'OpenRouter / Anthropic API の推定コスト（USD）';
