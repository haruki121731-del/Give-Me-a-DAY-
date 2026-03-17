from src.execution.statistical_tests import run_statistical_tests


def test_statistical_tests_include_split_metrics():
    returns = [0.001] * 100 + [-0.0005] * 40
    stats = run_statistical_tests(returns)

    assert "t_test_p_value" in stats
    assert "sharpe_p_value" in stats
    assert "in_sample_mean" in stats
    assert "out_of_sample_mean" in stats
    assert stats["in_sample_mean"] != stats["out_of_sample_mean"]
