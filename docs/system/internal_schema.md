# Internal Schema

## Schema principle
The schema must model:
- intent
- evidence
- validation
- rejection
- recommendation conditions

Not just requirements and architecture.

---

## User Intent Object

```json
{
  "run_id": "string",
  "created_at": "ISO-8601",
  "raw_goal": "string",
  "domain": "investment_research",
  "user_goal_summary": "string",
  "success_definition": "string",
  "risk_preference": "very_low | low | medium | high",
  "time_horizon_preference": "fast | one_day | one_week | one_month | quality_over_speed",
  "automation_preference": "advice_only | research_assist | semi_automated | full_if_safe",
  "must_not_do": ["string"],
  "available_inputs": ["string"],
  "open_uncertainties": ["string"]
}
```

## Research Spec Object

```json
{
  "spec_id": "string",
  "run_id": "string",
  "primary_objective": "string",
  "secondary_objectives": ["string"],
  "problem_frame": "string",
  "assumption_space": ["string"],
  "constraints": {
    "time": "string",
    "budget": "string",
    "tooling": ["string"],
    "forbidden_behaviors": ["string"]
  },
  "evidence_requirements": {
    "required_data": ["string"],
    "optional_data": ["string"],
    "proxy_data_allowed": true,
    "evidence_gaps": ["string"]
  },
  "validation_requirements": {
    "must_test": ["string"],
    "must_compare": ["string"],
    "disqualifying_failures": ["string"],
    "minimum_evidence_standard": "weak | moderate | strong"
  },
  "recommendation_requirements": {
    "must_return_runner_up": true,
    "must_return_rejections": true,
    "must_surface_unknowns": true,
    "allow_no_valid_candidate": true
  }
}
```

## Candidate Object

```json
{
  "candidate_id": "string",
  "name": "string",
  "candidate_type": "baseline | conservative | exploratory | hybrid | rejectable_variant",
  "summary": "string",
  "architecture_outline": ["string"],
  "core_assumptions": ["string"],
  "required_inputs": ["string"],
  "validation_burden": "low | medium | high",
  "implementation_complexity": "low | medium | high",
  "expected_strengths": ["string"],
  "expected_weaknesses": ["string"],
  "known_risks": ["string"]
}
```

## Validation Plan Object

```json
{
  "validation_plan_id": "string",
  "candidate_id": "string",
  "test_types": ["offline_backtest", "walk_forward", "paper_run", "stress_test", "other"],
  "metrics": ["string"],
  "time_windows": ["string"],
  "required_data_sources": ["string"],
  "failure_conditions": ["string"],
  "comparison_targets": ["string"],
  "notes": "string"
}
```

## Audit Object

```json
{
  "candidate_id": "string",
  "issues": [
    {
      "issue_id": "string",
      "severity": "low | medium | high | critical",
      "category": "assumption | evidence | leakage | complexity | realism | observability | recommendation_risk",
      "title": "string",
      "explanation": "string",
      "mitigation": "string",
      "disqualifying": false
    }
  ]
}
```

## Recommendation Object

```json
{
  "best_candidate_id": "string",
  "runner_up_candidate_id": "string",
  "rejected_candidate_ids": ["string"],
  "ranking_logic": ["string"],
  "open_unknowns": ["string"],
  "critical_conditions": ["string"],
  "monitoring_or_recheck_rules": ["string"],
  "confidence_label": "low | medium | high",
  "confidence_explanation": "string",
  "next_validation_steps": ["string"]
}
```
