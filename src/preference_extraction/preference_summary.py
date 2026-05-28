"""
preference_summary.py

Rule-based preference summary builder for the Boba Buddy Digital Waiter project.

This module turns multi-turn conversation into a structured preference summary.
It demonstrates the key design principle from the project notes:

    Do not embed only the user's final sentence.
    Instead, summarize multi-turn preferences into:
    - hard constraints
    - soft preferences
    - situational / emotional intent
    - updated summary

The output can then be used as the embedding query for candidate retrieval,
the state shown in UI, and the grounding context for final response generation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

try:
    from .constraint_parser import parse_constraints, merge_constraints
except ImportError:  # pragma: no cover - allows standalone script execution
    from constraint_parser import parse_constraints, merge_constraints


@dataclass
class PreferenceSummary:
    """Structured multi-turn preference summary."""

    hard_constraints: list[str]
    soft_preferences: list[str]
    situational_intent: list[str]
    updated_summary: str
    state: dict[str, Any]
    missing_slots: list[str]
    notes: list[str]


SOFT_PREFERENCE_PATTERNS: dict[str, list[str]] = {
    "refreshing": [
        r"\brefreshing\b",
        r"\blight\b",
        r"清爽",
        r"爽口",
        r"不要太膩",
        r"不膩",
    ],
    "fruity": [
        r"\bfruity\b",
        r"\bfruit\b",
        r"水果",
        r"果茶",
        r"果香",
    ],
    "tea-forward": [
        r"\btea[- ]?forward\b",
        r"\bstrong tea\b",
        r"茶味重",
        r"茶感",
        r"茶香",
    ],
    "not too tea-heavy": [
        r"不要茶味太重",
        r"茶味不要太重",
        r"不要太茶",
        r"not too tea",
    ],
    "milky": [
        r"\bmilky\b",
        r"\bmilk tea\b",
        r"\bcreamy\b",
        r"奶香",
        r"奶茶",
        r"奶味",
        r"濃郁",
    ],
    "not too heavy": [
        r"\bnot too heavy\b",
        r"\bless heavy\b",
        r"不要太厚重",
        r"不要太膩",
        r"不膩",
        r"清爽一點",
    ],
    "comforting": [
        r"\bcomforting\b",
        r"\bcozy\b",
        r"安慰",
        r"療癒",
        r"幸福感",
        r"溫暖",
    ],
    "energizing": [
        r"\benergizing\b",
        r"\bwake me up\b",
        r"\bboost\b",
        r"提神",
        r"醒腦",
        r"很累",
    ],
    "safe but special": [
        r"\bspecial but safe\b",
        r"\bdifferent but not too weird\b",
        r"特別但安全",
        r"不一樣但不要太奇怪",
        r"不要太怪",
    ],
    "not sour": [
        r"\bnot sour\b",
        r"不要酸",
        r"不酸",
    ],
    "not bitter": [
        r"\bnot bitter\b",
        r"不要苦",
        r"不苦",
        r"不要澀",
        r"不澀",
    ],
    "brown sugar aroma": [
        r"\bbrown sugar\b",
        r"黑糖香",
        r"黑糖",
    ],
    "roasted": [
        r"\broasted\b",
        r"\bhojicha\b",
        r"焙茶",
        r"烘焙",
        r"炭焙",
    ],
}

SITUATIONAL_INTENT_PATTERNS: dict[str, list[str]] = {
    "rainy day": [
        r"\brainy day\b",
        r"下雨",
        r"雨天",
    ],
    "comfort mood": [
        r"\bbad mood\b",
        r"\bfeel down\b",
        r"心情不好",
        r"想被安慰",
    ],
    "fried chicken pairing": [
        r"\bfried chicken\b",
        r"炸雞",
        r"鹽酥雞",
    ],
    "tired": [
        r"\btired\b",
        r"很累",
        r"疲倦",
    ],
}

REQUIRED_SLOTS = ["drink_base", "sweetness", "dairy_ok"]


def _matches_any(text: str, patterns: list[str]) -> bool:
    """Return True if any regex pattern matches text."""

    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def extract_soft_preferences(text: str) -> list[str]:
    """Extract soft preference tags from one message."""

    preferences: list[str] = []
    for label, patterns in SOFT_PREFERENCE_PATTERNS.items():
        if _matches_any(text, patterns):
            preferences.append(label)
    return preferences


def extract_situational_intent(text: str) -> list[str]:
    """Extract situational / emotional intent tags from one message."""

    intents: list[str] = []
    for label, patterns in SITUATIONAL_INTENT_PATTERNS.items():
        if _matches_any(text, patterns):
            intents.append(label)
    return intents


def infer_drink_base_from_text(text: str) -> str | None:
    """Infer a rough drink base from message text."""

    if re.search(r"果茶|水果|fruit", text, flags=re.IGNORECASE):
        return "fruit_or_fruit_tea"
    if re.search(r"奶茶|奶香|milky|milk tea|creamy", text, flags=re.IGNORECASE):
        return "milk_tea"
    if re.search(r"茶|tea|烏龍|紅茶|綠茶|焙茶", text, flags=re.IGNORECASE):
        return "tea"
    if re.search(r"咖啡|coffee|latte", text, flags=re.IGNORECASE):
        return "coffee"
    return None


def infer_state_patch_from_message(text: str) -> dict[str, Any]:
    """Infer non-hard-constraint state fields from one message."""

    patch: dict[str, Any] = {}

    drink_base = infer_drink_base_from_text(text)
    if drink_base:
        patch["drink_base"] = drink_base

    soft_preferences = extract_soft_preferences(text)
    if soft_preferences:
        patch["soft_preferences"] = soft_preferences

    situational_intent = extract_situational_intent(text)
    if situational_intent:
        patch["situational_intent"] = situational_intent

    if re.search(r"一杯|one drink|just one|only one", text, flags=re.IGNORECASE):
        patch["recommendation_count"] = 1

    return patch


def merge_list_unique(old: list[str] | None, new: list[str] | None) -> list[str]:
    """Merge lists while preserving order and uniqueness."""

    out: list[str] = []
    for item in (old or []) + (new or []):
        if item and item not in out:
            out.append(item)
    return out


def update_preference_state(
    state: dict[str, Any] | None,
    user_message: str,
) -> dict[str, Any]:
    """Update preference state using one user message.

    The update is intentionally transparent and rule-based:
    - hard constraints are parsed by constraint_parser;
    - soft preferences and situational intents are appended;
    - explicit latest values overwrite previous values when present.
    """

    state = dict(state or {})
    message = user_message or ""

    parsed_constraints = parse_constraints(message)
    state = merge_constraints(state, parsed_constraints)

    patch = infer_state_patch_from_message(message)

    if "drink_base" in patch:
        state["drink_base"] = patch["drink_base"]

    if "recommendation_count" in patch:
        state["recommendation_count"] = patch["recommendation_count"]

    if "soft_preferences" in patch:
        state["soft_preferences"] = merge_list_unique(state.get("soft_preferences"), patch["soft_preferences"])

    if "situational_intent" in patch:
        state["situational_intent"] = merge_list_unique(state.get("situational_intent"), patch["situational_intent"])

    # Mirror selected constraints into more convenient state names.
    if state.get("no_milk") is True:
        state["dairy_ok"] = False
    if state.get("no_coffee") is True:
        state["coffee_ok"] = False
    if state.get("no_caffeine") is True:
        state["caffeine_ok"] = False
    if state.get("sugar") is not None:
        state["sweetness"] = state.get("sugar")

    return state


def summarize_from_state(state: dict[str, Any]) -> str:
    """Build a concise summary string for embedding and debug logs."""

    parts: list[str] = []

    for key in ["drink_base", "sweetness", "ice", "temperature"]:
        value = state.get(key)
        if value:
            parts.append(str(value).replace("_", " "))

    hard_constraints = state.get("hard_constraints") or []
    parts.extend(hard_constraints)

    parts.extend(state.get("soft_preferences") or [])
    parts.extend(state.get("situational_intent") or [])

    if state.get("recommendation_count") == 1:
        parts.append("one drink only")

    # Remove duplicates while preserving order.
    unique_parts = []
    for part in parts:
        if part and part not in unique_parts:
            unique_parts.append(part)

    return ", ".join(unique_parts)


def find_missing_slots(state: dict[str, Any]) -> list[str]:
    """Return high-value missing slots for clarifying questions."""

    missing: list[str] = []

    if not state.get("drink_base"):
        missing.append("drink_base")
    if not state.get("sweetness"):
        missing.append("sweetness")
    if "dairy_ok" not in state:
        missing.append("dairy_ok")

    # Useful but not always mandatory.
    if not state.get("ice"):
        missing.append("ice")
    if not state.get("max_price"):
        missing.append("budget")

    return missing


def build_preference_summary(
    conversation_history: list[dict],
    current_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured preference summary from multi-turn conversation.

    Parameters
    ----------
    conversation_history:
        List of chat turns. Only user turns are used for preference extraction.
        Example:
        [
            {"role": "user", "content": "我想喝清爽一點"},
            {"role": "assistant", "content": "要不要奶？"},
            {"role": "user", "content": "不要奶，微糖"}
        ]

    current_state:
        Optional existing preference state.

    Returns
    -------
    dict
        {
          "hard_constraints": ["no milk", "low sugar"],
          "soft_preferences": ["refreshing", "fruity"],
          "situational_intent": ["rainy day"],
          "updated_summary": "refreshing, fruity, no milk, low sugar",
          "state": {...},
          "missing_slots": [...]
        }
    """

    state = dict(current_state or {})
    notes: list[str] = []

    for turn in conversation_history or []:
        if turn.get("role") != "user":
            continue

        content = str(turn.get("content", "")).strip()
        if not content:
            continue

        state = update_preference_state(state, content)

    hard_constraints = state.get("hard_constraints") or []
    soft_preferences = state.get("soft_preferences") or []
    situational_intent = state.get("situational_intent") or []
    updated_summary = summarize_from_state(state)
    missing_slots = find_missing_slots(state)

    if not updated_summary:
        notes.append("No strong preference signal detected yet.")

    if situational_intent:
        notes.append("Situational intent should be mapped to operational taste features before embedding.")

    return asdict(
        PreferenceSummary(
            hard_constraints=hard_constraints,
            soft_preferences=soft_preferences,
            situational_intent=situational_intent,
            updated_summary=updated_summary,
            state=state,
            missing_slots=missing_slots,
            notes=notes,
        )
    )


def build_preference_summary_from_messages(messages: list[str]) -> dict[str, Any]:
    """Convenience wrapper for a list of user-only messages."""

    history = [{"role": "user", "content": msg} for msg in messages]
    return build_preference_summary(history)


def build_embedding_query(preference_summary: dict[str, Any]) -> str:
    """Return the text that should be embedded for candidate retrieval.

    This is intentionally the updated multi-turn summary, not the latest user
    utterance alone.
    """

    return preference_summary.get("updated_summary", "")


def main() -> None:
    """Small CLI demo.

    Example:
        python src/preference_extraction/preference_summary.py \
          "我想喝清爽一點" "不要奶，微糖" "適合下雨天"
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Build Digital Waiter multi-turn preference summary.")
    parser.add_argument("messages", nargs="+", help="User messages in order.")
    args = parser.parse_args()

    summary = build_preference_summary_from_messages(args.messages)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
