import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any

import psycopg2
import psycopg2.extras
import streamlit as st


def get_database_url() -> str:
    """Read the Supabase Postgres connection string from Streamlit secrets or env."""
    url = None
    try:
        url = st.secrets.get("DATABASE_URL")
    except Exception:
        url = None
    url = url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is missing. Add it in Streamlit Secrets or .streamlit/secrets.toml."
        )
    return url


@contextmanager
def get_conn():
    conn = psycopg2.connect(get_database_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create EvolvIQ tables in Supabase Postgres if they do not exist."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge (
                    id BIGSERIAL PRIMARY KEY,
                    item_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    confidence TEXT DEFAULT 'Medium',
                    evidence TEXT,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    id BIGSERIAL PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_edges (
                    id BIGSERIAL PRIMARY KEY,
                    source TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    target TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id BIGSERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_text ON knowledge USING gin(to_tsvector('english', text));")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_source ON graph_edges(source);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_graph_target ON graph_edges(target);")


def add_knowledge(item_type: str, text: str, confidence: str = "Medium", evidence: str = "", source: str = "manual") -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO knowledge (item_type, text, confidence, evidence, source)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (item_type, text, confidence, evidence, source),
            )


def add_many_knowledge(items: List[Dict[str, Any]]) -> int:
    if not items:
        return 0
    rows = [
        (
            item.get("type", item.get("item_type", "fact")),
            item.get("text", ""),
            item.get("confidence", "Medium"),
            item.get("evidence", ""),
            item.get("source", "research"),
        )
        for item in items
        if item.get("text")
    ]
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(
                cur,
                """
                INSERT INTO knowledge (item_type, text, confidence, evidence, source)
                VALUES (%s, %s, %s, %s, %s)
                """,
                rows,
            )
    return len(rows)


def search_knowledge(query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if query.strip():
                cur.execute(
                    """
                    SELECT * FROM knowledge
                    WHERE text ILIKE %s OR evidence ILIKE %s OR source ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (f"%{query}%", f"%{query}%", f"%{query}%", limit),
                )
            else:
                cur.execute("SELECT * FROM knowledge ORDER BY created_at DESC LIMIT %s", (limit,))
            return [dict(row) for row in cur.fetchall()]


def get_all_knowledge(limit: int = 500) -> List[Dict[str, Any]]:
    return search_knowledge("", limit)


def add_memory(memory_type: str, text: str, status: str = "active") -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memory (memory_type, text, status, updated_at)
                VALUES (%s, %s, %s, %s)
                """,
                (memory_type, text, status, datetime.utcnow()),
            )


def get_memory(limit: int = 500) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM memory ORDER BY updated_at DESC LIMIT %s", (limit,))
            return [dict(row) for row in cur.fetchall()]


def add_graph_edge(source: str, relation: str, target: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO graph_edges (source, relation, target) VALUES (%s, %s, %s)",
                (source, relation, target),
            )


def add_many_graph_edges(edges: List[tuple]) -> int:
    if not edges:
        return 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(
                cur,
                "INSERT INTO graph_edges (source, relation, target) VALUES (%s, %s, %s)",
                edges,
            )
    return len(edges)


def get_graph_edges(limit: int = 1000) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM graph_edges ORDER BY created_at DESC LIMIT %s", (limit,))
            return [dict(row) for row in cur.fetchall()]


def add_document(filename: str, content: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (filename, content) VALUES (%s, %s)",
                (filename, content),
            )


def get_counts() -> Dict[str, int]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            counts = {}
            for table in ["knowledge", "memory", "graph_edges", "documents"]:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cur.fetchone()[0]
            return counts
