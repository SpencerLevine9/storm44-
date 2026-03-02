import json
from pathlib import Path
from typing import List, Dict, Any

# Simple, explainable proxy for token limits
MAX_CHARS = 1800
MIN_CHARS = 400


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def chunk_youtube(
    segments_jsonl: Path,
    metadata_json: Path,
    out_chunks_json: Path
) -> None:
    segments = read_jsonl(segments_jsonl)

    if not segments:
        raise ValueError(f"No segments found in {segments_jsonl}")

    # Load metadata
    with open(metadata_json, "r", encoding="utf-8") as f:
        meta = json.load(f)

    video_id = meta.get("video_id")
    title = meta.get("title")
    url = meta.get("url")

    chunks = []
    buffer = []
    buffer_len = 0

    seg_start_idx = 0
    chunk_idx = 0

    for i, seg in enumerate(segments):
        text = seg.get("text", "").strip()
        if not text:
            continue

        buffer.append(text)
        buffer_len += len(text)

        if buffer_len >= MAX_CHARS:
            chunk_text = " ".join(buffer)

            start_time = segments[seg_start_idx].get("start")
            end_time = (
                segments[i].get("start", 0)
                + segments[i].get("duration", 0)
            )

            chunks.append({
                "chunk_id": f"{segments_jsonl.stem}_chunk_{chunk_idx:03d}",
                "source_type": "youtube",
                "video_id": video_id,
                "title": title,
                "url": url,
                "text": chunk_text,
                "segment_start_idx": seg_start_idx,
                "segment_end_idx": i,
                "start_time": start_time,
                "end_time": end_time
            })

            chunk_idx += 1
            buffer = []
            buffer_len = 0
            seg_start_idx = i + 1

    # Flush remaining buffer
    if buffer:
        start_time = segments[seg_start_idx].get("start")
        last = segments[-1]
        end_time = last.get("start", 0) + last.get("duration", 0)

        chunks.append({
            "chunk_id": f"{segments_jsonl.stem}_chunk_{chunk_idx:03d}",
            "source_type": "youtube",
            "video_id": video_id,
            "title": title,
            "url": url,
            "text": " ".join(buffer),
            "segment_start_idx": seg_start_idx,
            "segment_end_idx": len(segments) - 1,
            "start_time": start_time,
            "end_time": end_time
        })

    # Write output
    out_chunks_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_chunks_json, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"✅ Wrote {len(chunks)} YouTube chunks to {out_chunks_json}")


if __name__ == "__main__":
    # Example local test (adjust paths if needed)
    base = Path("machine_learning/artifacts")

    chunk_youtube(
        segments_jsonl=base / "youtube_segments" / "Video_1.jsonl",
        metadata_json=base / "metadata" / "Video_1.json",
        out_chunks_json=base / "chunks" / "Video_1_chunks.json"
    )
    chunk_youtube(
        segments_jsonl=base / "youtube_segments" / "Video_2.jsonl",
        metadata_json=base / "metadata" / "Video_2.json",
        out_chunks_json=base / "chunks" / "Video_2_chunks.json"
    )