"""
candidate_retrieval.py

Mock candidate retrieval for the Boba Buddy Digital Waiter project.

This module demonstrates how a backend retrieval layer might work without
connecting to production Supabase.

Production design idea:
    Use a location-aware RPC such as `get_top_similar_drinks_by_radius`
    to retrieve drinks by embedding similarity and radius.

Portfolio mock:
    - uses in-memory mock drink data;
    - computes cosine similarity against toy embeddings;
    - filters by radius in meters;
    - returns JSON-like candidate dictionaries.

Important:
    Do not commit real Supabase URLs, credentials, API keys, or production data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any


@dataclass
class RetrievalDebug:
    """Debug metadata for retrieval."""

    rpc_used: str
    radius_meters: int
    lat: float
    lon: float
    limit: int
    candidate_count_before_location_filter: int
    candidate_count_after_location_filter: int
    candidate_count_returned: int
    notes: list[str]


MOCK_DRINKS: list[dict[str, Any]] = [
    {
        "drink_id": "demo-drink-001",
        "name_en": "Demo Green Tea",
        "name_zh": "示範綠茶",
        "store_id": "demo-store-a",
        "store_name": "Demo Store A",
        "lat": 25.0134,
        "lon": 121.5362,
        "price": 45,
        "embedding": [0.90, 0.10, 0.05, 0.10, 0.05],
        "metadata": {
            "drink_base": ["tea"],
            "contains_dairy": False,
            "contains_coffee": False,
            "caffeine_level": "medium",
            "sweetness_tendency": "low",
            "availability": True,
            "taste_tags": ["refreshing", "light", "tea_based"],
            "semantic_description": "Light green tea, refreshing and clean, no milk.",
        },
    },
    {
        "drink_id": "demo-drink-002",
        "name_en": "Demo Citrus Tea",
        "name_zh": "示範柑橘茶",
        "store_id": "demo-store-b",
        "store_name": "Demo Store B",
        "lat": 25.0150,
        "lon": 121.5370,
        "price": 55,
        "embedding": [0.85, 0.20, 0.20, 0.05, 0.10],
        "metadata": {
            "drink_base": ["fruit", "tea"],
            "contains_dairy": False,
            "contains_coffee": False,
            "caffeine_level": "medium",
            "sweetness_tendency": "medium",
            "availability": True,
            "taste_tags": ["refreshing", "citrus", "fruit_tea"],
            "semantic_description": "Bright citrus tea, refreshing and fruity, no milk.",
        },
    },
    {
        "drink_id": "demo-drink-003",
        "name_en": "Demo Light Milk Tea",
        "name_zh": "示範輕奶茶",
        "store_id": "demo-store-c",
        "store_name": "Demo Store C",
        "lat": 25.0190,
        "lon": 121.5420,
        "price": 65,
        "embedding": [0.30, 0.85, 0.10, 0.30, 0.20],
        "metadata": {
            "drink_base": ["milk", "tea"],
            "contains_dairy": True,
            "contains_coffee": False,
            "caffeine_level": "medium",
            "sweetness_tendency": "medium",
            "availability": True,
            "taste_tags": ["milky", "smooth", "not_too_heavy"],
            "semantic_description": "A lighter milk tea with smooth texture.",
        },
    },
    {
        "drink_id": "demo-drink-004",
        "name_en": "Demo Brown Sugar Milk",
        "name_zh": "示範黑糖鮮奶",
        "store_id": "demo-store-d",
        "store_name": "Demo Store D",
        "lat": 25.0300,
        "lon": 121.5600,
        "price": 80,
        "embedding": [0.10, 0.90, 0.05, 0.70, 0.40],
        "metadata": {
            "drink_base": ["milk"],
            "contains_dairy": True,
            "contains_coffee": False,
            "caffeine_level": "none",
            "sweetness_tendency": "high",
            "availability": True,
            "taste_tags": ["brown_sugar", "rich", "heavy", "sweet"],
            "semantic_description": "Rich brown sugar fresh milk, sweet and heavy.",
        },
    },
    {
        "drink_id": "demo-drink-005",
        "name_en": "Demo Black Tea",
        "name_zh": "示範紅茶",
        "store_id": "demo-store-a",
        "store_name": "Demo Store A",
        "lat": 25.0132,
        "lon": 121.5361,
        "price": 40,
        "embedding": [0.70, 0.10, 0.05, 0.20, 0.80],
        "metadata": {
            "drink_base": ["tea"],
            "contains_dairy": False,
            "contains_coffee": False,
            "caffeine_level": "high",
            "sweetness_tendency": "low",
            "availability": True,
            "taste_tags": ["tea_based", "energizing", "strong_tea"],
            "semantic_description": "Black tea with stronger tea flavor and energizing feel.",
        },
    },
    {
        "drink_id": "demo-drink-006",
        "name_en": "Demo Coffee Latte",
        "name_zh": "示範咖啡拿鐵",
        "store_id": "demo-store-e",
        "store_name": "Demo Store E",
        "lat": 25.0165,
        "lon": 121.5355,
        "price": 75,
        "embedding": [0.15, 0.70, 0.05, 0.50, 0.90],
        "metadata": {
            "drink_base": ["coffee", "milk"],
            "contains_dairy": True,
            "contains_coffee": True,
            "caffeine_level": "high",
            "sweetness_tendency": "medium",
            "availability": True,
            "taste_tags": ["coffee", "milky", "energizing"],
            "semantic_description": "Coffee latte, milky and energizing.",
        },
    },
]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity for two vectors."""

    if len(a) != len(b):
        raise ValueError(f"Vector dimensions do not match: {len(a)} vs {len(b)}")

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute approximate distance between two WGS84 coordinates."""

    radius_earth_m = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    h = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))
    return radius_earth_m * c


def _validate_radius_meters(radius_meters: int | float) -> int:
    """Validate radius and return integer meters.

    Endpoint notes highlight ambiguity between radius=1.5 and radius=1500.
    This mock function expects meters and flags suspicious tiny values by raising.
    """

    try:
        radius = int(radius_meters)
    except (TypeError, ValueError):
        raise ValueError("radius_meters must be numeric")

    if radius <= 0:
        raise ValueError("radius_meters must be positive")

    # Portfolio safety: warn users by failing fast if the value likely came from km.
    if radius < 10:
        raise ValueError(
            "radius_meters is suspiciously small. Use meters, e.g. 1500 instead of 1.5."
        )

    return radius


def retrieve_candidates_with_debug(
    query_embedding: list[float],
    lat: float,
    lon: float,
    radius_meters: int,
    limit: int = 10,
    mock_drinks: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Retrieve candidate drinks with debug metadata.

    Parameters
    ----------
    query_embedding:
        Embedding vector for accumulated preference summary.
    lat, lon:
        User location.
    radius_meters:
        Search radius in meters.
    limit:
        Number of candidates to return.
    mock_drinks:
        Optional list of mock drinks. If omitted, uses `MOCK_DRINKS`.

    Returns
    -------
    tuple[list[dict], dict]
        Candidates sorted by semantic similarity, plus debug metadata.
    """

    radius = _validate_radius_meters(radius_meters)
    drinks = mock_drinks or MOCK_DRINKS

    notes: list[str] = [
        "Portfolio mock retrieval; production should call get_top_similar_drinks_by_radius.",
        "Radius is interpreted as meters.",
    ]

    location_filtered: list[dict[str, Any]] = []

    for drink in drinks:
        distance = haversine_distance_meters(lat, lon, drink["lat"], drink["lon"])

        if distance <= radius:
            similarity = cosine_similarity(query_embedding, drink["embedding"])
            candidate = {
                "drink_id": drink["drink_id"],
                "name_en": drink["name_en"],
                "name_zh": drink["name_zh"],
                "store_id": drink["store_id"],
                "store_name": drink["store_name"],
                "price": drink["price"],
                "distance_meters": round(distance, 2),
                "semantic_similarity": round(similarity, 6),
                "metadata": drink["metadata"],
                "source": "mock_retrieval",
            }
            location_filtered.append(candidate)

    sorted_candidates = sorted(
        location_filtered,
        key=lambda item: item["semantic_similarity"],
        reverse=True,
    )[:limit]

    debug = RetrievalDebug(
        rpc_used="mock_get_top_similar_drinks_by_radius",
        radius_meters=radius,
        lat=float(lat),
        lon=float(lon),
        limit=int(limit),
        candidate_count_before_location_filter=len(drinks),
        candidate_count_after_location_filter=len(location_filtered),
        candidate_count_returned=len(sorted_candidates),
        notes=notes,
    )

    return sorted_candidates, asdict(debug)


