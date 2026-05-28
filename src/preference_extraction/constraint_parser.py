"""
constraint_parser.py

Rule-based hard-constraint parser for the Boba Buddy Digital Waiter project.

This module extracts machine-readable constraints from user messages. It is a
portfolio-safe mock parser designed to demonstrate how Digital Waiter should
separate hard constraints from soft preferences.

Hard constraints covered:
- no milk
- no coffee
- budget <= NTD amount
- low sugar / no sugar
- less ice / no ice
- no caffeine

Why this matters:
    UI testing treats "no milk", "not too sweet", and "within 60 NTD" as basic
    requirements that recommendation logic must respect. These should be parsed
    into structured fields and applied before ranking, not only mentioned in an
    LLM prompt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any


@dataclass
class ConstraintParseResult:
    """Structured hard-constraint output."""

    no_milk: bool | None = None
    no_coffee: bool | None = None
    no_caffeine: bool | None = None
    max_price: int | None = None
    sugar: str | None = None
    ice: str | None = None
    temperature: str | None = None
    one_drink_only: bool | None = None
    hard_constraints: list[str] | None = None
    parsing_notes: list[str] | None = None


NO_MILK_PATTERNS = [
    r"\bno milk\b",
    r"\bwithout milk\b",
    r"\bdairy[- ]?free\b",
    r"\bno dairy\b",
    r"\blactose[- ]?free\b",
    r"不要奶",
    r"不加奶",
    r"不含奶",
    r"不能喝奶",
    r"無奶",
    r"去奶",
    r"不要牛奶",
    r"不能喝牛奶",
]

NO_COFFEE_PATTERNS = [
    r"\bno coffee\b",
    r"\bwithout coffee\b",
    r"\bavoid coffee\b",
    r"\bnot coffee\b",
    r"不要咖啡",
    r"不喝咖啡",
    r"不能喝咖啡",
    r"去咖啡",
]

NO_CAFFEINE_PATTERNS = [
    r"\bno caffeine\b",
    r"\bcaffeine[- ]?free\b",
    r"\bdecaf\b",
    r"\bwithout caffeine\b",
    r"不要咖啡因",
    r"無咖啡因",
    r"不能喝咖啡因",
    r"不含咖啡因",
]

LOW_SUGAR_PATTERNS = [
    r"\blow sugar\b",
    r"\bless sugar\b",
    r"\bnot too sweet\b",
    r"\bnot sweet\b",
    r"\bhalf sugar\b",
    r"微糖",
    r"少糖",
    r"低糖",
    r"不要太甜",
    r"不太甜",
    r"半糖",
]

NO_SUGAR_PATTERNS = [
    r"\bno sugar\b",
    r"\bzero sugar\b",
    r"\bunsweetened\b",
    r"\bsugar[- ]?free\b",
    r"無糖",
    r"不要糖",
    r"零糖",
    r"去糖",
]

LESS_ICE_PATTERNS = [
    r"\bless ice\b",
    r"\blight ice\b",
    r"少冰",
    r"冰少一點",
]

NO_ICE_PATTERNS = [
    r"\bno ice\b",
    r"\bwithout ice\b",
    r"去冰",
    r"不要冰",
    r"無冰",
]

HOT_PATTERNS = [
    r"\bhot\b",
    r"\bwarm\b",
    r"熱的",
    r"溫的",
    r"溫熱",
]

COLD_PATTERNS = [
    r"\bcold\b",
    r"\biced\b",
    r"冰的",
    r"冷的",
]

ONE_DRINK_PATTERNS = [
    r"\bone drink\b",
    r"\bonly one\b",
    r"\bjust one\b",
    r"只要一杯",
    r"一杯就好",
    r"幫我挑一杯",
    r"選一杯",
]

BUDGET_PATTERNS = [
    r"(?:under|below|less than|within)\s*(\d{2,4})",
    r"(?:budget|max|maximum)\s*(?:is|=|:)?\s*(\d{2,4})",
    r"(\d{2,4})\s*(?:元|塊|ntd|NTD|台幣)?\s*(?:以內|以下|內)",
    r"預算\s*(?:是|=|:)?\s*(\d{2,4})",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    """Return True if any regex pattern matches text."""

    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def parse_budget(text: str) -> int | None:
    """Extract a budget upper bound from the message.

    Examples
    --------
    >>> parse_budget("預算 60 元內")
    60
    >>> parse_budget("under 80")
    80
    """

    for pattern in BUDGET_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                value = int(match.group(1))
            except (TypeError, ValueError):
                continue

            # Basic sanity range for drink prices.
            if 1 <= value <= 1000:
                return value

    return None


def parse_sugar(text: str) -> str | None:
    """Parse sugar-level hard/strong preference."""

    if _matches_any(text, NO_SUGAR_PATTERNS):
        return "none"
    if _matches_any(text, LOW_SUGAR_PATTERNS):
        return "low"
    return None


def parse_ice(text: str) -> str | None:
    """Parse ice-level hard/strong preference."""

    if _matches_any(text, NO_ICE_PATTERNS):
        return "none"
    if _matches_any(text, LESS_ICE_PATTERNS):
        return "less"
    return None


def parse_temperature(text: str) -> str | None:
    """Parse temperature preference."""

    if _matches_any(text, HOT_PATTERNS):
        return "hot"
    if _matches_any(text, COLD_PATTERNS):
        return "cold"
    return None


def parse_constraints(user_message: str) -> dict[str, Any]:
    """Parse constraints from a user message and return a simple dict.

    Suggested output shape from the portfolio plan:

    {
      "no_milk": True,
      "no_coffee": True,
      "max_price": 60,
      "sugar": "low",
      "ice": "less"
    }
    """

    text = user_message or ""

    result = ConstraintParseResult(
        no_milk=True if _matches_any(text, NO_MILK_PATTERNS) else None,
        no_coffee=True if _matches_any(text, NO_COFFEE_PATTERNS) else None,
        no_caffeine=True if _matches_any(text, NO_CAFFEINE_PATTERNS) else None,
        max_price=parse_budget(text),
        sugar=parse_sugar(text),
        ice=parse_ice(text),
        temperature=parse_temperature(text),
        one_drink_only=True if _matches_any(text, ONE_DRINK_PATTERNS) else None,
        hard_constraints=[],
        parsing_notes=[],
    )

    if result.no_milk:
        result.hard_constraints.append("no milk")
    if result.no_coffee:
        result.hard_constraints.append("no coffee")
    if result.no_caffeine:
        result.hard_constraints.append("no caffeine")
    if result.max_price is not None:
        result.hard_constraints.append(f"budget <= {result.max_price}")
    if result.sugar == "none":
        result.hard_constraints.append("no sugar")
    elif result.sugar == "low":
        result.hard_constraints.append("low sugar")
    if result.ice == "none":
        result.hard_constraints.append("no ice")
    elif result.ice == "less":
        result.hard_constraints.append("less ice")
    if result.temperature:
        result.hard_constraints.append(f"temperature = {result.temperature}")
    if result.one_drink_only:
        result.hard_constraints.append("one drink only")

    # Potential conflicts worth surfacing to the state layer.
    if result.no_caffeine and _matches_any(text, [r"提神", r"\benergizing\b", r"\bwake me up\b"]):
        result.parsing_notes.append("Potential conflict: user wants energizing but no caffeine.")

    if result.no_milk and _matches_any(text, [r"奶蓋", r"奶茶", r"\bmilk tea\b", r"\bmilk foam\b", r"\bcreamy\b"]):
        result.parsing_notes.append("Potential conflict: user mentions creamy/milk-style drink but also says no milk.")

    return asdict(result)


def parse_hard_constraints(user_message: str) -> dict[str, Any]:
    """Alias for parse_constraints, kept for readability in other modules."""

    return parse_constraints(user_message)


def merge_constraints(
    previous_constraints: dict[str, Any] | None,
    new_constraints: dict[str, Any],
) -> dict[str, Any]:
    """Merge constraints into existing state.

    Rule:
        - New explicit constraints overwrite old values.
        - None values do not erase previous constraints.
        - hard_constraints list is regenerated from merged fields.
    """

    previous_constraints = previous_constraints or {}
    merged = dict(previous_constraints)

    for key, value in new_constraints.items():
        if key in {"hard_constraints", "parsing_notes"}:
            continue
        if value is not None:
            merged[key] = value

    # Regenerate human-readable hard constraints from merged state.
    hard_constraints: list[str] = []
    if merged.get("no_milk"):
        hard_constraints.append("no milk")
    if merged.get("no_coffee"):
        hard_constraints.append("no coffee")
    if merged.get("no_caffeine"):
        hard_constraints.append("no caffeine")
    if merged.get("max_price") is not None:
        hard_constraints.append(f"budget <= {merged['max_price']}")
    if merged.get("sugar") == "none":
        hard_constraints.append("no sugar")
    elif merged.get("sugar") == "low":
        hard_constraints.append("low sugar")
    if merged.get("ice") == "none":
        hard_constraints.append("no ice")
    elif merged.get("ice") == "less":
        hard_constraints.append("less ice")
    if merged.get("temperature"):
        hard_constraints.append(f"temperature = {merged['temperature']}")
    if merged.get("one_drink_only"):
        hard_constraints.append("one drink only")

    merged["hard_constraints"] = hard_constraints
    merged["parsing_notes"] = list(previous_constraints.get("parsing_notes", [])) + list(new_constraints.get("parsing_notes", []))
    return merged


def main() -> None:
    """Small CLI demo.

    Example:
        python src/preference_extraction/constraint_parser.py "我想喝無糖少冰，不要奶，預算60元內"
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Parse Digital Waiter hard constraints.")
    parser.add_argument("message", help="User message.")
    args = parser.parse_args()

    print(json.dumps(parse_constraints(args.message), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
