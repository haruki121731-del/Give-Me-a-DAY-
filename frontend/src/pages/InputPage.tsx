import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, CompanionGoalResponse, CompanionQuestion } from '../api/client'

const RISK_OPTIONS = [
  { value: 'very_low', label: 'とても低い' },
  { value: 'low', label: '低い' },
  { value: 'medium', label: '中程度' },
  { value: 'high', label: '高い' },
]

const HORIZON_OPTIONS = [
  { value: 'fast', label: '最速' },
  { value: 'one_day', label: '1日' },
  { value: 'one_week', label: '1週間' },
  { value: 'one_month', label: '1ヶ月' },
  { value: 'quality_over_speed', label: '品質優先' },
]

const EXCLUSION_OPTIONS = [
  '特定セクターの除外',
  'レバレッジの使用禁止',
  '空売りの禁止',
  'デリバティブの使用禁止',
]

type Stage = 'input' | 'clarification' | 'review'

function InputPage() {
  const navigate = useNavigate()

  // Form fields
  const [goal, setGoal] = useState('')
  const [successCriteria, setSuccessCriteria] = useState('')
  const [risk, setRisk] = useState('medium')
  const [timeHorizon, setTimeHorizon] = useState('one_week')
  const [exclusions, setExclusions] = useState<string[]>([])

  // Preflight state
  const [stage, setStage] = useState<Stage>('input')
  const [preflightResult, setPreflightResult] = useState<CompanionGoalResponse | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [refinedRequest, setRefinedRequest] = useState<null | {
    goal: string
    success_criteria?: string
    risk?: string
    time_horizon?: string
    exclusions: string[]
  }>(null)
  const [inferenceSummary, setInferenceSummary] = useState<Array<{
    field: string; inferred_value: string; from_text: string
  }>>([])
  const [openUncertainties, setOpenUncertainties] = useState<string[]>([])

  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleExclusionToggle = (item: string) => {
    setExclusions(prev =>
      prev.includes(item) ? prev.filter(e => e !== item) : [...prev, item]
    )
  }

  // Stage 1: call preflight, show contradictions + questions if needed
  const handlePreflight = async () => {
    if (goal.length < 10) {
      setError('投資目標を10文字以上で入力してください')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      const result = await api.preflightGoal({
        goal,
        success_criteria: successCriteria || undefined,
        risk,
        time_horizon: timeHorizon,
        exclusions,
      })
      if (!result.needs_clarification && result.contradictions.length === 0) {
        // No issues — go straight to pipeline
        await submitRun({ goal, success_criteria: successCriteria || undefined, risk, time_horizon: timeHorizon, exclusions })
      } else {
        setPreflightResult(result)
        setAnswers({})
        setStage('clarification')
      }
    } catch {
      // Preflight failure is non-fatal — fall through to direct submission
      await submitRun({ goal, success_criteria: successCriteria || undefined, risk, time_horizon: timeHorizon, exclusions })
    } finally {
      setSubmitting(false)
    }
  }

  // Stage 2: submit answers, get refined request
  const handleAnswerSubmit = async () => {
    setError(null)
    setSubmitting(true)
    try {
      const res = await api.preflightSubmit({
        original_request: { goal, success_criteria: successCriteria || undefined, risk, time_horizon: timeHorizon, exclusions },
        answers,
      })
      setRefinedRequest(res.refined_request)
      setInferenceSummary(res.inference_summary)
      setOpenUncertainties(res.open_uncertainties)
      setStage('review')
    } catch (e) {
      setError(e instanceof Error ? e.message : '回答の送信に失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  // Stage 3: final submit with refined request
  const handleReviewSubmit = async () => {
    if (!refinedRequest) return
    setError(null)
    setSubmitting(true)
    await submitRun(refinedRequest)
    setSubmitting(false)
  }

  const submitRun = async (req: {
    goal: string
    success_criteria?: string
    risk?: string
    time_horizon?: string
    exclusions?: string[]
  }) => {
    try {
      const res = await api.createRun(req)
      navigate(`/runs/${res.run_id}/loading`)
    } catch (e) {
      setError(e instanceof Error ? e.message : '送信に失敗しました')
    }
  }

  // ── Stage: input ────────────────────────────────────────────────────────────
  if (stage === 'input') {
    return (
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-2">投資戦略を検証する</h2>
        <p className="text-gray-600 mb-6">
          投資の目標を入力してください。システムが候補を生成・検証・比較し、生き残った方向を提示します。
        </p>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              投資目標 <span className="text-red-500">*</span>
            </label>
            <textarea
              className="w-full border border-gray-300 rounded-lg p-3 min-h-[120px] focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="例: 日本株で12ヶ月モメンタム戦略を検証したい"
              value={goal}
              onChange={e => setGoal(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">成功基準（任意）</label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="例: 年率10%以上のリターン"
              value={successCriteria}
              onChange={e => setSuccessCriteria(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">リスク許容度</label>
            <select
              className="w-full border border-gray-300 rounded-lg p-3"
              value={risk}
              onChange={e => setRisk(e.target.value)}
            >
              {RISK_OPTIONS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">検証期間</label>
            <select
              className="w-full border border-gray-300 rounded-lg p-3"
              value={timeHorizon}
              onChange={e => setTimeHorizon(e.target.value)}
            >
              {HORIZON_OPTIONS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">除外条件</label>
            <div className="space-y-2">
              {EXCLUSION_OPTIONS.map(item => (
                <label key={item} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={exclusions.includes(item)}
                    onChange={() => handleExclusionToggle(item)}
                    className="rounded"
                  />
                  <span className="text-sm">{item}</span>
                </label>
              ))}
            </div>
          </div>

          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">{error}</div>
          )}

          <button
            onClick={handlePreflight}
            disabled={submitting || goal.length < 10}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? '確認中...' : '検証する →'}
          </button>
        </div>
      </div>
    )
  }

  // ── Stage: clarification ─────────────────────────────────────────────────────
  if (stage === 'clarification' && preflightResult) {
    const questions = preflightResult.questions.filter(q => q.type !== 'redirect_notice')
    const notices = preflightResult.questions.filter(q => q.type === 'redirect_notice')

    return (
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-2">確認事項</h2>
        <p className="text-gray-600 mb-6">
          検証を開始する前に、いくつか確認させてください。
        </p>

        <div className="space-y-6">
          {/* Contradiction notices — shown first */}
          {preflightResult.contradictions.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
              <p className="text-sm font-semibold text-amber-800">注意事項</p>
              {preflightResult.contradictions.map((notice, i) => (
                <p key={i} className="text-sm text-amber-700 whitespace-pre-wrap">{notice}</p>
              ))}
            </div>
          )}

          {/* Out-of-scope redirect notices */}
          {notices.map(q => (
            <div key={q.id} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-blue-800 mb-1">スコープ外のシグナル</p>
              <p className="text-sm text-blue-700 whitespace-pre-wrap">{q.text}</p>
            </div>
          ))}

          {/* Clarification questions */}
          {questions.map((q: CompanionQuestion) => (
            <div key={q.id} className="border border-gray-200 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-800 mb-3 whitespace-pre-wrap">{q.text}</p>
              <textarea
                className="w-full border border-gray-300 rounded-lg p-3 min-h-[80px] text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder={q.optional ? '任意 — スキップ可能' : '回答してください'}
                value={answers[q.id] || ''}
                onChange={e => setAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
              />
            </div>
          ))}

          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm">{error}</div>
          )}

          <div className="flex gap-3">
            <button
              onClick={handleAnswerSubmit}
              disabled={submitting}
              className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? '処理中...' : '回答して続ける →'}
            </button>
            <button
              onClick={() => submitRun({ goal, success_criteria: successCriteria || undefined, risk, time_horizon: timeHorizon, exclusions })}
              disabled={submitting}
              className="px-4 py-3 text-sm text-gray-500 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              スキップして開始
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── Stage: review ────────────────────────────────────────────────────────────
  if (stage === 'review' && refinedRequest) {
    return (
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-2">確認：回答から読み取った内容</h2>
        <p className="text-gray-600 mb-6">
          以下の内容でシステムを設定します。修正が必要な場合は「戻る」を押してください。
        </p>

        <div className="bg-white border border-gray-200 rounded-lg p-5 space-y-3 mb-6">
          {inferenceSummary.map((inf, i) => (
            <div key={i} className="flex gap-3 text-sm">
              <span className="text-gray-500 w-40 shrink-0">{inf.field}:</span>
              <span className="font-medium text-gray-800">{inf.inferred_value}</span>
            </div>
          ))}
          {inferenceSummary.length === 0 && (
            <p className="text-sm text-gray-500">新たな推論はありませんでした。元の設定を使用します。</p>
          )}
        </div>

        {openUncertainties.length > 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <p className="text-xs font-semibold text-gray-500 mb-2">未確定の項目</p>
            {openUncertainties.map((u, i) => (
              <p key={i} className="text-xs text-gray-500">{u}</p>
            ))}
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm mb-4">{error}</div>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleReviewSubmit}
            disabled={submitting}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? '開始中...' : '問題ありません — 検証を開始 →'}
          </button>
          <button
            onClick={() => setStage('clarification')}
            disabled={submitting}
            className="px-4 py-3 text-sm text-gray-500 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            戻る
          </button>
        </div>
      </div>
    )
  }

  return null
}

export default InputPage
