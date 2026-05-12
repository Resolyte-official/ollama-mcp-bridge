import requests
import psycopg2

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="school-db",
    user="mcpserver",
    password="open-db",
    port=5432
)
cur = conn.cursor()

cur.execute("""
SELECT id, retrieval_text
FROM procedural_memory
""")
rows = cur.fetchall()

def get_ollama_embedding(text):
    url = "http://localhost:11434/api/embed"
    payload = {
        "model": "embeddinggemma",
        "input": text,
        "dimensions": 768,
        "options": {
            "temperature": 0.0,
            "seed": 1024
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    data = response.json()
    return data['embeddings'][0]

for memory_id, retrieval_text in rows:
    embedding = get_ollama_embedding(retrieval_text)
    cur.execute("""
    UPDATE procedural_memory
    SET embedding = %s
    WHERE id = %s
    """, (embedding, memory_id))

conn.commit()
cur.close()
conn.close()

print("Embeddings updated")