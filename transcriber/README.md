# JP Transcriber

Create Japanese transcription from audio files.

## Usage

### 1. Extract audio

```bash
ffmpeg -i input.mkv -map 0:a:0 -vn -ac 1 -ar 16000 -c:a pcm_s16le sample.wav
```

This produces a 16 kHz mono `.wav` file, which is usually a good input format for Whisper (smaller, faster, and typically stable).

### 2. Create transcription

First, copy your `.wav` file as `./data/sample.wav` in project directory.

For typical anime/TV rips (music + overlapping sounds), you'll usually get the best results **without VAD** and with a moderate beam size:

```bash
uv run main.py --compute-type float32 --beam-size 5
```

## Notes

- Try enabling VAD (use `--vad-filter` option) if something goes wrong in the first place.

- In practice, `float32` vs. `float16` can make significant difference.

- Larger `beam-size` (up to 10) can help on clean dialogue, but may introduce “weird” hypotheses on noisy/overlapping audio.
