from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import ssl  # Imported explicitly so frozen builds bundle Python's SSL module.
import sys
from typing import Callable, Iterable


SUPPORTED_EXTENSIONS = {
    ".aac", ".flac", ".m4a", ".mp3", ".mp4", ".oga", ".ogg", ".opus",
    ".wav", ".webm",
}


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    language: str
    language_probability: float
    duration_seconds: float


def validate_audio(path: str | Path) -> Path:
    audio = Path(path).expanduser().resolve()
    if not audio.is_file():
        raise ValueError("O arquivo de áudio não foi encontrado.")
    if audio.suffix.lower() not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Formato não reconhecido. Formatos aceitos: {allowed}")
    return audio


def join_segments(texts: Iterable[str]) -> str:
    return " ".join(part.strip() for part in texts if part.strip()).strip()


def transcribe_audio(
    path: str | Path,
    model_name: str = "base",
    language: str | None = "pt",
    progress: Callable[[str], None] | None = None,
) -> TranscriptResult:
    """Transcribe an audio file locally using faster-whisper."""
    audio = validate_audio(path)
    report = progress or (lambda _message: None)

    report("Carregando o modelo de voz…")
    # Frozen Python apps do not inherit a system OpenSSL certificate path.
    # Point SSL clients at the CA bundle packaged with certifi before the model
    # downloader creates its HTTP client.
    import certifi

    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    from faster_whisper import WhisperModel

    bundle_root = Path(getattr(sys, "_MEIPASS", ""))
    bundled_model = bundle_root / "models" / model_name
    model_source = str(bundled_model) if bundled_model.is_dir() else model_name

    # CPU/int8 is the most portable configuration across Intel/ARM Macs and
    # ordinary Windows PCs. CTranslate2 still uses available CPU acceleration.
    model = WhisperModel(model_source, device="cpu", compute_type="int8")
    report("Ouvindo e transcrevendo…")

    segments, info = model.transcribe(
        str(audio),
        language=language,
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )
    text = join_segments(segment.text for segment in segments)
    if not text:
        raise ValueError("Não foi possível identificar fala neste arquivo.")

    return TranscriptResult(
        text=text,
        language=info.language,
        language_probability=float(info.language_probability),
        duration_seconds=float(info.duration),
    )

