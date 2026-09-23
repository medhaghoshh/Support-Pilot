"""
Milestone 2 - Knowledge Base Data Engineer (Member 4)
Full ingestion pipeline:
1. Chunk articles (300-word rule, split long ones by section)
2. Tag metadata (category, last_updated, tags, source, kb_id)
3. Generate embeddings and store in ChromaDB (vector store)
4. Populate the Knowledge_Base SQL table (article_id, title, content,
   category, embedding_id) - linking the relational DB to the vector store
"""

import sqlite3
import chromadb
from kb_articles import get_articles
from kb_reasoning import get_reasoning
from diagnosis_rules import SYMPTOM_RULES

CHUNK_MIN_WORDS = 500
DB_PATH = "knowledge_base.db"
CHROMA_PATH = "./chroma_db"


def _reasoning_for(kb_id):
    """Reasoning entry for an article, or an empty dict if none exists."""
    return get_reasoning(kb_id) or {}


def chunk_article(article):
    """Short articles = 1 chunk. Long articles = split by section."""
    content = article["content"]
    if len(content.split()) < CHUNK_MIN_WORDS:
        return [{
            "chunk_id": f"{article['kb_id']}-C1",
            "text": content.strip(),
            "section": "full_article",
        }]

    sections = ["Overview", "Symptoms", "Troubleshooting Steps", "Resolution"]
    chunks = []
    for i, section in enumerate(sections):
        if section not in content:
            continue
        start = content.index(section)
        nxt = sections[i + 1] if i + 1 < len(sections) else None
        end = content.index(nxt) if (nxt and nxt in content) else len(content)
        chunks.append({
            "chunk_id": f"{article['kb_id']}-C{i+1}",
            "text": content[start:end].strip(),
            "section": section,
        })
    return chunks


def build_metadata(article, chunk):
    return {
        "kb_id": article["kb_id"],
        "title": article["title"],
        "category": article["category"],
        "tags": ", ".join(article["tags"]),
        "last_updated": article["last_updated"],
        "source": article["kb_id"],
        "section": chunk["section"],
        "chunk_id": chunk["chunk_id"],
        # optional fields, included when available
        "priority": article.get("priority", ""),
        "version": article.get("version", ""),
        "author": article.get("author", ""),
        # Milestone 3: reasoning hooks carried into the vector store so the
        # Retrieval Agent can hand the Resolution/Escalation Agents what
        # they need without a second lookup
        "symptoms": "; ".join(_reasoning_for(article["kb_id"]).get("symptoms", [])),
        "escalate_to": _reasoning_for(article["kb_id"]).get("escalate_to", ""),
        "auto_resolvable": str(
            _reasoning_for(article["kb_id"]).get("auto_resolvable", False)
        ),
        "related_articles": ", ".join(
            _reasoning_for(article["kb_id"]).get("related_articles", [])
        ),
    }


