from db import add_many_knowledge, add_memory, add_many_graph_edges


def run_research(topic: str, max_sources: int = 3) -> dict:
    """Placeholder research pipeline. Replace this with real web/API research later."""
    knowledge_items = [
        {
            "type": "fact",
            "text": f"{topic} studies how psychological, social, and cognitive factors influence decision-making.",
            "confidence": "High",
            "evidence": f"Autonomous research synthesis for topic: {topic}",
            "source": "research_mode",
        },
        {
            "type": "fact",
            "text": "Daniel Kahneman and Amos Tversky are strongly associated with behavioral economics.",
            "confidence": "High",
            "evidence": "Stored knowledge from research mode.",
            "source": "research_mode",
        },
        {
            "type": "fact",
            "text": "Prospect Theory explains how people make decisions under risk and uncertainty.",
            "confidence": "High",
            "evidence": "Extracted research knowledge.",
            "source": "research_mode",
        },
        {
            "type": "fact",
            "text": "Loss aversion suggests people feel losses more strongly than equivalent gains.",
            "confidence": "High",
            "evidence": "Extracted research knowledge.",
            "source": "research_mode",
        },
        {
            "type": "insight",
            "text": "Behavioral economics connects psychology, economics, policy design, finance, and product decision-making.",
            "confidence": "Medium",
            "evidence": "Synthesized from accumulated knowledge.",
            "source": "research_mode",
        },
        {
            "type": "insight",
            "text": "Default choices, framing, and incentives can influence human behavior.",
            "confidence": "Medium",
            "evidence": "Synthesized from stored facts.",
            "source": "research_mode",
        },
    ]

    edges = [
        (topic, "MENTIONS", "Daniel Kahneman"),
        (topic, "MENTIONS", "Amos Tversky"),
        (topic, "HAS_CONCEPT", "Prospect Theory"),
        ("Prospect Theory", "INCLUDES", "Loss Aversion"),
        ("Default Effect", "INFLUENCES", "User Choice"),
        ("Behavioral Economics", "APPLIED_TO", "Policy Design"),
        ("Behavioral Economics", "APPLIED_TO", "Product Design"),
    ]

    created = add_many_knowledge(knowledge_items)
    add_many_graph_edges(edges)
    add_memory("stable_topic_summary", f"The workspace has accumulated structured knowledge about {topic}.")

    return {
        "summary": f"Research on {topic} produced structured knowledge, graph relationships, and memory records.",
        "sources_gathered": max_sources,
        "knowledge_created": created,
        "graph_edges_created": len(edges),
        "key_points": [
            f"{topic} studies decision-making behavior.",
            "Prospect Theory and loss aversion are central concepts.",
            "The knowledge graph was updated with entities and relationships.",
            "Memory was updated for future interactions.",
        ],
        "confidence": "Medium to High",
        "evolution": "No major contradiction detected in this run.",
    }
