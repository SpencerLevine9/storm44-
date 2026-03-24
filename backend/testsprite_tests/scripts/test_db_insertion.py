import asyncio
import io
import json
import os
import uuid
import numpy as np
import asyncpg
from pgvector.asyncpg import register_vector

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/storm44")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../machine_learning/data"))

async def main():
    print(f"Connecting to {DATABASE_URL}")
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Enable vector extension support in asyncpg
    await register_vector(conn)
    
    # Initialize schema
    with open(os.path.join(os.path.dirname(__file__), "../../app/db/schema.sql"), "r") as f:
        schema_sql = f.read()
    await conn.execute(schema_sql)
    print("Schema initialized.")
    
    # We need a user to satisfy the foreign key constraint
    user_id = str(uuid.uuid4())
    print(f"Creating test user {user_id}")
    await conn.execute(
        "INSERT INTO user_account (id, username, password_hash) VALUES ($1, $2, $3) ON CONFLICT (username) DO NOTHING",
        user_id, "testuser", "hashtest"
    )
    # Always fetch the actual id in case the user already existed
    user_id = await conn.fetchval("SELECT id FROM user_account WHERE username = 'testuser'")
    user_id = str(user_id)
    print(f"Using user_id {user_id}")

    # Read data_resources.json to know what to process
    data_resources_path = os.path.join(DATA_DIR, "data_resources.json")
    if not os.path.exists(data_resources_path):
        print(f"Could not find {data_resources_path}")
        return
        
    print("Loading data_resources.json")
    with open(data_resources_path, "r") as f:
        data_resources = json.load(f)
        
    print("Loading embeddings.npy")
    embeddings_path = os.path.join(DATA_DIR, "embeddings", "embeddings.npy")
    embeddings = np.load(embeddings_path)
    
    print("Loading chunks_index.jsonl")
    index_path = os.path.join(DATA_DIR, "embeddings", "chunks_index.jsonl")
    chunks_index = []
    with open(index_path, "r") as f:
        for line in f:
            if line.strip():
                chunks_index.append(json.loads(line))
                
    # Create mapping from (filename, chunk_id) to embedding vector
    print("Mapping embeddings...")
    embedding_map = {}
    for idx, entry in enumerate(chunks_index):
        # entry has source_file and chunk_id
        src = entry["source_file"]
        c_id = entry["chunk_id"]
        # embeddings is a numpy array of shape (N, 384)
        embedding_map[(src, c_id)] = embeddings[idx]

    sources_inserted = 0
    chunks_inserted = 0
    
    # Process each PDF source
    for pdf_info in data_resources.get("pdf", []):
        filename = os.path.basename(pdf_info["file"])
        # Expecting chunks file like Intro_CS_ch1_chunks.json
        # filename is Intro_CS_ch1.pdf, base name is Intro_CS_ch1
        base_name = filename.replace(".pdf", "")
        chunks_file = os.path.join(DATA_DIR, "chunks", f"{base_name}_chunks.json")
        
        if not os.path.exists(chunks_file):
            print(f"File {chunks_file} does not exist, skipping.")
            continue
            
        print(f"Processing {base_name}...")
        
        # Create a source
        source_id = str(uuid.uuid4())
        await conn.execute(
            """
            INSERT INTO source (id, user_id, title, source_type, source_path, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            source_id, user_id, pdf_info["title"], "pdf", pdf_info["file"], "ready"
        )
        sources_inserted += 1
        
        # Load chunks
        with open(chunks_file, "r") as f:
            chunks_data = json.load(f)
            
        for chunk in chunks_data:
            chunk_db_id = str(uuid.uuid4())
            c_id = chunk["chunk_id"]
            
            # Insert chunk
            await conn.execute(
                """
                INSERT INTO chunk (id, source_id, chunk_index, start_page, end_page, approx_words, text)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                chunk_db_id, source_id, c_id, chunk.get("start_page"), chunk.get("end_page"), chunk.get("approx_words"), chunk["text"]
            )
            chunks_inserted += 1
            
            # Insert embedding
            vec = embedding_map.get((filename, c_id))
            if vec is not None:
                # Need to convert numpy array to list for asyncpg vector adapter
                vec_list = vec.tolist()
                await conn.execute(
                    """
                    INSERT INTO embedding (chunk_id, embedding, embedding_model)
                    VALUES ($1, $2, $3)
                    """,
                    chunk_db_id, vec_list, "MiniLM-L6-v2"
                )

    # Process each YouTube video source
    for video_info in data_resources.get("youtube", []):
        title = video_info["title"]
        url = video_info["url"]
        # Derive video_id from URL query param
        from urllib.parse import urlparse, parse_qs
        video_id = parse_qs(urlparse(url).query).get("v", [None])[0]

        # Derive chunks filename: "Video 1" -> "Video_1_chunks.json"
        chunks_filename = title.replace(" ", "_") + "_chunks.json"
        chunks_file = os.path.join(DATA_DIR, "chunks", chunks_filename)

        if not os.path.exists(chunks_file):
            print(f"File {chunks_file} does not exist, skipping.")
            continue

        print(f"Processing {title}...")

        source_id = str(uuid.uuid4())
        await conn.execute(
            """
            INSERT INTO source (id, user_id, title, source_type, video_id, video_url, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            source_id, user_id, title, "youtube", video_id, url, "ready"
        )
        sources_inserted += 1

        with open(chunks_file, "r") as f:
            chunks_data = json.load(f)

        for chunk in chunks_data:
            chunk_db_id = str(uuid.uuid4())
            c_id = chunk["chunk_id"]  # string e.g. "Video_1_chunk_000"

            await conn.execute(
                """
                INSERT INTO chunk (id, source_id, chunk_index, start_time, end_time, text)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                chunk_db_id, source_id, chunk["segment_start_idx"],
                chunk.get("start_time"), chunk.get("end_time"), chunk["text"]
            )
            chunks_inserted += 1

            vec = embedding_map.get((None, c_id))
            if vec is not None:
                vec_list = vec.tolist()
                await conn.execute(
                    """
                    INSERT INTO embedding (chunk_id, embedding, embedding_model)
                    VALUES ($1, $2, $3)
                    """,
                    chunk_db_id, vec_list, "MiniLM-L6-v2"
                )

    print(f"Successfully processed and inserted {sources_inserted} sources and {chunks_inserted} chunks with embeddings.")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
