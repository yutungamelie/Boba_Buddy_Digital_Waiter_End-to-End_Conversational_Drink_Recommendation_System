"""
constraint_match_check.py

Constraint-match checker for the Boba Buddy Digital Waiter project.

Purpose
-------
Check whether a recommended drink violates the user's hard constraints.

This module is designed for the Digital Waiter evaluation layer. It answers the
most important UI-testing question:

    Did the final recommendation actually follow the user's explicit constraints,
    or did the LLM merely produce text that sounds reasonable?

Hard constraints covered in this portfolio-safe implementation:
- no milk / dairy-free
- no coffee
- no caffeine
- maximum price
- low sugar / no sugar
- ice preference
- temperature preference
- radius / distance constraint

This file does not call external APIs and does not use production data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ConstraintCheckResult:
    """Result returned by `check_constraint_match`."""

    passed: bool
    violations: list[str]
    warnings: list[str]
    score: float
    checked_constraints: list[str]


def _get_nested(source: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    """Get first available value from top-level or metadata keys."""

    for key in keys:
        if key in source:
            return source[key]

    metadata = source.get("metadata") or {}
    for key in keys:
        if key in metadata:
            return metadata[key]

    return default


def _as_bool(value: Any) -> bool | None:
    """Convert common truthy/falsy values to bool, otherwise None."""

    if isinstance(value, bool):
        return value

    if value is None:
        return None

    text = str(value).strip().lower()

    if text in {"true", "yes", "y", "1", "contains", "present"}:
        return True

    if text in {"false", "no", "n", "0", "none", "absent"}:
        return False

    return None


def _as_float(value: Any) -> float | None:
    """Convert value to float when possible."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_constraints(constraints: dict[str, Any]) -> dict[str, Any]:
    """Normalize constraint aliases from preference extraction / risk policy."""

    normalized = dict(constraints or {})

    # no milk / dairy
    if normalized.get("dairy_ok") is False:
        normalized["no_milk"] = True

    # no coffee
    if normalized.get("coffee_ok") is False:
        normalized["no_coffee"] = True

    # no caffeine
    if normalized.get("caffeine_ok") is False:
        normalized["no_caffeine"] = True

    # budget
    if normalized.get("budget_max") is not None and normalized.get("max_price") is None:
        normalized["max_price"] = normalized.get("budget_max")

    # radius
    if normalized.get("radius") is not None and normalized.get("radius_meters") is None:
        normalized["radius_meters"] = normalized.get("radius")

    return normalized