def retrieve_candidates(
    query_embedding: list[float],
    lat: float,
    lon: float,
    radius_meters: int,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Mock retrieval function for portfolio use.

    Suggested interface from the project plan:

    def retrieve_candidates(
        query_embedding: list[float],
        lat: float,
        lon: float,
        radius_meters: int,
        limit: int = 10
    ) -> list[dict]:
        ...

    This function does not connect to Supabase. It simulates a radius-aware
    candidate retrieval stage and returns JSON-like candidate dictionaries.
    """

    candidates, _ = retrieve_candidates_with_debug(
        query_embedding=query_embedding,
        lat=lat,
        lon=lon,
        radius_meters=radius_meters,
        limit=limit,
    )
    return candidates


def main() -> None:
    """CLI demo.

    Example:
        python src/retrieval_and_ranking/candidate_retrieval.py \
          --embedding 0.9 0.1 0.05 0.1 0.05 \
          --lat 25.0131 --lon 121.5364 --radius-meters 1500
    """

    import argparse
    import json

    parser = argparse.ArgumentParser(description="Mock radius-aware candidate retrieval.")
    parser.add_argument("--embedding", nargs="+", type=float, required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--radius-meters", type=int, required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    candidates, debug = retrieve_candidates_with_debug(
        query_embedding=args.embedding,
        lat=args.lat,
        lon=args.lon,
        radius_meters=args.radius_meters,
        limit=args.limit,
    )

    print(json.dumps({"debug": debug, "candidates": candidates}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