def create_sql_table():
    """Creates the Knowledge_Base table per the required schema."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS Knowledge_Base")
    cur.execute("""
        CREATE TABLE Knowledge_Base (
            article_id   TEXT PRIMARY KEY,
            title        TEXT NOT NULL,
            content      TEXT NOT NULL,
            category     TEXT NOT NULL,
            embedding_id TEXT NOT NULL
        )
    """)

    # ---- Milestone 3 tables ----
    # The Knowledge_Base table above keeps exactly the five required
    # columns. Agent reasoning data lives in these separate tables so the
    # original schema stays unchanged for anyone already consuming it.

    cur.execute("DROP TABLE IF EXISTS KB_Symptoms")
    cur.execute("""
        CREATE TABLE KB_Symptoms (
            kb_id   TEXT NOT NULL,
            symptom TEXT NOT NULL
        )
    """)

    cur.execute("DROP TABLE IF EXISTS KB_Resolution_Steps")
    cur.execute("""
        CREATE TABLE KB_Resolution_Steps (
            kb_id            TEXT NOT NULL,
            step_number      INTEGER NOT NULL,
            action           TEXT NOT NULL,
            expected_outcome TEXT NOT NULL
        )
    """)

    cur.execute("DROP TABLE IF EXISTS KB_Reasoning")
    cur.execute("""
        CREATE TABLE KB_Reasoning (
            kb_id              TEXT PRIMARY KEY,
            prerequisites      TEXT,
            related_articles   TEXT,
            next_if_unresolved TEXT,
            escalate_to        TEXT,
            escalate_when      TEXT,
            auto_resolvable    INTEGER
        )
    """)

    cur.execute("DROP TABLE IF EXISTS Diagnosis_Rules")
    cur.execute("""
        CREATE TABLE Diagnosis_Rules (
            category  TEXT NOT NULL,
            indicator TEXT NOT NULL,
            weight    INTEGER NOT NULL
        )
    """)

    conn.commit()
    return conn


def populate_reasoning_tables(conn):
    """Fills the Milestone 3 tables from kb_reasoning.py and diagnosis_rules.py."""
    cur = conn.cursor()

    for kb_id, r in get_reasoning().items():
        for symptom in r["symptoms"]:
            cur.execute(
                "INSERT INTO KB_Symptoms (kb_id, symptom) VALUES (?, ?)",
                (kb_id, symptom),
            )

        for step in r["resolution_steps"]:
            cur.execute(
                """INSERT INTO KB_Resolution_Steps
                   (kb_id, step_number, action, expected_outcome)
                   VALUES (?, ?, ?, ?)""",
                (kb_id, step["step"], step["action"], step["expected"]),
            )

        cur.execute(
            """INSERT INTO KB_Reasoning
               (kb_id, prerequisites, related_articles, next_if_unresolved,
                escalate_to, escalate_when, auto_resolvable)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                kb_id,
                " | ".join(r["prerequisites"]),
                ", ".join(r["related_articles"]),
                r.get("next_if_unresolved"),
                r["escalate_to"],
                r["escalate_when"],
                1 if r["auto_resolvable"] else 0,
            ),
        )

    for category, weighted in SYMPTOM_RULES.items():
        for weight, indicators in weighted.items():
            for indicator in indicators:
                cur.execute(
                    """INSERT INTO Diagnosis_Rules (category, indicator, weight)
                       VALUES (?, ?, ?)""",
                    (category, indicator, weight),
                )

    conn.commit()


def ingest():
    # --- 1. Set up ChromaDB vector store ---
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # reset collection for a clean run
    try:
        client.delete_collection("knowledge_base")
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name="knowledge_base",
        metadata={"description": "IT support knowledge base"}
    )

    # --- 2. Set up SQL table ---
    conn = create_sql_table()
    cur = conn.cursor()

    articles = get_articles()
    ids, documents, metadatas = [], [], []

    for article in articles:
        chunks = chunk_article(article)
        # embedding_id links the SQL row to its vector chunk(s) in ChromaDB.
        # For single-chunk articles it's the chunk_id; for multi-chunk we
        # store the first chunk id as the primary reference.
        primary_embedding_id = chunks[0]["chunk_id"]

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            documents.append(chunk["text"])
            metadatas.append(build_metadata(article, chunk))

        # --- 3. Insert into the Knowledge_Base SQL table ---
        cur.execute("""
            INSERT INTO Knowledge_Base
            (article_id, title, content, category, embedding_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            article["kb_id"],
            article["title"],
            article["content"],
            article["category"],
            primary_embedding_id,
        ))

    # --- 4. Store embeddings in ChromaDB ---
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    conn.commit()

    # --- 5. Milestone 3: populate the agent reasoning tables ---
    populate_reasoning_tables(conn)

    cur.execute("SELECT COUNT(*) FROM KB_Symptoms")
    n_symptoms = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM KB_Resolution_Steps")
    n_steps = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Diagnosis_Rules")
    n_rules = cur.fetchone()[0]

    conn.close()

    print(f"Ingested {len(articles)} articles as {len(ids)} chunks.")
    print(f"- ChromaDB vector store: {CHROMA_PATH}")
    print(f"- Knowledge_Base SQL table: {DB_PATH}")
    print("Milestone 3 reasoning data:")
    print(f"- KB_Symptoms:          {n_symptoms} rows")
    print(f"- KB_Resolution_Steps:  {n_steps} rows")
    print(f"- KB_Reasoning:         {len(get_reasoning())} rows")
    print(f"- Diagnosis_Rules:      {n_rules} rows")


if __name__ == "__main__":
    ingest()
