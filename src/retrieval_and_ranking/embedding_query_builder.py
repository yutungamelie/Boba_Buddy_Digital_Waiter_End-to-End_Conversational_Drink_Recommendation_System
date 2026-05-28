"""
embedding_query_builder.py

Embedding query builder for the Boba Buddy Digital Waiter project.

This module converts an accumulated preference summary into an embedding-ready
query string.

Design principle:
    Do not embed only the latest user utterance.
    Build the query from accumulated preference state, hard constraints,
    soft preferences, situational intent, and optional user profile summary.

Why:
    The project notes suggest moving from word-level / last-message embedding
    toward context-aware, sentence-level, multilingual embeddings. This lets the
    retrieval stage search using the user's full preference context rather than
    only the most recent phrase.

This module is portfolio-safe:
    - no external embedding API call;
    - no production keys;
    - no Supabase dependency;
    - compatible with multilingual embedding models if added later.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class EmbeddingQueryResult:
    """Structured result for embedding query construction."""

    embedding_query: str
    language_policy: str
    source_fields: list[str]
    hard_constraints_text: str
    soft_preferences_text: str
    situational_intent_text: str
    user_profile_text: str | None
    notes: list[str]


SITUATIONAL_INTENT_MAP: dict[str, list[str]] = {
    "rainy day": ["warm", "comforting", "roasted", "mellow"],
    "comfort mood": ["comforting", "gentle", "smooth", "not too bitter"],
    "fried chicken pairing": ["refreshing", "citrus", "tea-based", "low sweetness", "not too creamy"],
    "tired": ["energizing", "tea-based caffeine", "not coffee unless allowed"],
    "safe but special": ["familiar base", "slightly novel flavor", "not too strange"],
}


def _dedupe_keep_order(items: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""

    out: list[str] = []
    for item in items:
        cleaned = str(item).strip()
        if cleaned and cleaned not in out:
            out.append(cleaned)
    return out


def _as_list(value: Any) -> list[str]:
    """Normalize a value into a list of non-empty strings."""

    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, set):
        return [str(x).strip() for x in sorted(value) if str(x).strip()]
    if isinstance(value, str):
        if not value.strip():
            return []
        return [value.strip()]
    return [str(value).strip()]


def normalize_hard_constraints(preference_summary: dict[str, Any]) -> list[str]:
    """Extract hard constraints from preference summary/state.

    Expected source shapes:
    - preference_summary["hard_constraints"] = ["no milk", "low sugar"]
    - preference_summary["state"] contains fields such as dairy_ok, coffee_ok,
      caffeine_ok, max_price, sugar, ice, temperature, one_drink_only.
    """

    constraints = _as_list(preference_summary.get("hard_constraints"))
    state = preference_summary.get("state") or {}

    if state.get("dairy_ok") is False or state.get("no_milk") is True:
        constraints.append("no milk / dairy-free")
    if state.get("coffee_ok") is False or state.get("no_coffee") is True:
        constraints.append("no coffee")
    if state.get("caffeine_ok") is False or state.get("no_caffeine") is True:
        constraints.append("no caffeine")
    if state.get("max_price") is not None:
        constraints.append(f"budget under {state['max_price']} NTD")
    if state.get("sugar") == "none":
        constraints.append("unsweetened / no sugar")
    elif state.get("sugar") == "low" or state.get("sweetness") == "low":
        constraints.append("low sweetness / not too sweet")
    if state.get("ice") == "none":
        constraints.append("no ice")
    elif state.get("ice") == "less":
        constraints.append("less ice")
    if state.get("temperature"):
        constraints.append(f"temperature preference: {state['temperature']}")
    if state.get("recommendation_count") == 1 or state.get("one_drink_only") is True:
        constraints.append("recommend only one drink")

    return _dedupe_keep_order(constraints)


def normalize_soft_preferences(preference_summary: dict[str, Any]) -> list[str]:
    """Extract soft preferences from preference summary/state."""

    prefs = []
    prefs.extend(_as_list(preference_summary.get("soft_preferences")))

    state = preference_summary.get("state") or {}
    prefs.extend(_as_list(state.get("soft_preferences")))
    prefs.extend(_as_list(state.get("taste_keywords")))
    prefs.extend(_as_list(state.get("avoid_keywords")))

    for key in ["drink_base", "sweetness", "ice", "temperature"]:
        if state.get(key):
            prefs.append(f"{key}: {state[key]}")

    return _dedupe_keep_order(prefs)


def normalize_situational_intent(preference_summary: dict[str, Any]) -> list[str]:
    """Extract and expand situational / emotional intent into retrieval features."""

    intents = []
    intents.extend(_as_list(preference_summary.get("situational_intent")))

    state = preference_summary.get("state") or {}
    intents.extend(_as_list(state.get("situational_intent")))

    expanded: list[str] = []
    for intent in _dedupe_keep_order(intents):
        expanded.append(intent)
        expanded.extend(SITUATIONAL_INTENT_MAP.get(intent, []))

    return _dedupe_keep_order(expanded)


def build_query_sections(
    preference_summary: dict[str, Any],
    user_profile: str | dict[str, Any] | None = None,
) -> EmbeddingQueryResult:
    """Build a structured embedding-query result."""

    source_fields: list[str] = []
    notes: list[str] = []

    updated_summary = str(preference_summary.get("updated_summary") or "").strip()
    if updated_summary:
        source_fields.append("updated_summary")

    hard_constraints = normalize_hard_constraints(preference_summary)
    if hard_constraints:
        source_fields.append("hard_constraints")

    soft_preferences = normalize_soft_preferences(preference_summary)
    if soft_preferences:
        source_fields.append("soft_preferences")

    situational = normalize_situational_intent(preference_summary)
    if situational:
        source_fields.append("situational_intent")
        notes.append("Situational intent was expanded into operational taste descriptors.")

    user_profile_text: str | None = None
    if user_profile:
        if isinstance(user_profile, dict):
            profile_parts = []
            for key, value in user_profile.items():
                if value is None:
                    continue
                profile_parts.append(f"{key}: {value}")
            user_profile_text = "; ".join(profile_parts)
        else:
            user_profile_text = str(user_profile).strip()
        if user_profile_text:
            source_fields.append("user_profile")

    hard_text = ", ".join(hard_constraints)
    soft_text = ", ".join(soft_preferences)
    situational_text = ", ".join(situational)

    # Multilingual-friendly: keep user-provided Chinese/English tags as-is, while
    # adding simple English descriptors for operational matching.
    query_parts: list[str] = []

    if updated_summary:
        query_parts.append(f"Accumulated preference summary: {updated_summary}")

    if hard_text:
        query_parts.append(f"Hard constraints that must not be violated: {hard_text}")

    if soft_text:
        query_parts.append(f"Soft taste preferences: {soft_text}")

    if situational_text:
        query_parts.append(f"Situational or emotional intent mapped to taste descriptors: {situational_text}")

    if user_profile_text:
        query_parts.append(f"User profile / history: {user_profile_text}")

    if not query_parts:
        query_parts.append("General bubble tea recommendation; ask clarifying question before retrieval.")
        notes.append("No strong preference signal found; retrieval should be delayed or used only for safe defaults.")

    embedding_query = " | ".join(query_parts)

    return EmbeddingQueryResult(
        embedding_query=embedding_query,
        language_policy="Preserve original Chinese/English terms; use multilingual sentence embeddings when available.",
        source_fields=source_fields,
        hard_constraints_text=hard_text,
        soft_preferences_text=soft_text,
        situational_intent_text=situational_text,
        user_profile_text=user_profile_text,
        notes=notes,
    )


def build_embedding_query(
    preference_summary: dict[str, Any],
    user_profile: str | dict[str, Any] | None = None,
) -> str:
    """Build the final embedding-ready query string.

    Parameters
    ----------
    preference_summary:
        Output from `src/preference_extraction/preference_summary.py`.
        It should include accumulated state, not only the last user prompt.
    user_profile:
        Optional user profile/history summary such as favorite drink styles,
        previously liked drinks, or disliked attributes.

    Returns
    -------
    str
        Embedding-ready query string.

    Example
    -------
    >>> summary = {
    ...   "updated_summary": "refreshing, low sweetness, no milk",
    ...   "hard_constraints": ["no milk"],
    ...   "soft_preferences": ["refreshing"],
    ...   "state": {"sweetness": "low", "dairy_ok": False}
    ... }
    >>> build_embedding_query(summary)
    'Accumulated preference summary: refreshing, low sweetness, no milk | Hard constraints that must not be violated: no milk / dairy-free | Soft taste preferences: refreshing, sweetness: low'
    """

    return build_query_sections(preference_summary, user_profile).embedding_query


def build_debug_payload(
    preference_summary: dict[str, Any],
    user_profile: str | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return debug payload useful for endpoint logs."""

    return asdict(build_query_sections(preference_summary, user_profile))


def main() -> None:
    """CLI demo.

    Example:
        python src/retrieval_and_ranking/embedding_query_builder.py \
          --summary '{"updated_summary":"清爽, 微糖, 不要奶","hard_constraints":["no milk"],"soft_preferences":["refreshing"],"state":{"dairy_ok":false,"sweetness":"low"}}'
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Build Digital Waiter embedding query from preference summary.")
    parser.add_argument("--summary", required=True, help="Preference summary JSON string.")
    parser.add_argument("--user-profile", default=None, help="Optional user profile summary.")
    args = parser.parse_args()

    summary = json.loads(args.summary)
    payload = build_debug_payload(summary, args.user_profile)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
