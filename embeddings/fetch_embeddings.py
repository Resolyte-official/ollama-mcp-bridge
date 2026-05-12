import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Config
SIMILARITY_THRESHOLD = 0.50
TOP_K = 5
OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "embeddinggemma"
DIMENSIONS = 768


conn = psycopg2.connect(
    host="localhost",
    database="school-db",
    user="mcpserver",
    password="open-db",
    port=5432
)

cur = conn.cursor(cursor_factory=RealDictCursor)
print("Connected to database.")


def get_ollama_embedding(text):
    payload = {
        "model": MODEL_NAME,
        "input": text,
        "dimensions": DIMENSIONS,
        "options": {
            "temperature": 0.0,
            "seed": 1024
        }
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    data = response.json()
    embedding = data['embeddings'][0]

    # sanity check: pad if necessary
    if len(embedding) < DIMENSIONS:
        embedding += [0.0] * (DIMENSIONS - len(embedding))
    elif len(embedding) > DIMENSIONS:
        embedding = embedding[:DIMENSIONS]

    return embedding

def search_procedural_memories(user_query):

    print(f"User Query: {user_query}")

    query_embedding = get_ollama_embedding(user_query)
    print("\nGenerated query embedding.")
    print(f"Embedding dimensions: {len(query_embedding)}")
    print(f"First 5 values: {query_embedding[:5]}")

    cur.execute("""
        SELECT
            id,
            intent,
            canonical_query,
            retrieval_text,
            instruction,
            tool_sequence,
            constraints,
            1 - (embedding <=> %s::vector) AS similarity
        FROM procedural_memory
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (
        str(query_embedding),
        str(query_embedding),
        TOP_K
    ))

    raw_results = cur.fetchall()

    if not raw_results:
        print("\nNo records found in procedural_memory.")
        return []

    print("\nRaw similarity scores:\n")
    for idx, row in enumerate(raw_results, start=1):
        print(
            f"{idx}. Intent={row['intent']} | Similarity={round(row['similarity'], 4)}"
        )

    results = [row for row in raw_results if row["similarity"] >= SIMILARITY_THRESHOLD]
    print(f"\nThreshold: {SIMILARITY_THRESHOLD}")

    if not results:
        print("\nNo similar procedural memories found above threshold.")
        print("\nSuggestions:")
        print("- Lower threshold")
        print("- Improve retrieval_text")
        print("- Add more example queries")
        return []

    print(f"\nFound {len(results)} matching memories:\n")
    for idx, row in enumerate(results, start=1):
        print("=" * 80)
        print(f"Match #{idx}")
        print("=" * 80)
        print(f"Intent: {row['intent']}")
        print(f"Canonical Query: {row['canonical_query']}")
        print(f"Similarity: {round(row['similarity'], 4)}")
        print("\nInstruction:")
        print(row["instruction"])
        print("\nTool Sequence:")
        print(json.dumps(row["tool_sequence"], indent=2))
        print("\nConstraints:")
        print(json.dumps(row["constraints"], indent=2))
        print("\nRetrieval Text:")
        print(row["retrieval_text"])
        print()

    return results

if __name__ == "__main__":
    print("\nProcedural Memory Search Ready.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Enter your query: ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        try:
            matches = search_procedural_memories(query)
        except Exception as e:
            print("\nERROR:")
            print(str(e))


cur.close()
conn.close()
print("\nDatabase connection closed.")