curl http://localhost:11434/api/embed -d '{
  "model": "embeddinggemma",
  "input": "Why is the sky blue?",
  "dimensions": 768,
  "options": {
    "seed": 1024,
    "temperature": 0.0
  }
}'