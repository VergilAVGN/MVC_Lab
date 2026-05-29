from __future__ import annotations

import re
import requests
from urllib.parse import urljoin
from django.conf import settings

BASE_URL = settings.COCKTAILDB_API_URL.rstrip("/") + "/"
SEARCH_URL = urljoin(BASE_URL, "search.php")


def fetch_cocktail_by_name(name: str) -> dict | None:
    """Returns mapped dict for Recipe form or None if not found."""
    name = (name or "").strip()
    if not name:
        return None

    try:
        response = requests.get(SEARCH_URL, params={"s": name}, timeout=8)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    drinks = data.get("drinks")
    if not drinks:
        return None

    return map_drink_to_recipe(drinks[0])


def map_drink_to_recipe(drink: dict) -> dict:
    ingredients_lines: list[str] = []
    for i in range(1, 16):
        ing = (drink.get(f"strIngredient{i}") or "").strip()
        measure = (drink.get(f"strMeasure{i}") or "").strip()
        if not ing:
            continue
        line = f"- {measure} {ing}".strip() if measure else f"- {ing}"
        ingredients_lines.append(line)

    raw_instructions = (drink.get("strInstructions") or "").strip()
    instruction_lines = _split_instructions(raw_instructions)

    return {
        "name": (drink.get("strDrink") or "").strip()[:100],
        "ingredients": "\n".join(ingredients_lines) if ingredients_lines else "- (no ingredients listed)",
        "instructions": "\n".join(instruction_lines) if instruction_lines else "1. (no instructions listed)",
        "image_url": (drink.get("strDrinkThumb") or "").strip(),
    }


def _split_instructions(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        parts = [text]
    return [f"{i}. {part}" for i, part in enumerate(parts, start=1)]
