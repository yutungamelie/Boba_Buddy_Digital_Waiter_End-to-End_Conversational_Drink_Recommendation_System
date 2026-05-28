"""
recommendation_reliability_score.py

Recommendation reliability scoring for the Boba Buddy Digital Waiter project.

Purpose
-------
Turn Digital Waiter recommendation quality into a simple risk-aware engineering
score.

The central portfolio idea:
    A fluent LLM response is not necessarily reliable.
    Recommendation reliability depends on:
        - hard-constraint satisfaction
        - semantic relevance
        - location validity
        - conversation-state consistency
        - response grounding

This module computes:
    {
      "score": 0.82,
      "level": "high",
      "needs_clarification": False,
      "risk_flags": []
    }

It can be used in API tests, UI/endpoint comparison, and offline evaluation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ReliabilityScoreResult:
    """Output of `compute_reliability_score`."""

    score: float
    level: str
    needs_clarification: bool
    risk_flags: list[str]
    component_scores: dict[str, float]


DEFAULT_WEIGHTS = {
    "constraint_score": 0.30,
    "semantic_score": 0.20,
    "location_score": 0.15,
    "state_consistency_score": 0.20,
    "grounding_score": 0.15,
}


def _clip_score(value: float | int | None, default: float = 0.0) -> float:
    """Clamp score to [0, 1]."""

    if value is None:
        return default

    try:
        score = float(value)
    except (TypeError, ValueError):
        return default

    return max(0.0, min(1.0, score))


def _score_level(score: float) -> str:
    """Convert numeric reliability score to level."""

    if score >= 0.80:
        return "high"

    if score >= 0.50:
        return "medium"

    return "low"


def _build_risk_flags(component_scores: dict[str, float]) -> list[str]:
    """Build risk flags from component scores."""

    flags: list[str] = []

    if component_scores["constraint_score"] < 1.0:
        if component_scores["constraint_score"] == 0.0:
            flags.append("hard_constraint_violation")
        else:
            flags.append("constraint_metadata_uncertain")

    if component_scores["semantic_score"] < 0.5:
        flags.append("low_semantic_relevance")

    if component_scores["location_score"] < 1.0:
        if component_scores["location_score"] == 0.0:
            flags.append("location_or_radius_invalid")
        else:
            flags.append("location_metadata_uncertain")

    if component_scores["state_consistency_score"] < 1.0:
        if component_scores["state_consistency_score"] == 0.0:
            flags.append("conversation_state_inconsistent")
        else:
            flags.append("conversation_state_uncertain")

    if component_scores["grounding_score"] < 1.0:
        if component_scores["grounding_score"] == 0.0:
            flags.append("ungrounded_or_hallucinated_response")
        else:
            flags.append("response_grounding_uncertain")

    return flags


def compute_reliability_score(
    constraint_score: float,
    semantic_score: float,
    location_score: float,
    state_consistency_score: float,
    grounding_score: float,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Compute recommendation reliability score.

    Parameters
    ----------
    constraint_score:
        Whether top recommendations satisfy hard constraints.
    semantic_score:
        Whether recommendations match soft preferences / situational intent.
    location_score:
        Whether recommendations are within radius / location-valid.
    state_consistency_score:
        Whether final recommendation reflects multi-turn preference state.
    grounding_score:
        Whether final response only mentions candidate drinks and supported
        metadata-based reasons.
    weights:
        Optional component weights. Defaults to `DEFAULT_WEIGHTS`.

    Returns
    -------
    dict
        {
          "score": 0.82,
          "level": "high",
          "needs_clarification": False,
          "risk_flags": [],
          "component_scores": {...}
        }

    Clarification policy
    --------------------
    The system needs clarification or fallback if:
    - overall score < 0.80;
    - hard constraint score is 0;
    - grounding score is 0;
    - state consistency is 0.
    """

    weights = weights or DEFAULT_WEIGHTS

    component_scores = {
        "constraint_score": _clip_score(constraint_score),
        "semantic_score": _clip_score(semantic_score),
        "location_score": _clip_score(location_score),
        "state_consistency_score": _clip_score(state_consistency_score),
        "grounding_score": _clip_score(grounding_score),
    }

    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("weights must sum to a positive value")

    normalized_weights = {key: value / total_weight for key, value in weights.items()}

    score = sum(component_scores[key] * normalized_weights[key] for key in component_scores)
    score = round(score, 6)

    level = _score_level(score)
    risk_flags = _build_risk_flags(component_scores)

    needs_clarification = (
        score < 0.80
        or component_scores["constraint_score"] == 0.0
        or component_scores["grounding_score"] == 0.0
        or component_scores["state_consistency_score"] == 0.0
    )

    return asdict(
        ReliabilityScoreResult(
            score=score,
            level=level,
            needs_clarification=needs_clarification,
            risk_flags=risk_flags,
            component_scores=component_scores,
        )
    )


