# Local Audiobook Generator — README

Turn `Code_Audiobook_Edition.pdf` into a set of chapter-by-chapter audio
files on your own machine, fully offline, using [Piper TTS](https://github.com/OHF-Voice/piper1-gpl)
(open-source, no cloud, no account needed).

---

## What you need

- Python 3.9 or newer
- The `make_audiobook.py` script
- The `Code_Audiobook_Edition.pdf` file (or any similarly-cleaned book PDF)
- About 5–10 minutes for setup, then a few minutes of processing per chapter

---

## Step 1: Install the required packages

Open a terminal in the folder where you saved `make_audiobook.py`, then run:

```bash
pip install piper-tts pdfplumber
```

- **piper-tts** — the offline text-to-speech engine
- **pdfplumber** — reads the PDF's text and font sizes so the script can tell chapter headings apart from body text

If `pip` isn't recognized, try `pip3` instead.

---

## Step 2: Choose and download a voice

Piper ships many free, pre-built voices. Preview them before downloading so you pick one you actually like:

- **Listen to voice samples:** https://rhasspy.github.io/piper-samples/
- **Full voice library (download source):** https://huggingface.co/rhasspy/piper-voices

A few good starting points for narrating a technical book:
| Voice name | Style |
|---|---|
| `en_US-lessac-medium` | Neutral, clear, good default |
| `en_US-ryan-high` | Deeper male voice |
| `en_US-libritts-high` | Warm, audiobook-style narration |
| `en_GB-alan-medium` | British male voice |

Once you've picked one, download it with:

```bash
python -m piper.download_voices en_US-lessac-medium
```

Replace `en_US-lessac-medium` with whichever voice name you chose. This downloads two files into your current folder:
- `en_US-lessac-medium.onnx` (the voice model)
- `en_US-lessac-medium.onnx.json` (its configuration — keep this next to the `.onnx` file)

> **Want a different voice later?** Just run the download command again with a new voice name — you can have as many downloaded at once as you like and switch between them with the `--voice` flag below.

> ⚠️ **A note on voice sources:** Stick to the official Hugging Face repo above. Some third-party sites (Nexus Mods, random Discord shares) host Piper voices trained on celebrities or game/movie characters without consent — avoid those regardless of the source.

---

## Step 3: Run the script

```bash
python make_audiobook.py Code_Audiobook_Edition.pdf --voice en_US-lessac-medium.onnx
```

**Arguments:**
| Flag | Required? | Description |
|---|---|---|
| `pdf_path` (first argument) | Yes | Path to the cleaned book PDF |
| `--voice` | Yes | Path to the `.onnx` voice model file you downloaded |
| `--out-dir` | No | Output folder name (default: `audiobook_output`) |

Example with a custom output folder:
```bash
python make_audiobook.py Code_Audiobook_Edition.pdf --voice en_US-ryan-high.onnx --out-dir my_audiobook
```

---

## Step 4: Find your audio files

Once it finishes, you'll have a folder like this:

```
audiobook_output/
├── 00_Preface_to_the_Paperback_Edition.wav
├── 01_Best_Friends.wav
├── 02_Codes_and_Combinations.wav
├── 03_Braille_and_Binary_Codes.wav
...
├── 25_The_Graphical_Revolution.wav
```

Each file is one chapter, in order, ready to play in any media player.

---

## How the script works (short version)

Instead of blindly reading text top to bottom, the script opens the PDF with `pdfplumber` and looks at **font size** to figure out structure:

- Large text (~22pt) → a chapter title → starts a new audio file
- Medium text (~13pt, e.g. "Chapter One") → a chapter marker → skipped (not narrated)
- Regular text (~11.5pt) → body text → gets narrated

This means it splits the book by its actual formatting rather than guessing from blank lines, which is more reliable — including on other PDFs, as long as headings use a visibly larger font than body text.

If you run this on a different PDF and the chapter splitting looks off, you can adjust this line near the top of the script:

```python
HEADING_SIZE_THRESHOLD = 12.5
```

Raise or lower it depending on your PDF's actual font sizes (use the print statements described in the script's comments, or ask for help inspecting a specific PDF's font sizes).

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'piper'"**
→ Run `pip install piper-tts` again, and make sure you're using the same Python environment to install and to run the script.

**Script finds 0 or 1 sections**
→ The PDF's headings might not be a larger font than the body text, so nothing looks like a heading. This script is tuned for PDFs formatted like `Code_Audiobook_Edition.pdf`.

**Audio sounds robotic or mispronounces technical terms**
→ Try a different voice (`en_US-libritts-high` tends to sound most natural), or use SSML-style punctuation adjustments in the source text (e.g., spelling out acronyms) if a specific term keeps getting mangled.

**It's slow**
→ Piper is CPU-only by default and roughly real-time per chapter — a few minutes for a long chapter is normal. If you have an NVIDIA GPU, `PiperVoice.load(..., use_cuda=True)` (with `onnxruntime-gpu` installed) speeds this up significantly.

---

## Optional next step

Want the output combined into a single audiobook file with chapter markers (like a real audiobook `.m4b`), or converted to `.mp3`? That's a quick follow-up script using `ffmpeg` — just ask.
