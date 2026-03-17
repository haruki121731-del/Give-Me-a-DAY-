from src.execution.comparison_engine import build_comparison_result


def test_build_comparison_result_ranks_candidates():
    result = build_comparison_result(
        "run_cmp_001",
        {
            "C01": {"sharpe": 0.8, "total_return": 0.12},
            "C02": {"sharpe": 1.0, "total_return": 0.10},
        },
    )

    assert result.run_id == "run_cmp_001"
    assert result.comparison_matrix.baseline_candidate_id == "C01"
    assert result.execution_based_ranking.recommended_best == "C02"
    assert len(result.comparison_matrix.metrics) >= 2
