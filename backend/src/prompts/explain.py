"""
Prompt templates for the explain endpoint.

Keeping prompts separate makes them easier to iterate and test.
"""


def build_explain_prompt(query: str, matches: list[dict]) -> str:
    """
    Build the prompt for explaining flavor connections.

    Args:
        query: The ingredient being searched
        matches: List of similar ingredients with name, description, and optionally compounds

    Returns:
        Formatted prompt string for the LLM
    """
    matches_context = "\n".join(
        f"- {m['name']}: {m['description']}"
        + (f" Compounds: {m['compounds']}" if m.get("compounds") else "")
        for m in matches[:3]
    )

    return f"""You are a culinary scientist explaining flavor connections between ingredients.

A user searched for "{query}" and found these similar ingredients (ranked by chemical similarity):

{matches_context}

Explain WHY these ingredients are "chemical cousins" to {query}. Focus on:
1. Shared flavor compounds (glutamates, fermentation byproducts, etc.)
2. The science behind the similarity (amino acids, Maillard reaction, etc.)
3. A practical cooking tip for substitution

Keep it concise (2-3 sentences max) and accessible to home cooks."""

