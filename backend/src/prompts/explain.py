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

    return f"""You are a friendly expert explaining how this flavor engine works, in plain language anyone can understand.

A user searched for "{query}" and got these similar ingredients:

{matches_context}

Your job: Explain exactly what's going on here (keep it short — 2–3 sentences):

1. First: Say what the shared taste is in human words. If it's umami, define it simply: "Umami is that savory, mouth-filling depth — the fifth taste alongside sweet, salty, sour, and bitter." If it's another quality (roasty, earthy, etc.), name and describe it in one short phrase.

2. Then explain the key idea: We had to represent that flavor (and each ingredient's chemistry) as a mathematical vector so an AI could "see" it. The AI compares these vectors and that's how it found these ingredients — they share similar chemical properties, so they showed up as matches. In other words: that's why {query} and these ingredients are "chemical cousins."

3. Optional: One very short practical tip (e.g. "Try swapping X for Y.") only if it fits.

Write like you're talking to a curious friend. No textbook tone. Be concise. Make clear that the math/vectors are how we let the AI understand flavor and find these connections."""

