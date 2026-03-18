# pipeline.py responsibilities
# Run ingestion steps in order
# Later: optionally run a test query

import subprocess

def run(step):
    subprocess.run(step, check=True)

if __name__ == "__main__":
    run(["python", "machine_learning/ingest_pipeline/extract_text/pdfs.py"])
    run(["python", "machine_learning/ingest_pipeline/process/chunk.py"])
    run(["python", "machine_learning/ingest_pipeline/process/yt_chunk.py"])
    run(["python", "machine_learning/ingest_pipeline/process/embed.py"])
    run(["python", "machine_learning/ingest_pipeline/store/postgres.py"])

    print("Ingestion pipeline complete.")