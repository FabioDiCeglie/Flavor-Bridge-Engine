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

    return f"""You are a friendly expert explaining why certain ingredients taste similar, in plain language anyone can understand.

A user searched for "{query}" and got these similar ingredients:

{matches_context}

Your job (keep it short — 2–3 sentences total):

1. First sentence: Explain what the shared taste IS in human words. If it's umami, say so and define it simply (e.g. "Umami is that savory, mouth-filling depth — the 'fifth taste' alongside sweet, salty, sour, and bitter."). If it's another shared quality (roasty, earthy, etc.), name it and describe it in one short phrase.

2. Next: In one short sentence, say why these ingredients together give that taste (same building blocks, fermentation, roasting, etc.). No jargon, or explain it in plain words.

3. Optional: One very short practical tip (e.g. "Try swapping X for Y.") only if it fits in the same breath.

Write like you're talking to a curious friend. No textbook tone. Be concise."""