def _check_no_milk(drink: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return violation/warning for no-milk check."""

    contains_dairy = _as_bool(
        _get_nested(
            drink,
            ["contains_dairy", "has_dairy", "contains_milk", "is_milk_based"],
        )
    )

    name_text = " ".join(
        str(x).lower()
        for x in [
            drink.get("name_en"),
            drink.get("name_zh"),
            drink.get("drink_name_english"),
            drink.get("drink_name_chinese"),
            _get_nested(drink, ["semantic_description", "short_summary"], ""),
        ]
        if x is not None
    )

    dairy_keywords = [
        "milk",
        "latte",
        "cream",
        "creamy",
        "yogurt",
        "cheese",
        "foam",
        "奶",
        "鮮奶",
        "拿鐵",
        "奶茶",
        "奶蓋",
        "優格",
        "乳",
    ]

    keyword_suggests_dairy = any(keyword in name_text for keyword in dairy_keywords)

    if contains_dairy is True:
        return "contains dairy but user requested no milk", None

    if contains_dairy is None and keyword_suggests_dairy:
        return "drink name/summary suggests dairy but dairy metadata is missing", None

    if contains_dairy is None:
        return None, "dairy metadata missing; cannot fully verify no-milk constraint"

    return None, None


def _check_no_coffee(drink: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return violation/warning for no-coffee check."""

    contains_coffee = _as_bool(
        _get_nested(
            drink,
            ["contains_coffee", "has_coffee", "is_coffee_based"],
        )
    )

    name_text = " ".join(
        str(x).lower()
        for x in [
            drink.get("name_en"),
            drink.get("name_zh"),
            drink.get("drink_name_english"),
            drink.get("drink_name_chinese"),
            _get_nested(drink, ["semantic_description", "short_summary"], ""),
        ]
        if x is not None
    )

    coffee_keywords = ["coffee", "latte", "espresso", "americano", "mocha", "咖啡", "拿鐵", "美式"]

    keyword_suggests_coffee = any(keyword in name_text for keyword in coffee_keywords)

    if contains_coffee is True:
        return "contains coffee but user requested no coffee", None

    if contains_coffee is None and keyword_suggests_coffee:
        return "drink name/summary suggests coffee but coffee metadata is missing", None

    if contains_coffee is None:
        return None, "coffee metadata missing; cannot fully verify no-coffee constraint"

    return None, None


def _check_no_caffeine(drink: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return violation/warning for no-caffeine check."""

    caffeine_level = _get_nested(drink, ["caffeine_level", "caffeine"], None)

    if caffeine_level is None:
        return None, "caffeine metadata missing; cannot fully verify no-caffeine constraint"

    level = str(caffeine_level).strip().lower()

    if level in {"none", "zero", "0", "caffeine_free", "decaf", "no"}:
        return None, None

    return f"caffeine_level={caffeine_level} but user requested no caffeine", None


def _check_max_price(drink: dict[str, Any], max_price: Any) -> tuple[str | None, str | None]:
    """Return violation/warning for budget check."""

    price = _as_float(_get_nested(drink, ["price", "drink_price"], None))
    max_price_num = _as_float(max_price)

    if max_price_num is None:
        return None, "max_price constraint is not numeric"

    if price is None:
        return None, "price metadata missing; cannot fully verify budget constraint"

    if price > max_price_num:
        return f"price {price:g} exceeds budget {max_price_num:g}", None

    return None, None


def _check_sugar(drink: dict[str, Any], sugar_constraint: Any) -> tuple[str | None, str | None]:
    """Return violation/warning for sugar preference/constraint."""

    if sugar_constraint is None:
        return None, None

    sugar = str(sugar_constraint).strip().lower()
    sweetness = _get_nested(drink, ["sweetness", "sweetness_tendency", "sugar_level"], None)

    if sweetness is None:
        return None, "sweetness metadata missing; cannot fully verify sugar constraint"

    sweetness_text = str(sweetness).strip().lower()

    if sugar in {"none", "no", "zero", "unsweetened"}:
        if any(token in sweetness_text for token in ["high", "medium", "sweet", "brown sugar", "黑糖"]):
            return f"sweetness_tendency={sweetness} but user requested no sugar", None

    if sugar in {"low", "less", "not_too_sweet"}:
        if any(token in sweetness_text for token in ["high", "very sweet", "brown sugar", "黑糖"]):
            return f"sweetness_tendency={sweetness} but user requested low sweetness", None

    return None, None


def _check_ice(drink: dict[str, Any], ice_constraint: Any) -> tuple[str | None, str | None]:
    """Return violation/warning for ice preference."""

    if ice_constraint is None:
        return None, None

    available_ice = _get_nested(drink, ["available_ice", "ice_options"], None)

    if available_ice is None:
        return None, "ice metadata missing; cannot fully verify ice constraint"

    ice = str(ice_constraint).strip().lower()
    options = [str(x).lower() for x in available_ice] if isinstance(available_ice, list) else [str(available_ice).lower()]

    if ice == "none" and not any(option in {"none", "no", "no_ice", "去冰", "無冰"} for option in options):
        return "no-ice option not available according to metadata", None

    if ice == "less" and not any(option in {"less", "light", "less_ice", "少冰"} for option in options):
        return "less-ice option not available according to metadata", None

    return None, None


def _check_temperature(drink: dict[str, Any], temperature_constraint: Any) -> tuple[str | None, str | None]:
    """Return violation/warning for temperature preference."""

    if temperature_constraint is None:
        return None, None

    available_temperature = _get_nested(drink, ["available_temperature", "temperature_options"], None)

    if available_temperature is None:
        return None, "temperature metadata missing; cannot fully verify temperature constraint"

    requested = str(temperature_constraint).strip().lower()
    options = (
        [str(x).lower() for x in available_temperature]
        if isinstance(available_temperature, list)
        else [str(available_temperature).lower()]
    )

    if requested == "hot" and not any(option in {"hot", "warm", "熱", "溫"} for option in options):
        return "hot option not available according to metadata", None

    if requested == "cold" and not any(option in {"cold", "iced", "冰", "冷"} for option in options):
        return "cold option not available according to metadata", None

    return None, None


def _check_radius(drink: dict[str, Any], radius_meters: Any) -> tuple[str | None, str | None]:
    """Return violation/warning for location radius."""

    distance = _as_float(_get_nested(drink, ["distance_meters", "distance"], None))
    radius = _as_float(radius_meters)

    if radius is None:
        return None, "radius_meters constraint is not numeric"

    if distance is None:
        return None, "distance_meters missing; cannot fully verify location constraint"

    if distance > radius:
        return f"distance_meters {distance:g} exceeds radius_meters {radius:g}", None

    return None, None


def check_constraint_match(drink: dict[str, Any], constraints: dict[str, Any]) -> dict[str, Any]:
    """Check whether a drink recommendation satisfies hard constraints.

    Parameters
    ----------
    drink:
        Candidate/recommended drink dictionary. Can contain fields at top level
        or inside `metadata`.
    constraints:
        Parsed constraints from `constraint_parser.py` or preference state.

    Returns
    -------
    dict
        {
          "passed": bool,
          "violations": list[str],
          "warnings": list[str],
          "score": float,
          "checked_constraints": list[str]
        }

    Score policy
    ------------
    - 1.0: checked constraints pass and no warnings
    - 0.5: no clear violation, but metadata is missing/uncertain
    - 0.0: at least one clear violation
    """

    constraints = _normalize_constraints(constraints)
    violations: list[str] = []
    warnings: list[str] = []
    checked_constraints: list[str] = []

    def add_result(label: str, result: tuple[str | None, str | None]) -> None:
        violation, warning = result
        checked_constraints.append(label)

        if violation:
            violations.append(violation)

        if warning:
            warnings.append(warning)

    if constraints.get("no_milk") is True:
        add_result("no_milk", _check_no_milk(drink))

    if constraints.get("no_coffee") is True:
        add_result("no_coffee", _check_no_coffee(drink))

    if constraints.get("no_caffeine") is True:
        add_result("no_caffeine", _check_no_caffeine(drink))

    if constraints.get("max_price") is not None:
        add_result("max_price", _check_max_price(drink, constraints.get("max_price")))

    if constraints.get("sugar") is not None or constraints.get("sweetness") is not None:
        add_result("sugar", _check_sugar(drink, constraints.get("sugar") or constraints.get("sweetness")))

    if constraints.get("ice") is not None:
        add_result("ice", _check_ice(drink, constraints.get("ice")))

    if constraints.get("temperature") is not None:
        add_result("temperature", _check_temperature(drink, constraints.get("temperature")))

    if constraints.get("radius_meters") is not None:
        add_result("radius_meters", _check_radius(drink, constraints.get("radius_meters")))

    passed = not violations

    if violations:
        score = 0.0
    elif warnings:
        score = 0.5
    else:
        score = 1.0

    return asdict(
        ConstraintCheckResult(
            passed=passed,
            violations=violations,
            warnings=warnings,
            score=score,
            checked_constraints=checked_constraints,
        )
    )


def check_top_drinks_constraints(
    top_drinks: list[dict[str, Any]],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    """Check all top drinks and summarize violations."""

    results = [check_constraint_match(drink, constraints) for drink in top_drinks]

    passed_all = all(result["passed"] for result in results)
    scores = [result["score"] for result in results]
    average_score = sum(scores) / len(scores) if scores else 0.0

    violations_by_drink = []
    warnings_by_drink = []

    for drink, result in zip(top_drinks, results):
        drink_id = drink.get("drink_id") or drink.get("id") or drink.get("name_en") or drink.get("name_zh")

        if result["violations"]:
            violations_by_drink.append(
                {
                    "drink_id": drink_id,
                    "violations": result["violations"],
                }
            )

        if result["warnings"]:
            warnings_by_drink.append(
                {
                    "drink_id": drink_id,
                    "warnings": result["warnings"],
                }
            )

    return {
        "passed_all": passed_all,
        "average_constraint_score": round(average_score, 6),
        "n_drinks_checked": len(top_drinks),
        "violations_by_drink": violations_by_drink,
        "warnings_by_drink": warnings_by_drink,
        "drink_level_results": results,
    }


def main() -> None:
    """CLI demo."""

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Check whether a drink violates hard constraints.")
    parser.add_argument("--drink", required=True, help="Drink JSON string.")
    parser.add_argument("--constraints", required=True, help="Constraints JSON string.")
    args = parser.parse_args()

    drink = json.loads(args.drink)
    constraints = json.loads(args.constraints)

    print(json.dumps(check_constraint_match(drink, constraints), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
