"""
ui_endpoint_comparison.py

UI vs endpoint comparison utilities for the Boba Buddy Digital Waiter project.

Purpose
-------
Convert UI testing symptoms and raw endpoint responses into a structured
debugging record.

UI testing tells us:
    What did the user see? What felt wrong?

Endpoint testing tells us:
    What did the backend actually receive, retrieve, rank, and return?

This module helps compare both sides and assign a suspected layer:
- frontend_request_payload
- frontend_state_or_rendering
- backend_intent_or_state
- backend_retrieval_or_ranking
- backend_response_generation
- no_mismatch_detected

This file is portfolio-safe and uses only mock / exported test records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class UIEndpointComparisonResult:
    """Structured comparison row."""

    test_case_id: str
    user_prompt: str
    ui_observed_behavior: str
    endpoint_intent: str | None
    endpoint_composite_query: str | None
    endpoint_top_drinks: list[str]
    ui_displayed_drinks: list[str]
    matched_or_not: str
    suspected_layer: str
    notes: list[str]


def _extract_drink_ids(drinks: Any) -> list[str]:
    """Extract drink IDs or names from endpoint/UI drink arrays."""

    if drinks is None:
        return []

    if isinstance(drinks, str):
        return [drinks]

    if isinstance(drinks, list):
        out: list[str] = []
        for item in drinks:
            if isinstance(item, dict):
                value = (
                    item.get("drink_id")
                    or item.get("id")
                    or item.get("name_en")
                    or item.get("drink_name_english")
                    or item.get("name_zh")
                    or item.get("drink_name_chinese")
                )
                if value is not None:
                    out.append(str(value))
            elif item is not None:
                out.append(str(item))
        return out

    return []


def _extract_endpoint_intent(endpoint_response: dict[str, Any]) -> str | None:
    """Extract intent from endpoint response/debug payload."""

    return (
        endpoint_response.get("intent")
        or endpoint_response.get("endpoint_intent")
        or (endpoint_response.get("debug") or {}).get("intent")
    )


def _extract_composite_query(endpoint_response: dict[str, Any]) -> str | None:
    """Extract composite query from endpoint response/debug payload."""

    return (
        endpoint_response.get("composite_query")
        or endpoint_response.get("updated_composite_query")
        or endpoint_response.get("endpoint_composite_query")
        or (endpoint_response.get("debug") or {}).get("composite_query")
        or ((endpoint_response.get("preference_summary") or {}).get("updated_summary"))
    )


def _extract_endpoint_top_drinks(endpoint_response: dict[str, Any]) -> list[str]:
    """Extract endpoint top drink identifiers."""

    return _extract_drink_ids(
        endpoint_response.get("top_drinks")
        or endpoint_response.get("endpoint_top_drinks")
        or ((endpoint_response.get("ranking_debug") or {}).get("top_drinks"))
    )


def _sets_match_in_order(a: list[str], b: list[str]) -> bool:
    """Whether two lists match exactly in order."""

    return a == b


def _sets_overlap(a: list[str], b: list[str]) -> bool:
    """Whether two lists share at least one item."""

    return bool(set(a).intersection(set(b)))


def _detect_constraint_symptom(ui_observed_behavior: str) -> bool:
    """Detect whether UI symptom mentions constraint violation."""

    text = ui_observed_behavior.lower()
    keywords = [
        "violat",
        "no milk",
        "milk despite",
        "no coffee",
        "coffee despite",
        "budget",
        "over price",
        "太甜",
        "不要奶",
        "不要咖啡",
        "超過預算",
        "違反",
    ]
    return any(keyword in text for keyword in keywords)


def _detect_memory_symptom(ui_observed_behavior: str) -> bool:
    """Detect whether UI symptom mentions memory/state issue."""

    text = ui_observed_behavior.lower()
    keywords = [
        "forget",
        "memory",
        "previous",
        "state",
        "changed mind",
        "stale",
        "忘記",
        "多輪",
        "改口",
        "狀態",
        "前面",
    ]
    return any(keyword in text for keyword in keywords)


def _detect_rendering_symptom(ui_observed_behavior: str) -> bool:
    """Detect whether UI symptom mentions rendering/language issue."""

    text = ui_observed_behavior.lower()
    keywords = [
        "render",
        "garbled",
        "mojibake",
        "encoding",
        "unreadable",
        "亂碼",
        "顯示",
        "讀不懂",
    ]
    return any(keyword in text for keyword in keywords)


def infer_suspected_layer(
    *,
    ui_observed_behavior: str,
    endpoint_top_drinks: list[str],
    ui_displayed_drinks: list[str],
    endpoint_intent: str | None,
    endpoint_composite_query: str | None,
    endpoint_response: dict[str, Any],
) -> tuple[str, list[str]]:
    """Infer suspected layer from UI/endpoint comparison."""

    notes: list[str] = []

    exact_match = _sets_match_in_order(endpoint_top_drinks, ui_displayed_drinks)
    overlap = _sets_overlap(endpoint_top_drinks, ui_displayed_drinks)

    endpoint_status = endpoint_response.get("status")

    if endpoint_status not in {None, "success"}:
        notes.append(f"Endpoint status is not success: {endpoint_status}")
        return "backend_endpoint_error", notes

    if _detect_rendering_symptom(ui_observed_behavior):
        notes.append("UI symptom suggests rendering or language/encoding issue.")
        return "frontend_state_or_rendering", notes

    if endpoint_top_drinks and ui_displayed_drinks and not overlap:
        notes.append("UI displayed drinks do not overlap with endpoint top drinks.")
        return "frontend_state_or_rendering", notes

    if endpoint_top_drinks and ui_displayed_drinks and overlap and not exact_match:
        notes.append("UI and endpoint overlap but order/content differs.")
        return "frontend_state_or_rendering_or_postprocessing", notes

    if _detect_memory_symptom(ui_observed_behavior):
        notes.append("UI symptom suggests missing conversation state or state update failure.")
        return "backend_intent_or_state", notes

    if _detect_constraint_symptom(ui_observed_behavior):
        notes.append("UI symptom suggests hard constraint was violated or not enforced.")
        return "backend_retrieval_or_ranking", notes

    if endpoint_intent in {"ask_clarifying_question", "refine_inquiry"} and endpoint_top_drinks:
        notes.append("Endpoint returned drinks despite clarify/refine intent.")
        return "backend_intent_or_state", notes

    if not endpoint_top_drinks:
        notes.append("Endpoint returned no top drinks; inspect retrieval/filtering/fallback logic.")
        return "backend_retrieval_or_ranking", notes

    if endpoint_composite_query is None:
        notes.append("Endpoint composite query missing; inspect preference summary / embedding query construction.")
        return "backend_intent_or_state", notes

    if exact_match:
        notes.append("UI displayed drinks match endpoint top drinks in order.")
        return "no_mismatch_detected", notes

    notes.append("No obvious mismatch detected, but endpoint/UI evidence is incomplete.")
    return "unknown", notes


def compare_ui_endpoint(
    test_case_id: str,
    user_prompt: str,
    ui_observed_behavior: str,
    endpoint_response: dict[str, Any],
    ui_displayed_drinks: list[str | dict[str, Any]] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Compare one UI test case with one endpoint response.

    Parameters
    ----------
    test_case_id:
        Unique test case ID, e.g. "UI-T03".
    user_prompt:
        Prompt shown in UI.
    ui_observed_behavior:
        Human-written UI observation.
    endpoint_response:
        Raw endpoint response JSON.
    ui_displayed_drinks:
        Drink IDs/names shown in UI, if available.
    notes:
        Optional manually provided notes.

    Returns
    -------
    dict
        Structured comparison record with suggested debug layer.
    """

    endpoint_intent = _extract_endpoint_intent(endpoint_response)
    endpoint_composite_query = _extract_composite_query(endpoint_response)
    endpoint_top_drinks = _extract_endpoint_top_drinks(endpoint_response)
    ui_drink_ids = _extract_drink_ids(ui_displayed_drinks)

    if endpoint_top_drinks and ui_drink_ids:
        if _sets_match_in_order(endpoint_top_drinks, ui_drink_ids):
            matched_or_not = "matched"
        elif _sets_overlap(endpoint_top_drinks, ui_drink_ids):
            matched_or_not = "partial_match"
        else:
            matched_or_not = "not_matched"
    elif endpoint_top_drinks and not ui_drink_ids:
        matched_or_not = "ui_drinks_not_logged"
    elif not endpoint_top_drinks and ui_drink_ids:
        matched_or_not = "endpoint_no_drinks_but_ui_has_drinks"
    else:
        matched_or_not = "insufficient_evidence"

    suspected_layer, inferred_notes = infer_suspected_layer(
        ui_observed_behavior=ui_observed_behavior,
        endpoint_top_drinks=endpoint_top_drinks,
        ui_displayed_drinks=ui_drink_ids,
        endpoint_intent=endpoint_intent,
        endpoint_composite_query=endpoint_composite_query,
        endpoint_response=endpoint_response,
    )

    combined_notes = []
    combined_notes.extend(notes or [])
    combined_notes.extend(inferred_notes)

    result = UIEndpointComparisonResult(
        test_case_id=test_case_id,
        user_prompt=user_prompt,
        ui_observed_behavior=ui_observed_behavior,
        endpoint_intent=endpoint_intent,
        endpoint_composite_query=endpoint_composite_query,
        endpoint_top_drinks=endpoint_top_drinks,
        ui_displayed_drinks=ui_drink_ids,
        matched_or_not=matched_or_not,
        suspected_layer=suspected_layer,
        notes=combined_notes,
    )

    return asdict(result)


def compare_many(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare many UI/endpoint records.

    Each record should contain:
        test_case_id
        user_prompt
        ui_observed_behavior
        endpoint_response
        ui_displayed_drinks
        notes
    """

    return [
        compare_ui_endpoint(
            test_case_id=record.get("test_case_id", ""),
            user_prompt=record.get("user_prompt", ""),
            ui_observed_behavior=record.get("ui_observed_behavior", ""),
            endpoint_response=record.get("endpoint_response", {}),
            ui_displayed_drinks=record.get("ui_displayed_drinks"),
            notes=record.get("notes"),
        )
        for record in records
    ]


def main() -> None:
    """CLI demo."""

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Compare UI observation with endpoint response.")
    parser.add_argument("--record", required=True, help="JSON record with UI and endpoint fields.")
    args = parser.parse_args()

    record = json.loads(args.record)
    result = compare_ui_endpoint(
        test_case_id=record.get("test_case_id", ""),
        user_prompt=record.get("user_prompt", ""),
        ui_observed_behavior=record.get("ui_observed_behavior", ""),
        endpoint_response=record.get("endpoint_response", {}),
        ui_displayed_drinks=record.get("ui_displayed_drinks"),
        notes=record.get("notes"),
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
