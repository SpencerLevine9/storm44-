import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    VideoUnavailable,
)

import subprocess
import tempfile

def download_audio_with_ytdlp(url: str, out_wav_path: Path, cookies_path: Path) -> None:
    """
    Downloads best audio and converts to wav using yt-dlp + ffmpeg.

    Requires:
      - yt-dlp installed
      - ffmpeg on PATH
      - cookies.txt exported from a logged-in browser session
    """
    out_template = str(out_wav_path.parent / out_wav_path.stem) + ".%(ext)s"

    cmd = [
        "yt-dlp",
        "--cookies", str(cookies_path),
        "--extractor-args", "youtube:player_client=android",
        "--no-playlist",
        "-x",
        "--audio-format", "wav",
        "-o", out_template,
        url,
    ]
    subprocess.run(cmd, check=True)

def whisper_transcribe_wav(wav_path: Path) -> List[Dict[str, Any]]:
    """
    Uses faster-whisper to transcribe wav and returns segments with timestamps.
    """
    from faster_whisper import WhisperModel

    model = WhisperModel("base", device="cpu")  # change to "cuda" if you have GPU
    segments_out = []
    segments, _ = model.transcribe(str(wav_path))

    for seg in segments:
        segments_out.append({
            "text": seg.text.strip(),
            "start": float(seg.start),
            "duration": float(seg.end - seg.start),
        })
    return segments_out

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../storm44-
DATA_RESOURCES = PROJECT_ROOT / "machine_learning" / "data" / "data_resources.json"
ART_TEXT_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "text"
ART_META_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "metadata"
COOKIES_PATH = PROJECT_ROOT / "machine_learning" / "secrets" / "cookies.txt"
ART_SEG_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "youtube_segments"
ART_SEG_DIR.mkdir(parents=True, exist_ok=True)
ART_TEXT_DIR.mkdir(parents=True, exist_ok=True)
ART_META_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_\-]+", "", name)
    return name[:80] if len(name) > 80 else name

def write_segments_jsonl(out_path: Path, segments: List[Dict[str, Any]], *, video_id: str, title: str, url: str, source: str) -> None:
    """
    Writes one JSON object per line (JSONL). Each line = one segment.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        for seg in segments:
            row = {
                "source_type": source,
                "video_id": video_id,
                "title": title,
                "url": url,
                "text": seg.get("text", ""),
                "start": seg.get("start", None),
                "duration": seg.get("duration", None),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def extract_video_id(url: str) -> Optional[str]:
    """
    Supports:
      - https://www.youtube.com/watch?v=VIDEOID
      - https://youtu.be/VIDEOID
      - https://www.youtube.com/shorts/VIDEOID
    """
    try:
        u = urlparse(url)
        if u.netloc in ("youtu.be", "www.youtu.be"):
            return u.path.strip("/")

        if "youtube.com" in u.netloc:
            # watch?v=
            qs = parse_qs(u.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]

            # /shorts/VIDEOID
            parts = [p for p in u.path.split("/") if p]
            if len(parts) >= 2 and parts[0] == "shorts":
                return parts[1]
    except Exception:
        return None

    return None

def fetch_transcript_text(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns dict with:
      - text
      - language
      - segments (list of dicts with text/start/duration)
    OR returns None if no transcript is available.
    Compatible with youtube-transcript-api >= 1.0 (instance-based API).
    """
    api = YouTubeTranscriptApi()
    raw_segments = None
    language = None

    try:
        fetched = api.fetch(video_id, languages=["en"])
        raw_segments = fetched
        language = "en"
    except Exception:
        try:
            fetched = api.fetch(video_id)
            raw_segments = fetched
        except Exception:
            return None

    if not raw_segments:
        return None

    # Normalise to plain dicts regardless of snippet object type
    segments = []
    for s in raw_segments:
        if hasattr(s, "text"):
            segments.append({
                "text": s.text.strip(),
                "start": float(s.start),
                "duration": float(getattr(s, "duration", 0.0)),
            })
        elif isinstance(s, dict):
            segments.append({
                "text": s.get("text", "").strip(),
                "start": float(s.get("start", 0.0)),
                "duration": float(s.get("duration", 0.0)),
            })

    if not segments:
        return None

    text = "\n".join(s["text"] for s in segments if s["text"]).strip()
    if not text:
        return None

    return {
        "text": text,
        "language": language,
        "segments": segments,
    }

