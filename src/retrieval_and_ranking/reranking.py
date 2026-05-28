"""
reranking.py

Mock reranker for the Boba Buddy Digital Waiter project.

This module demonstrates that final recommendation ranking should not rely only
on embedding similarity. The reranker combines:
- semantic similarity;
- hard constraint satisfaction;
- menu metadata match;
- availability;
- user profile match.

Suggested scoring formula from the project plan:

    final_score = (
        0.35 * semantic_similarity
        + 0.30 * constraint_match
        + 0.15 * menu_metadata_match
        + 0.10 * availability
        + 0.10 * user_profile_match
    )

This file is portfolio-safe and uses only candidate dictionaries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RerankedCandidate:
    """One reranked candidate with explainable component scores."""

    drink_id: str
    rank: int
    final_score: float
    semantic_similarity: float
    constraint_match: float
    menu_metadata_match: float
    availability: float
    user_profile_match: float
    violations: list[str]
    matched_preferences: list[str]
    recommendation_reason: str
    candidate: dict[str, Any]


WEIGHTS = {
    "semantic_similarity": 0.35,
    "constraint_match": 0.30,
    "menu_metadata_match": 0.15,
    "availability": 0.10,
    "user_profile_match": 0.10,
}


def _get_state(preference_summary: dict[str, Any]) -> dict[str, Any]:
    """Return state dict from preference summary."""

    return preference_summary.get("state") or preference_summary


def check_constraint_match(candidate: dict[str, Any], preference_summary: dict[str, Any]) -> tuple[float, list[str]]:
    """Score hard-constraint satisfaction.

    Returns:
        1.0 if no violations;
        0.0 if any clear violation;
        0.5 if metadata missing for a relevant constraint.
    """

    state = _get_state(preference_summary)
    metadata = candidate.get("metadata") or {}
    violations: list[str] = []
    unknowns: list[str] = []

    contains_dairy = metadata.get("contains_dairy")
    contains_coffee = metadata.get("contains_coffee")
    caffeine_level = metadata.get("caffeine_level")
    price = candidate.get("price")

    if state.get("dairy_ok") is False or state.get("no_milk") is True:
        if contains_dairy is True:
            violations.append("contains dairy but user requested no milk")
        elif contains_dairy is None:
            unknowns.append("dairy metadata missing")

    if state.get("coffee_ok") is False or state.get("no_coffee") is True:
        if contains_coffee is True:
            violations.append("contains coffee but user requested no coffee")
        elif contains_coffee is None:
            unknowns.append("coffee metadata missing")

    if state.get("caffeine_ok") is False or state.get("no_caffeine") is True:
        if caffeine_level not in {None, "none", "zero", "caffeine_free"}:
            violations.append("contains caffeine but user requested no caffeine")
        elif caffeine_level is None:
            unknowns.append("caffeine metadata missing")

    max_price = state.get("max_price")
    if max_price is not None:
        try:
            if float(price) > float(max_price):
                violations.append(f"price {price} exceeds budget {max_price}")
        except (TypeError, ValueError):
            unknowns.append("price metadata missing or invalid")

    if violations:
        return 0.0, violations

    if unknowns:
        return 0.5, unknowns

    return 1.0, []


def score_menu_metadata_match(candidate: dict[str, Any], preference_summary: dict[str, Any]) -> tuple[float, list[str]]:
    """Score how well structured drink metadata matches soft preferences."""

    state = _get_state(preference_summary)
    metadata = candidate.get("metadata") or {}
    taste_tags = set(str(tag).lower() for tag in metadata.get("taste_tags", []))
    drink_base = set(str(base).lower() for base in metadata.get("drink_base", []))
    semantic_description = str(metadata.get("semantic_description", "")).lower()

    soft_preferences = []
    soft_preferences.extend(preference_summary.get("soft_preferences") or [])
    soft_preferences.extend(state.get("soft_preferences") or [])
    soft_preferences.extend(state.get("taste_keywords") or [])
    soft_preferences.extend(state.get("situational_intent") or [])

    if state.get("drink_base"):
        soft_preferences.append(str(state["drink_base"]))

    if state.get("sweetness") == "low":
        soft_preferences.append("low sweetness")

    matched: list[str] = []
    possible = 0

    def has_any(*keywords: str) -> bool:
        joined = " ".join(list(taste_tags) + list(drink_base) + [semantic_description])
        return any(keyword.lower() in joined for keyword in keywords)

    for pref in soft_preferences:
        pref_lower = str(pref).lower()
        possible += 1

        if pref_lower in taste_tags or pref_lower in drink_base or pref_lower in semantic_description:
            matched.append(str(pref))
        elif pref_lower in {"refreshing", "清爽"} and has_any("refreshing", "light", "citrus", "fruit"):
            matched.append(str(pref))
        elif pref_lower in {"not too sweet", "low sweetness", "low", "微糖", "少糖"} and has_any("low", "light"):
            matched.append(str(pref))
        elif pref_lower in {"milky", "milk_tea"} and has_any("milk", "milky", "smooth"):
            matched.append(str(pref))
        elif pref_lower in {"energizing", "提神", "tired"} and has_any("energizing", "tea_based", "high"):
            matched.append(str(pref))
        elif pref_lower in {"rainy day", "comforting", "comfort mood"} and has_any("roasted", "mellow", "comforting", "smooth"):
            matched.append(str(pref))
        elif pref_lower in {"fried chicken pairing"} and has_any("refreshing", "citrus", "tea_based"):
            matched.append(str(pref))

    if possible == 0:
        return 0.5, []

    return len(matched) / possible, matched


def score_availability(candidate: dict[str, Any]) -> float:
    """Score candidate availability."""

    metadata = candidate.get("metadata") or {}
    availability = metadata.get("availability", True)

    if availability is True:
        return 1.0
    if availability is False:
        return 0.0
    return 0.5


def score_user_profile_match(candidate: dict[str, Any], user_profile: dict[str, Any] | None = None) -> float:
    """Score how well candidate matches simple user profile/history.

    Supported optional profile fields:
    - liked_tags: list[str]
    - disliked_tags: list[str]
    - liked_drink_ids: list[str]
    - disliked_drink_ids: list[str]
    """

    if not user_profile:
        return 0.5

    metadata = candidate.get("metadata") or {}
    tags = set(str(tag).lower() for tag in metadata.get("taste_tags", []))
    drink_id = str(candidate.get("drink_id"))

    liked_tags = set(str(tag).lower() for tag in user_profile.get("liked_tags", []))
    disliked_tags = set(str(tag).lower() for tag in user_profile.get("disliked_tags", []))
    liked_drink_ids = set(str(x) for x in user_profile.get("liked_drink_ids", []))
    disliked_drink_ids = set(str(x) for x in user_profile.get("disliked_drink_ids", []))

    if drink_id in disliked_drink_ids:
        return 0.0
    if drink_id in liked_drink_ids:
        return 1.0
    if tags.intersection(disliked_tags):
        return 0.2
    if tags.intersection(liked_tags):
        return 0.9

    return 0.5


def normalize_semantic_similarity(value: float | int | None) -> float:
    """Normalize cosine-like similarity into [0, 1]."""

    if value is None:
        return 0.5

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.5

    # If value is already 0..1, keep it. If cosine could be -1..1, map it.
    if 0.0 <= score <= 1.0:
        return score

    if -1.0 <= score <= 1.0:
        return (score + 1.0) / 2.0

    return max(0.0, min(score, 1.0))


def build_recommendation_reason(
    candidate: dict[str, Any],
    matched_preferences: list[str],
    violations: list[str],
) -> str:
    """Build short grounded reason for portfolio output."""

    name = candidate.get("name_en") or candidate.get("name_zh") or candidate.get("drink_id")

    if violations and any("but user requested" in v or "exceeds budget" in v for v in violations):
        return f"{name} should be excluded because it violates: {', '.join(violations)}."

    if matched_preferences:
        return f"{name} matches: {', '.join(matched_preferences)}."

    return f"{name} is included as a possible candidate, but the match is uncertain."


def compute_final_score(
    *,
    semantic_similarity: float,
    constraint_match: float,
    menu_metadata_match: float,
    availability: float,
    user_profile_match: float,
) -> float:
    """Compute final weighted score."""

    return (
        WEIGHTS["semantic_similarity"] * semantic_similarity
        + WEIGHTS["constraint_match"] * constraint_match
        + WEIGHTS["menu_metadata_match"] * menu_metadata_match
        + WEIGHTS["availability"] * availability
        + WEIGHTS["user_profile_match"] * user_profile_match
    )


def rerank_candidates(
    candidates: list[dict[str, Any]],
    preference_summary: dict[str, Any],
    user_profile: dict[str, Any] | None = None,
    top_k: int = 3,
    exclude_hard_violations: bool = True,
) -> list[dict[str, Any]]:
    """Rerank candidates with a multi-factor scoring formula.

    Parameters
    ----------
    candidates:
        Candidate dictionaries from `candidate_retrieval.retrieve_candidates`.
    preference_summary:
        Accumulated preference summary/state.
    user_profile:
        Optional user profile/history.
    top_k:
        Number of final candidates to return.
    exclude_hard_violations:
        If True, candidates with clear hard-constraint violations are not
        returned even if semantic similarity is high.

    Returns
    -------
    list[dict]
        Reranked candidates with component scores and reasons.
    """

    reranked: list[RerankedCandidate] = []

    for candidate in candidates:
        semantic_similarity = normalize_semantic_similarity(
            candidate.get("semantic_similarity", candidate.get("similarity"))
        )
        constraint_match, violations = check_constraint_match(candidate, preference_summary)
        menu_metadata_match, matched_preferences = score_menu_metadata_match(candidate, preference_summary)
        availability = score_availability(candidate)
        user_profile_match = score_user_profile_match(candidate, user_profile)

        final_score = compute_final_score(
            semantic_similarity=semantic_similarity,
            constraint_match=constraint_match,
            menu_metadata_match=menu_metadata_match,
            availability=availability,
            user_profile_match=user_profile_match,
        )

        # Strongly demote invalid hard-constraint candidates. If excluded, they
        # won't be returned, but keeping a clear score makes debug easier.
        clear_hard_violation = constraint_match == 0.0
        if clear_hard_violation:
            final_score = min(final_score, 0.25)

        reranked.append(
            RerankedCandidate(
                drink_id=str(candidate.get("drink_id")),
                rank=0,
                final_score=round(final_score, 6),
                semantic_similarity=round(semantic_similarity, 6),
                constraint_match=round(constraint_match, 6),
                menu_metadata_match=round(menu_metadata_match, 6),
                availability=round(availability, 6),
                user_profile_match=round(user_profile_match, 6),
                violations=violations,
                matched_preferences=matched_preferences,
                recommendation_reason=build_recommendation_reason(candidate, matched_preferences, violations),
                candidate=candidate,
            )
        )

    if exclude_hard_violations:
        filtered = [
            item for item in reranked
            if not (item.constraint_match == 0.0 and any("but user requested" in v or "exceeds budget" in v for v in item.violations))
        ]
    else:
        filtered = reranked

    sorted_items = sorted(filtered, key=lambda item: item.final_score, reverse=True)[:top_k]

    output: list[dict[str, Any]] = []
    for rank, item in enumerate(sorted_items, start=1):
        item.rank = rank
        output.append(asdict(item))

    return output


def build_reranking_debug(
    candidates: list[dict[str, Any]],
    preference_summary: dict[str, Any],
    user_profile: dict[str, Any] | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """Return debug payload containing selected and excluded candidates."""

    selected = rerank_candidates(
        candidates,
        preference_summary,
        user_profile=user_profile,
        top_k=top_k,
        exclude_hard_violations=True,
    )

    all_scored = rerank_candidates(
        candidates,
        preference_summary,
        user_profile=user_profile,
        top_k=len(candidates),
        exclude_hard_violations=False,
    )

    selected_ids = {item["drink_id"] for item in selected}
    excluded = [item for item in all_scored if item["drink_id"] not in selected_ids]

    return {
        "weights": WEIGHTS,
        "top_k": top_k,
        "selected": selected,
        "excluded_or_lower_ranked": excluded,
        "violations_in_selected": [
            {"drink_id": item["drink_id"], "violations": item["violations"]}
            for item in selected
            if item["violations"]
        ],
    }


def main() -> None:
    """CLI demo using mock retrieval candidates.

    Example:
        python src/retrieval_and_ranking/reranking.py
    """

    import json

    demo_candidates = [
        {
            "drink_id": "demo-drink-001",
            "name_en": "Demo Green Tea",
            "semantic_similarity": 0.86,
            "price": 45,
            "metadata": {
                "contains_dairy": False,
                "contains_coffee": False,
                "caffeine_level": "medium",
                "availability": True,
                "drink_base": ["tea"],
                "taste_tags": ["refreshing", "light", "tea_based"],
                "semantic_description": "Light green tea, refreshing and clean, no milk.",
            },
        },
        {
            "drink_id": "demo-drink-003",
            "name_en": "Demo Light Milk Tea",
            "semantic_similarity": 0.88,
            "price": 65,
            "metadata": {
                "contains_dairy": True,
                "contains_coffee": False,
                "caffeine_level": "medium",
                "availability": True,
                "drink_base": ["milk", "tea"],
                "taste_tags": ["milky", "smooth"],
                "semantic_description": "Light milk tea.",
            },
        },
    ]

    demo_summary = {
        "updated_summary": "refreshing, low sweetness, no milk",
        "hard_constraints": ["no milk"],
        "soft_preferences": ["refreshing"],
        "state": {"dairy_ok": False, "sweetness": "low", "max_price": 60},
    }

    print(json.dumps(build_reranking_debug(demo_candidates, demo_summary), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
