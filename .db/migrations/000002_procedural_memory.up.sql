
CREATE TABLE IF NOT EXISTS procedural_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent TEXT NOT NULL,
    canonical_query TEXT NOT NULL,
    retrieval_text TEXT NOT NULL,
    query_examples JSONB NOT NULL,
    instruction TEXT NOT NULL,
    tool_sequence JSONB NOT NULL,
    constraints JSONB,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT now()
);