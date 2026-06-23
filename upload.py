from db import add_knowledge, add_memory, add_graph_edge, add_document


def process_txt_upload(filename: str, text: str, max_chunks: int = 10) -> dict:
    chunks = [x.strip() for x in text.split(".") if len(x.strip()) > 20]
    created = 0

    add_document(filename, text)

    for chunk in chunks[:max_chunks]:
        add_knowledge(
            item_type="uploaded_fact",
            text=chunk + ".",
            confidence="Medium",
            evidence=f"Uploaded file: {filename}",
            source="upload",
        )
        created += 1

    add_memory("incremental_update", f"Uploaded file {filename} added {created} new knowledge items.")
    add_graph_edge("Uploaded Knowledge", "UPDATES", "Knowledge Base")

    return {
        "filename": filename,
        "knowledge_items": created,
        "evolution": "New information was added incrementally.",
        "contradictions": "Potential contradictions would be flagged for review.",
    }