def score_from_endpoint_debug(endpoint_response: dict[str, Any]) -> dict[str, Any]:
    """Compute reliability from endpoint/debug payload when available.

    This helper accepts common fields produced by the portfolio modules:
    - constraint_score / average_constraint_score
    - semantic_score / semantic_relevance_score
    - location_score / location_validity_score
    - state_consistency_score / conversation_state_consistency
    - grounding_score / response_grounding_score
    """

    reliability = endpoint_response.get("reliability") or {}
    constraint_debug = endpoint_response.get("constraint_debug") or {}
    response_debug = endpoint_response.get("response_debug") or {}

    constraint_score = (
        reliability.get("constraint_match_score")
        or endpoint_response.get("constraint_score")
        or constraint_debug.get("average_constraint_score")
        or 0.0
    )

    semantic_score = (
        reliability.get("semantic_relevance_score")
        or endpoint_response.get("semantic_score")
        or endpoint_response.get("semantic_relevance_score")
        or 0.5
    )

    location_score = (
        reliability.get("location_validity_score")
        or endpoint_response.get("location_score")
        or endpoint_response.get("location_validity_score")
        or 0.5
    )

    state_score = (
        reliability.get("conversation_state_consistency")
        or endpoint_response.get("state_consistency_score")
        or endpoint_response.get("conversation_state_consistency")
        or 0.5
    )

    grounding_score = (
        reliability.get("top_k_grounding_score")
        or reliability.get("response_grounding_score")
        or endpoint_response.get("grounding_score")
        or endpoint_response.get("response_grounding_score")
        or (1.0 if response_debug.get("final_response_items_subset_of_top_k") is True else 0.5)
    )

    return compute_reliability_score(
        constraint_score=constraint_score,
        semantic_score=semantic_score,
        location_score=location_score,
        state_consistency_score=state_score,
        grounding_score=grounding_score,
    )


def choose_recommendation_action(score_result: dict[str, Any]) -> dict[str, Any]:
    """Choose a recommendation action from reliability score.

    Actions:
    - show_recommendation
    - show_cautious_recommendation
    - ask_clarifying_question
    - fallback_no_reliable_match
    """

    score = score_result.get("score", 0.0)
    flags = set(score_result.get("risk_flags", []))

    if "hard_constraint_violation" in flags:
        return {
            "action": "fallback_no_reliable_match",
            "reason": "Hard constraint violation detected.",
        }

    if "ungrounded_or_hallucinated_response" in flags:
        return {
            "action": "ask_clarifying_question",
            "reason": "Final response is not grounded in selected candidates.",
        }

    if "conversation_state_inconsistent" in flags:
        return {
            "action": "ask_clarifying_question",
            "reason": "Conversation state appears inconsistent.",
        }

    if score >= 0.80:
        return {
            "action": "show_recommendation",
            "reason": "Recommendation reliability is high.",
        }

    if score >= 0.50:
        return {
            "action": "show_cautious_recommendation",
            "reason": "Recommendation reliability is medium; show uncertainty or ask one follow-up.",
        }

    return {
        "action": "ask_clarifying_question",
        "reason": "Recommendation reliability is low.",
    }


def build_reliability_report(
    constraint_score: float,
    semantic_score: float,
    location_score: float,
    state_consistency_score: float,
    grounding_score: float,
) -> dict[str, Any]:
    """Compute reliability score and recommended action together."""

    score_result = compute_reliability_score(
        constraint_score=constraint_score,
        semantic_score=semantic_score,
        location_score=location_score,
        state_consistency_score=state_consistency_score,
        grounding_score=grounding_score,
    )

    action = choose_recommendation_action(score_result)

    return {
        **score_result,
        "recommended_action": action["action"],
        "action_reason": action["reason"],
    }


def main() -> None:
    """CLI demo."""

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Compute Digital Waiter recommendation reliability score.")
    parser.add_argument("--constraint-score", type=float, required=True)
    parser.add_argument("--semantic-score", type=float, required=True)
    parser.add_argument("--location-score", type=float, required=True)
    parser.add_argument("--state-consistency-score", type=float, required=True)
    parser.add_argument("--grounding-score", type=float, required=True)
    args = parser.parse_args()

    report = build_reliability_report(
        constraint_score=args.constraint_score,
        semantic_score=args.semantic_score,
        location_score=args.location_score,
        state_consistency_score=args.state_consistency_score,
        grounding_score=args.grounding_score,
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
