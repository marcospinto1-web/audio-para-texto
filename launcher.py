import sys
import traceback
from pathlib import Path


if len(sys.argv) >= 4 and sys.argv[1] == "--diagnose":
    output = Path(sys.argv[3])
    try:
        from audio_para_texto.transcriber import transcribe_audio

        result = transcribe_audio(sys.argv[2], progress=lambda text: None)
        output.write_text(f"OK\n{result.text}", encoding="utf-8")
    except Exception:
        output.write_text(traceback.format_exc(), encoding="utf-8")
    raise SystemExit(0)

from audio_para_texto.app import main

raise SystemExit(main())

