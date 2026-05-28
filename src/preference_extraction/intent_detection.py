"""
intent_detection.py

Rule-based mock intent detection for the Boba Buddy Digital Waiter project.

This module demonstrates the intent-routing idea behind the Digital Waiter
`ai_recommendations3` workflow. The real production system may use an LLM or a
more robust classifier, but this portfolio version intentionally uses simple,
transparent rules.

Supported intents:
- clear
- unrelated
- conversational
- refine_inquiry
- recommend_drinks

Reference design:
    The project notes describe an intent branch in `ai_recommendations3` with
    clear / unrelated / conversational / refine_inquiry / recommend_drinks.
    This module mocks that routing behavior without calling any external API.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Literal


Intent = Literal[
    "clear",
    "unrelated",
    "conversational",
    "refine_inquiry",
    "recommend_drinks",
]


@dataclass
class IntentResult:
    """Structured intent detection output."""

    intent: Intent
    confidence: float
    reason: str
    recommendation_ready: bool
    requires_state_update: bool


CLEAR_PATTERNS = [
    r"\bclear\b",
    r"\breset\b",
    r"\bstart over\b",
    r"\bnew search\b",
    r"清除",
    r"重來",
    r"重新開始",
    r"換一個話題",
    r"忘掉",
]

CONVERSATIONAL_PATTERNS = [
    r"\bhi\b",
    r"\bhello\b",
    r"\bhey\b",
    r"\bthanks?\b",
    r"\bthank you\b",
    r"\bbye\b",
    r"你好",
    r"嗨",
    r"哈囉",
    r"謝謝",
    r"掰掰",
    r"再見",
]

RECOMMEND_PATTERNS = [
    r"\brecommend\b",
    r"\bsuggest\b",
    r"\bchoose\b",
    r"\bpick\b",
    r"\bwhat should i drink\b",
    r"\bone drink\b",
    r"推薦",
    r"建議",
    r"幫我選",
    r"幫我挑",
    r"我想喝",
    r"我要喝",
    r"想喝",
    r"喝什麼",
    r"只要一杯",
    r"一杯最適合",
]

REFINE_PATTERNS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bwithout\b",
    r"\bless\b",
    r"\bmore\b",
    r"\binstead\b",
    r"\bactually\b",
    r"\bchange\b",
    r"\bmake it\b",
    r"不要",
    r"不想",
    r"少一點",
    r"多一點",
    r"改成",
    r"換成",
    r"其實",
    r"等一下",
    r"算了",
    r"微糖",
    r"無糖",
    r"少冰",
    r"去冰",
    r"不要奶",
    r"不要咖啡",
]

DRINK_DOMAIN_TERMS = [
    "drink",
    "tea",
    "milk",
    "coffee",
    "boba",
    "bubble",
    "sugar",
    "ice",
    "fruit",
    "refreshing",
    "sweet",
    "caffeine",
    "latte",
    "oolong",
    "black tea",
    "green tea",
    "飲料",
    "茶",
    "奶",
    "咖啡",
    "珍珠",
    "波霸",
    "甜",
    "冰",
    "水果",
    "清爽",
    "提神",
    "奶茶",
    "紅茶",
    "綠茶",
    "烏龍",
    "焙茶",
    "無糖",
    "微糖",
    "少冰",
    "去冰",
]

UNRELATED_HINTS = [
    "weather",
    "stock",
    "homework",
    "python bug",
    "movie",
    "politics",
    "天氣",
    "股票",
    "作業",
    "電影",
    "政治",
]


def _contains_any_pattern(text: str, patterns: list[str]) -> bool:
    """Return True if any regex pattern matches."""

    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _contains_drink_domain_term(text: str) -> bool:
    """Return True when the message appears related to drinks."""

    lowered = text.lower()
    return any(term.lower() in lowered for term in DRINK_DOMAIN_TERMS)


def _has_conversation_history(conversation_history: list[dict] | None) -> bool:
    """Whether a previous conversation state likely exists."""

    return bool(conversation_history)


def _latest_assistant_asked_question(conversation_history: list[dict] | None) -> bool:
    """Detect whether the last assistant turn was likely a clarifying question."""

    if not conversation_history:
        return False

    for turn in reversed(conversation_history):
        if turn.get("role") == "assistant":
            content = str(turn.get("content", ""))
            return "?" in content or "？" in content or "想要" in content or "prefer" in content.lower()

    return False


def detect_intent_detail(
    user_message: str,
    conversation_history: list[dict] | None = None,
) -> IntentResult:
    """Detect user intent with simple transparent rules.

    Parameters
    ----------
    user_message:
        Latest user message.
    conversation_history:
        Optional list of chat turns, e.g.
        `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`.

    Returns
    -------
    IntentResult
        Structured intent routing result.

    Intent definitions
    ------------------
    clear:
        User wants to reset / clear / start over.

    unrelated:
        User message is not related to drink recommendation.

    conversational:
        Greeting, thanks, small talk, or polite closing.

    refine_inquiry:
        User modifies, narrows, negates, or answers a follow-up question about
        a previous recommendation context.

    recommend_drinks:
        User asks for a drink recommendation or provides drink preferences.
    """

    message = (user_message or "").strip()

    if not message:
        return IntentResult(
            intent="conversational",
            confidence=0.4,
            reason="Empty message treated as conversational.",
            recommendation_ready=False,
            requires_state_update=False,
        )

    if _contains_any_pattern(message, CLEAR_PATTERNS):
        return IntentResult(
            intent="clear",
            confidence=0.95,
            reason="User explicitly requested reset / clear.",
            recommendation_ready=False,
            requires_state_update=True,
        )

    # If the latest assistant asked a question, the user's reply often refines
    # preference state even if it is short, e.g. "不要奶" or "fruit tea".
    if _latest_assistant_asked_question(conversation_history) and (
        _contains_drink_domain_term(message) or _contains_any_pattern(message, REFINE_PATTERNS)
    ):
        return IntentResult(
            intent="refine_inquiry",
            confidence=0.82,
            reason="User appears to answer or refine a previous clarifying question.",
            recommendation_ready=False,
            requires_state_update=True,
        )

    if _contains_any_pattern(message, CONVERSATIONAL_PATTERNS) and not _contains_drink_domain_term(message):
        return IntentResult(
            intent="conversational",
            confidence=0.85,
            reason="Message looks like greeting, thanks, or small talk.",
            recommendation_ready=False,
            requires_state_update=False,
        )

    if _contains_any_pattern(message, REFINE_PATTERNS) and _has_conversation_history(conversation_history):
        return IntentResult(
            intent="refine_inquiry",
            confidence=0.80,
            reason="User modifies or narrows an existing drink inquiry.",
            recommendation_ready=False,
            requires_state_update=True,
        )

    if _contains_any_pattern(message, RECOMMEND_PATTERNS) or _contains_drink_domain_term(message):
        return IntentResult(
            intent="recommend_drinks",
            confidence=0.78,
            reason="Message contains drink-domain terms or recommendation request.",
            recommendation_ready=True,
            requires_state_update=True,
        )

    if any(term in message.lower() for term in UNRELATED_HINTS):
        return IntentResult(
            intent="unrelated",
            confidence=0.75,
            reason="Message appears unrelated to drink recommendation.",
            recommendation_ready=False,
            requires_state_update=False,
        )

    return IntentResult(
        intent="unrelated",
        confidence=0.55,
        reason="No drink-domain or conversational signal detected.",
        recommendation_ready=False,
        requires_state_update=False,
    )


def detect_intent(
    user_message: str,
    conversation_history: list[dict] | None = None,
) -> Intent:
    """Return only the intent string.

    This is the minimal mock function suggested for the portfolio repository.

    Examples
    --------
    >>> detect_intent("我想喝清爽一點的，不要太甜", [])
    'recommend_drinks'
    >>> detect_intent("等一下，我今天不想喝奶類了", [{"role": "user", "content": "我想喝奶茶"}])
    'refine_inquiry'
    >>> detect_intent("重來", [])
    'clear'
    """

    return detect_intent_detail(user_message, conversation_history).intent


def should_ask_clarifying_question(result: IntentResult, missing_slots: list[str] | None = None) -> bool:
    """Decide whether the assistant should clarify instead of recommend immediately."""

    missing_slots = missing_slots or []

    if result.intent in {"clear", "unrelated", "conversational"}:
        return False

    if result.intent == "refine_inquiry":
        return bool(missing_slots)

    if result.intent == "recommend_drinks":
        # In the real system this should be controlled by recommendation_readiness.
        # This portfolio mock asks a question when many important preference slots
        # are still missing.
        high_value_slots = {"drink_base", "sweetness", "dairy_ok", "temperature", "budget"}
        missing_high_value = high_value_slots.intersection(missing_slots)
        return len(missing_high_value) >= 2

    return False


def main() -> None:
    """Small CLI demo.

    Example:
        python src/preference_extraction/intent_detection.py "我想喝清爽一點的，不要太甜"
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Rule-based Digital Waiter intent detection demo.")
    parser.add_argument("message", help="Latest user message.")
    args = parser.parse_args()

    result = detect_intent_detail(args.message, conversation_history=[])
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
