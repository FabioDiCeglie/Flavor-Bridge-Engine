"""
IngredientService - Lookup and text helpers for ingredients.

Responsibilities:
- Find ingredient by name (case-insensitive)
- Check if an ingredient exists
- Build query text for embedding (name + compounds, same format as Vectorize index)
"""

from data import INGREDIENTS
from utils.helpers import format_ingredient_for_embedding


class IngredientService:
    """Service for ingredient lookup and embedding-text building."""

    def __init__(self):
        """No bindings required; uses in-memory INGREDIENTS."""
        pass

    def find_by_name(self, name: str) -> dict | None:
        """
        Return the ingredient dict if a known ingredient matches the name.
        Matches: exact (case-insensitive); no-spaces (Parmesancheese → Parmesan cheese);
        ingredient name starts with query (Parmesan → Parmesan cheese);
        or query starts with ingredient name (Parmesan cheese aged → Parmesan cheese).
        """
        name_lower = (name or "").strip().lower()
        name_no_spaces = "".join(name_lower.split())
        for ing in INGREDIENTS:
            ing_name = ing["name"].strip().lower()
            if ing_name == name_lower:
                return ing
            if name_no_spaces and "".join(ing_name.split()) == name_no_spaces:
                return ing
            if name_lower and ing_name.startswith(name_lower):
                return ing
            if ing_name and name_lower.startswith(ing_name):
                return ing
        return None

    def exists(self, name: str) -> bool:
        """Return True if a known ingredient matches the name (case-insensitive)."""
        return self.find_by_name(name) is not None

    def get_query_text_for_embedding(self, query: str) -> str:
        """
        Build the text to embed for a search query (name + compounds, same format
        as the Vectorize index). If the query matches a known ingredient, returns
        that; otherwise returns the raw query.
        """
        ing = self.find_by_name(query)
        return format_ingredient_for_embedding(ing)
