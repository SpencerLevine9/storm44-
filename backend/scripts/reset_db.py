"""
Wipe all user data from the database to test a clean empty state.

Truncates: embedding → chunk → video_segment → source
Preserves: user_account rows and the schema itself.

Run from the repo root:
    python backend/scripts/reset_db.py

Pass --yes to skip the confirmation prompt (useful in CI / scripts).
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / "backend" / ".env"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset the Storm44 database to an empty state")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    load_env(ENV_FILE)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        sys.exit("ERROR: DATABASE_URL is not set. Check backend/.env or your environment.")

    if not args.yes:
        print("This will DELETE all rows from:")
        print("  embedding, chunk, video_segment, source")
        print("user_account rows are preserved.")
        print(f"\nTarget: {database_url[:40]}...")
        answer = input("\nType 'yes' to continue: ").strip().lower()
        if answer != "yes":
            print("Aborted.")
            return

    try:
        import psycopg2
    except ImportError:
        sys.exit("ERROR: psycopg2 is required – pip install psycopg2-binary")

    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Delete in FK-safe order: leaf tables first
            tables = ["embedding", "chunk", "video_segment", "source"]
            for table in tables:
                cur.execute(f"DELETE FROM {table}")
                print(f"  Cleared {table}: {cur.rowcount} rows deleted")

        conn.commit()
        print("\nDatabase reset complete. Ready for a fresh manual upload.")
    except Exception as exc:
        conn.rollback()
        sys.exit(f"ERROR: {exc}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
