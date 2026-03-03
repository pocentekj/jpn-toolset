from dataclasses import dataclass
from pathlib import Path
from typing import cast, Literal
from faster_whisper import WhisperModel


ComputeType = Literal["int8", "int8_float16", "float16", "float32"]

ALLOWED_COMPUTE_TYPES: set[ComputeType] = {"int8", "int8_float16", "float16", "float32"}
DATA_DIR = Path(__file__).parent / "data"
IN_FILE = DATA_DIR / "sample.wav"
OUT_FILE = DATA_DIR / "subs.srt"


@dataclass
class AppConfig:
    beam_size: int
    vad_filter: bool
    compute_type: ComputeType


def positive_int_argument(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


def compute_type_argument(value: str) -> ComputeType:
    value = value.lower()
    if value not in ALLOWED_COMPUTE_TYPES:
        raise argparse.ArgumentTypeError(f"{value!r} is not a valid compute_type.")
    return cast(ComputeType, value)


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02},{millis:03}"


def main(config: AppConfig):
    model = WhisperModel(
        "large-v3",
        device="cuda",
        compute_type=config.compute_type,
        cpu_threads=16,
        num_workers=1,
    )

    segments = model.transcribe(
        str(IN_FILE),
        language="ja",
        beam_size=config.beam_size,
        vad_filter=config.vad_filter,
    )[0]

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            text = segment.text.strip()

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")

    print(f"Saved to {OUT_FILE}")


if __name__ == "__main__":  # noqa
    import argparse, time

    parser = argparse.ArgumentParser(prog="jp-transcriber")
    parser.add_argument("--beam-size", type=positive_int_argument, default=10)
    parser.add_argument("--vad-filter", action="store_true")
    parser.add_argument("--compute-type", type=compute_type_argument, default="float16")
    args = parser.parse_args()

    start_time = time.perf_counter()
    main(AppConfig(**vars(args)))
    end_time = format_timestamp(time.perf_counter() - start_time)

    print(f"Done in {end_time}s")
