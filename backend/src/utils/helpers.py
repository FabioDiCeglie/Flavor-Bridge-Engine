"""Shared helpers for ingredient formatting (embedding, metadata)."""


def format_ingredient_for_embedding(ingredient: dict, max_compounds: int = 20) -> str:
    """
    Build "name: compound1, compound2, ..." for embedding. Same format used
    in the Vectorize index and for search query embedding.
    """
    name = ingredient.get("name", "")
    compounds = format_compounds(ingredient, max_compounds)
    return f"{name}: {compounds}" if compounds else name


def format_compounds(ingredient: dict, max_compounds: int = 20) -> str:
    """Comma-separated compounds string (e.g. for metadata)."""
    return ", ".join(ingredient.get("compounds", [])[:max_compounds])
