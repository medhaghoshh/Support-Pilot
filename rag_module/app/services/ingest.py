"""
SupportPilot AI

Knowledge Base Ingestion Service

Builds the ChromaDB vector database from the
Knowledge Base articles.

Responsibilities
----------------
1. Chunk Knowledge Base articles
2. Generate metadata
3. Store chunks in ChromaDB
4. Populate the SQL Knowledge Base table
"""

from __future__ import annotations

import sqlite3

import chromadb

from app.services.kb_articles import get_articles


# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

CHUNK_MIN_WORDS = 500

SQLITE_DB_PATH = "knowledge_base.db"

CHROMA_PATH = "./database/chromadb"

COLLECTION_NAME = "knowledge_base"


# ---------------------------------------------------
# Chunking
# ---------------------------------------------------

def chunk_article(article: dict) -> list[dict]:
    """
    Split large articles into logical sections.

    Smaller articles remain a single chunk.
    """

    content = article["content"]

    if len(content.split()) < CHUNK_MIN_WORDS:

        return [
            {
                "chunk_id": f"{article['kb_id']}-C1",
                "text": content.strip(),
                "section": "full_article",
            }
        ]

    sections = [
        "Overview",
        "Symptoms",
        "Troubleshooting Steps",
        "Resolution",
    ]

    chunks = []

    for index, section in enumerate(sections):

        if section not in content:
            continue

        start = content.index(section)

        next_section = (
            sections[index + 1]
            if index + 1 < len(sections)
            else None
        )

        end = (
            content.index(next_section)
            if (
                next_section
                and next_section in content
            )
            else len(content)
        )

        chunks.append(
            {
                "chunk_id": f"{article['kb_id']}-C{index+1}",
                "text": content[start:end].strip(),
                "section": section,
            }
        )

    return chunks


# ---------------------------------------------------
# Metadata
# ---------------------------------------------------

def build_metadata(
    article: dict,
    chunk: dict,
) -> dict:
    """
    Build metadata stored alongside every
    ChromaDB document.
    """

    return {
        "kb_id": article["kb_id"],
        "title": article["title"],
        "category": article["category"],
        "tags": ", ".join(article["tags"]),
        "last_updated": article["last_updated"],
        "source": article["kb_id"],
        "section": chunk["section"],
        "chunk_id": chunk["chunk_id"],
        "priority": article.get("priority", ""),
        "version": article.get("version", ""),
        "author": article.get("author", ""),
    }


# ---------------------------------------------------
# SQL Database
# ---------------------------------------------------

def create_sql_table():
    """
    Create the local Knowledge Base table.

    This mirrors the vector database and
    links each article to its primary chunk.
    """

    connection = sqlite3.connect(
        SQLITE_DB_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        "DROP TABLE IF EXISTS Knowledge_Base"
    )

    cursor.execute(
        """
        CREATE TABLE Knowledge_Base
        (
            article_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            embedding_id TEXT NOT NULL
        )
        """
    )

    connection.commit()

    return connection


# ---------------------------------------------------
# Ingestion
# ---------------------------------------------------

def ingest():
    """
    Build the ChromaDB Knowledge Base.
    """

    print("\nBuilding Knowledge Base...")

    # -----------------------------------------
    # ChromaDB
    # -----------------------------------------

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description":
            "SupportPilot Enterprise IT Knowledge Base"
        },
    )

    # -----------------------------------------
    # SQLite
    # -----------------------------------------

    connection = create_sql_table()

    cursor = connection.cursor()

    articles = get_articles()

    ids = []
    documents = []
    metadatas = []

    # -----------------------------------------
    # Process Articles
    # -----------------------------------------

    for article in articles:

        chunks = chunk_article(article)

        primary_embedding_id = (
            chunks[0]["chunk_id"]
        )

        for chunk in chunks:

            ids.append(chunk["chunk_id"])

            documents.append(
                chunk["text"]
            )

            metadatas.append(
                build_metadata(
                    article,
                    chunk,
                )
            )

        cursor.execute(
            """
            INSERT INTO Knowledge_Base
            (
                article_id,
                title,
                content,
                category,
                embedding_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                article["kb_id"],
                article["title"],
                article["content"],
                article["category"],
                primary_embedding_id,
            ),
        )

    # -----------------------------------------
    # Store in ChromaDB
    # -----------------------------------------

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    connection.commit()
    connection.close()

    print("\nKnowledge Base created successfully.")
    print(f"Articles : {len(articles)}")
    print(f"Chunks   : {len(ids)}")
    print(f"Collection : {COLLECTION_NAME}")
    print(f"ChromaDB : {CHROMA_PATH}")
    print(f"SQLite   : {SQLITE_DB_PATH}")


# ---------------------------------------------------
# Entry Point
# ---------------------------------------------------

if __name__ == "__main__":
    ingest()