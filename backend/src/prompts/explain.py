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

    return f"""You are a friendly expert. Explain in plain language, 2–3 short sentences. No repetition.

A user searched for "{query}" and got these similar ingredients (they're good to use together on the same plate or as substitutes):

{matches_context}

Structure your answer exactly like this:

1. One sentence — what's the shared flavor? If it's umami, say: "Umami is that savory, mouth-filling depth (the fifth taste)." If it's something else (pungent, roasty, earthy), name it in a few words.

2. One sentence — the key idea: "We had to represent that flavor as a mathematical vector so an AI could understand which ingredients share similar chemical properties — like miso and parmesan for umami. That's why {query} and these show up together: they're chemical cousins." Use this idea; you can shorten or rephrase slightly but keep "represent as a vector" and "chemical cousins" and "similar chemical properties."

3. Optional: One very short tip (e.g. "Try swapping X for Y") only if it fits in one phrase.

Do not add extra sentences about "maps," "the AI compares," or "that's why they show up." Stick to: shared flavor → vectors so the AI understands chemical similarity → these are chemical cousins, good on the same plate."""

