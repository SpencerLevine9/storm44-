from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ftfy import fix_text

# Smaller chunks = better retrieval for concept questions
CHUNK_WORDS = 100
OVERLAP_WORDS = 20
MIN_CHUNK_WORDS = 35

TEXT_DIR = Path("machine_learning/artifacts/text")
OUT_DIR = Path("machine_learning/artifacts/chunks")

PAGE_RE = re.compile(r"^=+\s*PAGE\s+(\d+)\s*=+\s*$", re.IGNORECASE)


@dataclass
class Page:
    page_num: int
    text: str


def read_text_file(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return repair_text_encoding(raw)


def repair_text_encoding(text: str) -> str:
    text = fix_text(text)

    replacements = {
        "â€“": "–",
        "â€”": "—",
        "â€˜": "‘",
        "â€™": "’",
        "â€œ": "“",
        "â€": "”",
        "Â ": " ",
        "Â": "",
        "\ufeff": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def split_into_pages(raw: str) -> List[Page]:
    """
    Parse files formatted like:

    ===== PAGE 1 =====
    text...
    ===== PAGE 2 =====
    text...

    Returns list of Page(page_num, text).
    """
    lines = raw.splitlines()
    pages: List[Page] = []
    current_page_num: int | None = None
    buf: List[str] = []

    def flush() -> None:
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
            buf.append(line)

    flush()
    pages = [p for p in pages if p.text.strip()]
    return pages


def clean_pdf_text(text: str) -> str:
    """
    Remove noisy textbook lines before chunking so embeddings focus on
    actual concept content instead of chapter scaffolding.
    """
    lines = text.splitlines()
    cleaned: List[str] = []

    skip_patterns = [
        r"^chapter outline$",
        r"^chapter summary$",
        r"^learning objectives$",
        r"^access for free at",
        r"^figure\s+\d",
        r"^table\s+\d",
        r"^example\s+\d",
        r"^checkpoint\b",
        r"^concepts in practice\b",
        r"^review questions\b",
        r"^multiple choice\b",
        r"^true or false\b",
        r"^fill in the blank\b",
        r"^key terms\b",
        r"^exercise\b",
        r"^summary\b$",
        r"^by the end of this section",
        r"^access multimedia content",
        r"^link to learning",
        r"^chapter review",
        r"^try it\b",
        r"^recommended spacing",
        r"^automatic concatenation",
        r"^function description",
        r"^operator description",
        r"^syntax description",
    ]

    for line in lines:
        s = line.strip()
        if not s:
            continue

        lower = s.lower()

        if any(re.search(pat, lower) for pat in skip_patterns):
            continue

        # Skip lines that are mostly decorative / separators
        if re.fullmatch(r"[-_=•* ]{3,}", s):
            continue

        # Skip very short heading-like lines
        if len(s.split()) <= 3 and s == s.title():
            continue

        # Skip lines that are mostly symbols/numbers
        if len(re.findall(r"[A-Za-z]", s)) < 3:
            continue

        cleaned.append(s)

    # Collapse repeated whitespace but keep sentence spacing readable
    joined = "\n".join(cleaned)
    joined = re.sub(r"[ \t]+", " ", joined)
    joined = re.sub(r"\n{3,}", "\n\n", joined)
    return joined.strip()


def words(text: str) -> List[str]:
    return re.findall(r"\S+", text)


def make_chunks_from_pages(pages: List[Page], source_file: str) -> List[Dict[str, Any]]:
    """
    Chunk across pages while preserving start/end page metadata.
    Uses cleaned page text so noisy textbook scaffolding is removed first.
    """
    stream: List[Tuple[int, str]] = []

    for p in pages:
        cleaned_text = clean_pdf_text(p.text)
        if not cleaned_text:
            continue
        for w in words(cleaned_text):
            stream.append((p.page_num, w))

    if not stream:
        return []

    chunks: List[Dict[str, Any]] = []
    i = 0
    chunk_id = 0

    while i < len(stream):
        j = min(i + CHUNK_WORDS, len(stream))
        window = stream[i:j]

        start_page = window[0][0]
        end_page = window[-1][0]
        text = " ".join(w for _, w in window).strip()
        wcount = len(window)

        if wcount >= MIN_CHUNK_WORDS or chunk_id == 0:
            chunks.append(
                {
                    "source_type": "pdf",
                    "source_file": source_file,
                    "chunk_id": chunk_id,
                    "start_page": start_page,
                    "end_page": end_page,
                    "approx_words": wcount,
                    "text": text,
                }
            )
            chunk_id += 1

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

        source_pdf_guess = txt_path.stem + ".pdf"
        chunks = make_chunks_from_pages(pages, source_pdf_guess)

        out_path = OUT_DIR / f"{txt_path.stem}_chunks.json"
        out_path.write_text(
            json.dumps(chunks, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print(f"Chunked {txt_path.name}: {len(chunks)} chunks -> {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()