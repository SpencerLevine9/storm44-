# Each row in Postgres represents one chunk:
# {
#   "chunk_id": int,
#   "source_file": str,
#   "start_page": int,
#   "end_page": int,
#   "text": str,
#   "embedding": List[float]  # dim = 384 (or 1536 if OpenAI)
# }

def insert_chunks(chunks, embeddings):
    """
    chunks: List[dict]
    embeddings: np.ndarray
    """
    pass
