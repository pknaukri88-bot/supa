from db import search_knowledge


def answer_from_knowledge(question: str, limit: int = 6) -> dict:
    """Simple keyword retrieval. Embeddings can replace this later."""
    rows = search_knowledge(question, limit=limit)
    if not rows:
        rows = search_knowledge("", limit=limit)

    if not rows:
        return {
            "answer": "No stored knowledge found. Please run Research Mode or upload knowledge first.",
            "evidence": [],
            "confidence": "Low",
        }

    answer_lines = [row["text"] for row in rows]
    evidence = [row.get("evidence") or row.get("source") or "Stored knowledge" for row in rows]

    return {
        "answer": "\n".join(f"- {line}" for line in answer_lines),
        "evidence": evidence,
        "confidence": "Medium — based on retrieved stored knowledge.",
    }
