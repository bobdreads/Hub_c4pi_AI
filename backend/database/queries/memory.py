import json
import uuid


async def insert_semantic_memory(pool, user_id: str, chat_id: str, content: str, embedding: list[float], metadata: dict = None):
    """Insere uma nova memória no banco de dados com seu vetor e gera um ID único."""
    memory_id = str(uuid.uuid4())

    await pool.execute(
        """
        INSERT INTO memory (id, user_id, chat_id, content, metadata, embedding)
        VALUES ($1::uuid, $2::uuid, $3::uuid, $4, $5::jsonb, $6::vector)
        """,
        memory_id, user_id, chat_id, content, json.dumps(
            metadata or {}), str(embedding)
    )


async def search_semantic_memory(pool, user_id: str, query_embedding: list[float], limit: int = 3, threshold: float = 0.1):
    """
    Busca memórias semânticas usando pgvector (distância de cosseno).
    A similaridade é calculada como 1 - distância.
    """
    return await pool.fetch(
        """
        SELECT id, chat_id, content, metadata, created_at,
               1 - (embedding <=> $2::vector) AS similarity
        FROM memory
        WHERE user_id = $1::uuid
          AND 1 - (embedding <=> $2::vector) >= $3
        ORDER BY embedding <=> $2::vector ASC
        LIMIT $4
        """,
        user_id, str(query_embedding), threshold, limit
    )