def main() -> None:
    if not DATA_RESOURCES.exists():
        raise FileNotFoundError(f"Missing data_resources.json at: {DATA_RESOURCES}")

    resources = json.loads(DATA_RESOURCES.read_text(encoding="utf-8"))
    yt_items: List[Dict[str, str]] = resources.get("youtube", [])

    if not yt_items:
        print("No youtube items found in data_resources.json. Nothing to do.")
        return

    print(f"Found {len(yt_items)} YouTube URLs.")

    for item in yt_items:
        title = item.get("title", "youtube_video")
        url = item.get("url", "")
        vid = extract_video_id(url)

        if not vid:
            print(f"[SKIP] Could not parse video id from URL: {url}")
            continue

        # define output files BEFORE the try so both paths can use them
        base = safe_filename(title)
        out_txt = ART_TEXT_DIR / f"{base}.txt"
        out_meta = ART_META_DIR / f"{base}.json"
        out_seg = ART_SEG_DIR / f"{base}.jsonl"

        print(f"Extracting transcript: {title} ({vid})")

        try:
            # =========================
            # Path A: Transcript API
            # =========================
            data = fetch_transcript_text(vid)
            if data is None:
                raise RuntimeError("NO_TRANSCRIPT")

            text = data["text"].strip()
            if not text:
                print(f"[WARN] Transcript fetched but empty for: {title} ({vid})")
                continue

            out_txt.write_text(text, encoding="utf-8")

            meta = {
                "source_type": "youtube",
                "title": title,
                "url": url,
                "video_id": vid,
                "language": data.get("language"),
                "output_text_file": str(out_txt).replace("\\", "/"),
                "num_segments": len(data.get("segments", [])),
                "output_segments_file": str(out_seg).replace("\\", "/"),
                "transcript_source": "youtube_transcript_api",
            }
            out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")

            # PART B (Transcript API): write JSONL segments
            write_segments_jsonl(
                out_seg,
                data.get("segments", []),
                video_id=vid,
                title=title,
                url=url,
                source="youtube_transcript_api",
            )

            print(f"  -> wrote {out_txt}, {out_meta}, {out_seg}")

        except RuntimeError as e:
            # Only used for our own "NO_TRANSCRIPT" signal
            if str(e) != "NO_TRANSCRIPT":
                raise

            # =========================
            # Path B: Whisper fallback
            # =========================
            print(f"[NO TRANSCRIPT] {title} ({vid})")
            print(f"[FALLBACK] Using Whisper for: {title} ({vid})")

            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    wav_path = Path(tmpdir) / f"{vid}.wav"
                    download_audio_with_ytdlp(url, wav_path, COOKIES_PATH)
                    segments = whisper_transcribe_wav(wav_path)

                text = "\n".join(s.get("text", "") for s in segments if s.get("text")).strip()
                if not text:
                    print(f"[WARN] Whisper returned empty transcript for: {title} ({vid})")
                    continue

                out_txt.write_text(text, encoding="utf-8")

                meta = {
                    "source_type": "youtube",
                    "title": title,
                    "url": url,
                    "video_id": vid,
                    "language": "whisper",
                    "output_text_file": str(out_txt).replace("\\", "/"),
                    "num_segments": len(segments),
                    "output_segments_file": str(out_seg).replace("\\", "/"),
                    "transcript_source": "whisper",
                }
                out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")

                # PART B (Whisper): write JSONL segments
                write_segments_jsonl(
                    out_seg,
                    segments,
                    video_id=vid,
                    title=title,
                    url=url,
                    source="whisper",
                )

                print(f"  -> wrote {out_txt}, {out_meta}, {out_seg} (Whisper fallback)")

            except subprocess.CalledProcessError as ex:
                print(f"[FALLBACK ERROR] yt-dlp/ffmpeg failed for {title}: {ex}")
            except Exception as ex:
                print(f"[FALLBACK ERROR] Whisper failed for {title}: {type(ex).__name__}: {ex}")

        except VideoUnavailable as e:
            # This is NOT a "use Whisper" case. If the video is unavailable, yt-dlp will fail too.
            print(f"[UNAVAILABLE] {title}: {e}")

        except Exception as e:
            # Only for unexpected Transcript API path errors (rate limits, etc.)
            msg = str(e).lower()
            if "too many requests" in msg or "429" in msg:
                print(f"[RATE LIMITED] {title}: {e}")
                print("Stop for now, try again later.")
                break

            print(f"[ERROR] {title}: {type(e).__name__}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
