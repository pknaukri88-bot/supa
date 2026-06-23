import streamlit as st
import pandas as pd

from db import init_db, get_counts, get_all_knowledge, get_memory, get_graph_edges
from research import run_research
from rag import answer_from_knowledge
from upload import process_txt_upload

st.set_page_config(page_title="EvolvIQ", layout="wide")

st.title("EvolvIQ — AI-Native Intelligence Workspace")
st.caption("Research Mode + Knowledge-Augmented Chat + Memory + Knowledge Graph + Supabase PostgreSQL")

try:
    init_db()
except Exception as e:
    st.error("Database connection failed. Check your Supabase DATABASE_URL in Streamlit Secrets.")
    st.exception(e)
    st.stop()

mode = st.sidebar.radio(
    "Choose workflow",
    [
        "Research Mode",
        "Knowledge Chat",
        "Upload Knowledge",
        "Knowledge Graph",
        "Memory",
        "Knowledge Base",
        "Admin",
    ],
)

counts = get_counts()
st.sidebar.markdown("### Database")
st.sidebar.write(f"Knowledge: {counts['knowledge']}")
st.sidebar.write(f"Memory: {counts['memory']}")
st.sidebar.write(f"Graph edges: {counts['graph_edges']}")
st.sidebar.write(f"Documents: {counts['documents']}")

if mode == "Research Mode":
    st.header("Autonomous Research Mode")
    topic = st.text_input("Enter topic", "Behavioral Economics")
    max_sources = st.slider("Max sources", 1, 5, 3)

    if st.button("Start Research", type="primary"):
        result = run_research(topic, max_sources)
        st.success("Research complete and saved to Supabase PostgreSQL")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sources gathered", result["sources_gathered"])
        c2.metric("Knowledge created", result["knowledge_created"])
        c3.metric("Graph edges", result["graph_edges_created"])
        st.subheader("Synthesis")
        st.json(result)

elif mode == "Knowledge Chat":
    st.header("Knowledge-Augmented Chat")
    question = st.text_input("Ask a question", "What do we know about Behavioral Economics?")

    if st.button("Ask", type="primary"):
        result = answer_from_knowledge(question)
        st.subheader("Answer based on stored knowledge")
        st.markdown(result["answer"])
        st.subheader("Evidence trace")
        for item in result["evidence"][:6]:
            st.write(f"- {item}")
        st.subheader("Confidence")
        st.write(result["confidence"])

elif mode == "Upload Knowledge":
    st.header("Upload Knowledge")
    uploaded_file = st.file_uploader("Upload a TXT file", type=["txt"])

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        result = process_txt_upload(uploaded_file.name, text)
        st.success("Upload processed and knowledge saved to Supabase PostgreSQL")
        st.json(result)

elif mode == "Knowledge Graph":
    st.header("Knowledge Graph Summary")
    edges = get_graph_edges()
    nodes = set()
    for edge in edges:
        nodes.add(edge["source"])
        nodes.add(edge["target"])

    c1, c2 = st.columns(2)
    c1.metric("Nodes", len(nodes))
    c2.metric("Edges", len(edges))

    if edges:
        df = pd.DataFrame(edges)
        st.dataframe(df[["source", "relation", "target", "created_at"]], use_container_width=True)
    else:
        st.info("No graph relationships yet. Run Research Mode first.")

elif mode == "Memory":
    st.header("Memory")
    memory = get_memory()
    if memory:
        st.dataframe(pd.DataFrame(memory), use_container_width=True)
    else:
        st.info("No memory yet. Run Research Mode first.")

elif mode == "Knowledge Base":
    st.header("Knowledge Base")
    query = st.text_input("Search knowledge", "")
    rows = get_all_knowledge() if not query else __import__("db").search_knowledge(query, limit=500)

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "evolviq_knowledge.csv", "text/csv")
    else:
        st.info("No knowledge yet. Run Research Mode first.")

elif mode == "Admin":
    st.header("Admin")
    st.write("Database tables are initialized automatically on app startup.")
    st.json(counts)
    st.warning("Do not put DATABASE_URL directly in GitHub. Use Streamlit Secrets.")
