"""
Local audiobook generator using Piper TTS (fully offline, open-source).

SETUP (run once):
    pip install piper-tts pdfplumber
    python -m piper.download_voices en_US-lessac-medium
    # This downloads en_US-lessac-medium.onnx + .onnx.json into the current folder.
    # Browse/listen to other voice options at https://rhasspy.github.io/piper-samples/

USAGE:
    python make_audiobook.py Code_Audiobook_Edition.pdf --voice en_US-lessac-medium.onnx

OUTPUT:
    A folder "audiobook_output/" containing one WAV file per section, e.g.:
        00_Preface_to_the_Paperback_Edition.wav
        01_Best_Friends.wav
        02_Codes_and_Combinations.wav
        ...

How it works:
    Rather than re-extracting plain text (which loses structure), this script
    reads the PDF with pdfplumber and uses font size to tell headings apart
    from body text:
      - Book title / big heading   (~26pt, ~20pt)  -> section boundary
      - "Chapter One" style marker (~13pt)          -> section boundary
      - Chapter title (~22pt)                       -> section title
      - Everything else (~11.5pt)                   -> body text to narrate
    This matches the styles used when the companion cleaning script built the PDF.
    If you run this on a differently-formatted PDF, adjust HEADING_SIZE_THRESHOLD below.
"""

import argparse
import re
import wave
from pathlib import Path

import pdfplumber
from piper import PiperVoice

# Any line whose max font size is >= this is treated as a heading, not body text.
HEADING_SIZE_THRESHOLD = 12.5


def extract_structured_sections(pdf_path: str):
    """
    Walks the PDF page by page, using font size to split it into
    (title, body_text) sections.
    Returns a list of (title, body_text) tuples in reading order.
    """
    sections = []
    current_title = None
    current_body = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for line in page.extract_text_lines():
                text = line["text"].strip()
                if not text:
                    continue
                sizes = [c["size"] for c in line.get("chars", []) if "size" in c]
                max_size = max(sizes) if sizes else 0

                if max_size >= HEADING_SIZE_THRESHOLD:
                    # Heading line. "Chapter One" (13pt) markers precede the
                    # real title (22pt) - skip the marker, use the next
                    # heading line as the section title.
                    if re.match(r"^Chapter\s+\S+$", text):
                        continue
                    # Flush the previous section before starting a new one
                    if current_title is not None and current_body:
                        sections.append((current_title, "\n\n".join(current_body)))
                    current_title = text
                    current_body = []
                else:
                    current_body.append(text)

    if current_title is not None and current_body:
        sections.append((current_title, "\n\n".join(current_body)))

    return sections


def safe_filename(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:60] or "untitled"


def synthesize_section(voice: PiperVoice, text: str, out_path: Path):
    with wave.open(str(out_path), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a cleaned book PDF into a local audiobook using Piper TTS."
    )
    parser.add_argument("pdf_path", help="Path to the cleaned PDF")
    parser.add_argument("--voice", required=True, help="Path to the Piper .onnx voice model file")
    parser.add_argument("--out-dir", default="audiobook_output", help="Output folder for the WAV files")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading and structuring {args.pdf_path} ...")
    sections = extract_structured_sections(args.pdf_path)
    print(f"Found {len(sections)} sections.")

    print(f"Loading voice model {args.voice} ...")
    voice = PiperVoice.load(args.voice)

    for idx, (title, body) in enumerate(sections):
        if not body.strip():
            continue
        fname = f"{idx:02d}_{safe_filename(title)}.wav"
        out_path = out_dir / fname
        print(f"  Synthesizing: {title!r} -> {fname} ({len(body.split())} words)")
        synthesize_section(voice, body, out_path)

    print(f"\nDone. Audio files are in: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
