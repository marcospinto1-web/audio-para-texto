from pathlib import Path

import pytest

from audio_para_texto.transcriber import join_segments, validate_audio


def test_join_segments_normalizes_spacing():
    assert join_segments([" Olá ", "", " tudo bem? "]) == "Olá tudo bem?"


def test_validate_audio_accepts_whatsapp_ogg(tmp_path: Path):
    audio = tmp_path / "WhatsApp Ptt.ogg"
    audio.write_bytes(b"fake")
    assert validate_audio(audio) == audio.resolve()


def test_validate_audio_rejects_unknown_format(tmp_path: Path):
    document = tmp_path / "arquivo.pdf"
    document.write_bytes(b"fake")
    with pytest.raises(ValueError, match="Formato não reconhecido"):
        validate_audio(document)

