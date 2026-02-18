from __future__ import annotations  # for Python 3.10+ type hinting (e.g. List[Page] inside Page class)

import json    # for outputting chunk metadata as JSON
import re # for simple word splitting and page parsing
from dataclasses import dataclass   # for simple Page class
from pathlib import Path    # for file handling
from typing import List, Dict, Any, Tuple   # for type annotations


# Config (tune later if needed)

CHUNK_WORDS = 350          # 500-ish tokens depending on text
OVERLAP_WORDS = 60         # overlap to preserve context
MIN_CHUNK_WORDS = 80       # skip tiny chunks unless it's the only content

TEXT_DIR = Path("machine_learning/artifacts/text")
OUT_DIR = Path("machine_learning/artifacts/chunks")


PAGE_RE = re.compile(r"^=+\s*PAGE\s+(\d+)\s*=+\s*$", re.IGNORECASE)     # matches lines like "===== PAGE 1 ====="


@dataclass  # simple class to hold page number and text
class Page:
    page_num: int
    text: str

def read_text_file(path: Path) -> str:  # read text file content, ignoring encoding errors to avoid issues with weird characters
    return path.read_text(encoding="utf-8", errors="ignore")    


def split_into_pages(raw: str) -> List[Page]:   # split raw text into pages based on PAGE_RE, returning list of Page objects
    """
    Parse files formatted like:

    ===== PAGE 1 =====
    text...
    ===== PAGE 2 =====
    text...

    Returns list of Page(page_num, text).
    """
    lines = raw.splitlines()    # split into lines for easier processing
    pages: List[Page] = []
    current_page_num: int | None = None
    buf: List[str] = [] # buffer to accumulate lines for current page

    def flush():    # helper to flush current page buffer into pages list when we hit a new page or end of file
        nonlocal buf, current_page_num
        if current_page_num is None:
            return
        text = "\n".join(buf).strip()
        pages.append(Page(page_num=current_page_num, text=text))
        buf = []

    for line in lines:
        m = PAGE_RE.match(line.strip())
        if m:
            flush()
            current_page_num = int(m.group(1))
        else:
            # Skip empty leading lines in a page
            buf.append(line)

    flush()
    # Remove totally empty pages
    pages = [p for p in pages if p.text.strip()]
    return pages


def words(text: str) -> List[str]:
    # simple word split (good enough for now)
    return re.findall(r"\S+", text)


def make_chunks_from_pages(pages: List[Page], source_file: str) -> List[Dict[str, Any]]:
    """
    Chunk across pages while preserving start/end page metadata.
    """
    # Flatten pages into a stream of (page_num, word)
    stream: List[Tuple[int, str]] = []
    for p in pages:
        for w in words(p.text):
            stream.append((p.page_num, w))

    if not stream:
        return []

    chunks: List[Dict[str, Any]] = []
    i = 0
    chunk_id = 0

    while i < len(stream):
        # target window
        j = min(i + CHUNK_WORDS, len(stream))
        window = stream[i:j]

        start_page = window[0][0]
        end_page = window[-1][0]
        text = " ".join(w for _, w in window).strip()
        wcount = len(window)

        # Only skip tiny chunks if we already have at least 1 chunk
        if wcount >= MIN_CHUNK_WORDS or chunk_id == 0:
            chunks.append({
                "source_file": source_file,
                "chunk_id": chunk_id,
                "start_page": start_page,
                "end_page": end_page,
                "approx_words": wcount,
                "text": text
            })
            chunk_id += 1

        # advance with overlap
        if j == len(stream):
            break
        i = max(j - OVERLAP_WORDS, i + 1)

    return chunks


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(TEXT_DIR.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {TEXT_DIR}")
        return

    print(f"Found {len(txt_files)} text files.")

    for txt_path in txt_files:
        raw = read_text_file(txt_path)
        pages = split_into_pages(raw)

        source_pdf_guess = txt_path.stem + ".pdf"  # matches your naming
        chunks = make_chunks_from_pages(pages, source_pdf_guess)

        out_path = OUT_DIR / f"{txt_path.stem}_chunks.json"
        out_path.write_text(json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"Chunked {txt_path.name}: {len(chunks)} chunks -> {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
