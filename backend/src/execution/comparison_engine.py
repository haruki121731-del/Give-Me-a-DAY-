"""Round 3 cross-candidate metric comparison matrix."""

from __future__ import annotations

import uuid

from src.domain.models import (
    CandidateMetricValue,
    ComparisonMetric,
    ComparisonMatrixData,
    ComparisonResult,
    ExecutionBasedRanking,
    RankingRationale,
)


def build_comparison_result(run_id: str, candidate_metrics: dict[str, dict[str, float]]) -> ComparisonResult:
    candidate_ids = list(candidate_metrics.keys())
    baseline = candidate_ids[0] if candidate_ids else ""

    metric_names = sorted({m for vals in candidate_metrics.values() for m in vals.keys()})
    metrics: list[ComparisonMetric] = []

    for metric_name in metric_names:
        values: dict[str, CandidateMetricValue] = {}
        base_v = candidate_metrics.get(baseline, {}).get(metric_name, 0.0)

        ranked = sorted(
            ((cid, candidate_metrics.get(cid, {}).get(metric_name, 0.0)) for cid in candidate_ids),
            key=lambda x: x[1],
            reverse=True,
        )
        rank_map = {cid: rank + 1 for rank, (cid, _) in enumerate(ranked)}

        for cid in candidate_ids:
            v = candidate_metrics.get(cid, {}).get(metric_name, 0.0)
            values[cid] = CandidateMetricValue(
                value=float(v),
                vs_baseline=float(v - base_v),
                is_significant=False,
                p_value=1.0,
                rank=rank_map[cid],
            )

        metrics.append(ComparisonMetric(metric_name=metric_name, values=values))

    ordered = sorted(
        candidate_ids,
        key=lambda cid: candidate_metrics.get(cid, {}).get("sharpe", 0.0),
        reverse=True,
    )
    best = ordered[0] if ordered else None
    runner_up = ordered[1] if len(ordered) > 1 else None

    rationale = []
    if best:
        rationale.append(RankingRationale(
            comparison_axis="sharpe",
            winner=best,
            margin=f"vs baseline: {candidate_metrics.get(best, {}).get('sharpe', 0.0) - candidate_metrics.get(baseline, {}).get('sharpe', 0.0):.4f}",
        ))

    return ComparisonResult(
        comparison_id=f"cmp_{uuid.uuid4().hex[:8]}",
        run_id=run_id,
        comparison_matrix=ComparisonMatrixData(
            candidates=candidate_ids,
            baseline_candidate_id=baseline,
            metrics=metrics,
        ),
        execution_based_rejections=[],
        execution_based_ranking=ExecutionBasedRanking(
            recommended_best=best,
            recommended_runner_up=runner_up,
            ranking_rationale=rationale,
        ),
    )
