from __future__ import annotations  # for Python 3.9 compatibility

import os # for os.PathLike
import json
from pathlib import Path   # for text extraction: provides convenient shorthand methods for reading files as either text or raw bytes
from typing import Dict, Any, List

import fitz  # PyMuPDF


def extract_pdf_text(pdf_path: Path) -> Dict[str, Any]:
    """
    Extracts text from a PDF using PyMuPDF, page by page.
    Returns a dict containing:
      - full_text: concatenated text
      - pages: list of page dicts with page_num and text
    """
    doc = fitz.open(str(pdf_path))
    pages: List[Dict[str, Any]] = []

    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text")  # best default for textbooks
        
        # Fallback: some PDFs are scanned images
        if not text.strip():
            text = page.get_text("blocks")
            text = "\n".join([b[4] for b in text if isinstance(b[4], str)])

        pages.append({"page_num": i + 1, "text": text})

    doc.close()

    full_text = "\n\n".join(
        [f"\n===== PAGE {p['page_num']} =====\n{p['text']}" for p in pages]
    )

    return {"full_text": full_text, "pages": pages}


def main():
    # INPUT: where your PDFs live
    input_dir = Path("machine_learning/data/pdf/CS_pdfs")
    # If you actually keep them in machine_learning/data/pdf/CS_pdfs:
    # input_dir = Path("machine_learning/data/pdf/CS_pdfs")

    # OUTPUT: where extracted text + metadata will go
    out_text_dir = Path("machine_learning/artifacts/text")
    out_meta_dir = Path("machine_learning/artifacts/metadata")

    out_text_dir.mkdir(parents=True, exist_ok=True)
    out_meta_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_dir.rglob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found under: {input_dir.resolve()}")

    print(f"Found {len(pdf_files)} PDFs.")
    for pdf_path in pdf_files:
        print(f"Extracting: {pdf_path}")

        data = extract_pdf_text(pdf_path)

        # Make safe filenames
        stem = pdf_path.stem

        txt_path = out_text_dir / f"{stem}.txt"
        meta_path = out_meta_dir / f"{stem}.json"

        # Save text
        txt_path.write_text(data["full_text"], encoding="utf-8")

        # Save metadata (for citations later)
        meta = {
            "source_type": "pdf",
            "source_file": str(pdf_path.as_posix()),
            "output_text_file": str(txt_path.as_posix()),
            "num_pages": len(data["pages"]),
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        print(f"  -> wrote {txt_path} and {meta_path}")

    print("Done.")


if __name__ == "__main__":
    main()
