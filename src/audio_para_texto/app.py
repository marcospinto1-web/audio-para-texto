from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .transcriber import SUPPORTED_EXTENSIONS, TranscriptResult, transcribe_audio


def error_log_path() -> Path:
    if sys.platform == "darwin":
        folder = Path.home() / "Library" / "Logs" / "Audio para Texto"
    else:
        folder = Path.home() / "AppData" / "Local" / "Audio para Texto" / "Logs"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "erros.log"


def record_error() -> Path:
    path = error_log_path()
    with path.open("a", encoding="utf-8") as log:
        log.write(f"\n--- {datetime.now().isoformat(timespec='seconds')} ---\n")
        log.write(traceback.format_exc())
    return path


APP_STYLE = """
QWidget { background: #F6F7FB; color: #172033; font-size: 14px; }
QLabel#title { font-size: 27px; font-weight: 700; color: #14213D; }
QLabel#subtitle { color: #536179; font-size: 14px; }
QLabel#dropZone {
  background: white; border: 2px dashed #86A8E7; border-radius: 14px;
  color: #42526A; padding: 28px;
}
QPushButton {
  background: #246BFD; color: white; border: none; border-radius: 8px;
  padding: 10px 16px; font-weight: 600;
}
QPushButton:hover { background: #1656D9; }
QPushButton:disabled { background: #AAB6CA; }
QPushButton#secondary { background: white; color: #246BFD; border: 1px solid #B8C8E8; }
QPlainTextEdit {
  background: white; border: 1px solid #DCE3EF; border-radius: 10px;
  padding: 12px; selection-background-color: #A9C7FF;
}
QComboBox { background: white; border: 1px solid #DCE3EF; border-radius: 7px; padding: 7px; }
"""


class TranscriptionWorker(QObject):
    completed = Signal(object)
    failed = Signal(str)
    status = Signal(str)

    def __init__(self, path: Path, model: str, language: str | None):
        super().__init__()
        self.path = path
        self.model = model
        self.language = language

    def run(self) -> None:
        try:
            result = transcribe_audio(
                self.path,
                model_name=self.model,
                language=self.language,
                progress=self.status.emit,
            )
            self.completed.emit(result)
        except Exception as exc:  # Error crosses the worker/UI boundary.
            log_path = record_error()
            self.failed.emit(f"{exc}\n\nDiagnóstico salvo em:\n{log_path}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.audio_path: Path | None = None
        self.worker_thread: QThread | None = None
        self.worker: TranscriptionWorker | None = None
        self.setWindowTitle("Áudio para Texto")
        self.resize(760, 650)
        self.setMinimumSize(620, 540)
        self.setAcceptDrops(True)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(32, 26, 32, 26)
        layout.setSpacing(14)

        title = QLabel("Áudio para Texto")
        title.setObjectName("title")
        subtitle = QLabel("Transcreva áudios do WhatsApp sem enviar nada para a internet.")
        subtitle.setObjectName("subtitle")
        self.drop_zone = QLabel("Solte um áudio aqui\n\nou clique em “Escolher áudio”")
        self.drop_zone.setObjectName("dropZone")
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setMinimumHeight(145)

        options = QHBoxLayout()
        self.choose_button = QPushButton("Escolher áudio")
        self.choose_button.setObjectName("secondary")
        self.choose_button.clicked.connect(self.choose_audio)
        self.model_combo = QComboBox()
        self.model_combo.addItem("Rápido — qualidade boa", "base")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Português", "pt")
        self.language_combo.addItem("Detectar idioma", None)
        self.transcribe_button = QPushButton("Transcrever")
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.clicked.connect(self.start_transcription)
        options.addWidget(self.choose_button)
        options.addStretch()
        options.addWidget(self.model_combo)
        options.addWidget(self.language_combo)
        options.addWidget(self.transcribe_button)

        self.status_label = QLabel("Pronto. Seus áudios permanecem neste computador.")
        self.status_label.setObjectName("subtitle")
        self.output = QPlainTextEdit()
        self.output.setPlaceholderText("A transcrição aparecerá aqui…")
        self.output.setMinimumHeight(190)

        actions = QHBoxLayout()
        self.copy_button = QPushButton("Copiar texto")
        self.copy_button.setObjectName("secondary")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_text)
        self.save_button = QPushButton("Salvar como TXT")
        self.save_button.setObjectName("secondary")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_text)
        actions.addWidget(self.copy_button)
        actions.addWidget(self.save_button)
        actions.addStretch()
        privacy = QLabel("🔒 100% local • gratuito • sem cadastro")
        privacy.setObjectName("subtitle")
        actions.addWidget(privacy)

        for widget in (title, subtitle, self.drop_zone):
            layout.addWidget(widget)
        layout.addLayout(options)
        layout.addWidget(self.status_label)
        layout.addWidget(self.output, 1)
        layout.addLayout(actions)
        self.setCentralWidget(root)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        urls = event.mimeData().urls()
        if urls and Path(urls[0].toLocalFile()).suffix.lower() in SUPPORTED_EXTENSIONS:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self.set_audio(Path(urls[0].toLocalFile()))
            event.acceptProposedAction()

    def choose_audio(self) -> None:
        filters = "Áudios (*.aac *.flac *.m4a *.mp3 *.mp4 *.oga *.ogg *.opus *.wav *.webm)"
        filename, _ = QFileDialog.getOpenFileName(self, "Escolher áudio", "", filters)
        if filename:
            self.set_audio(Path(filename))

    def set_audio(self, path: Path) -> None:
        self.audio_path = path
        self.drop_zone.setText(f"✓ {path.name}\n\nPronto para transcrever")
        self.transcribe_button.setEnabled(True)
        self.status_label.setText("Arquivo selecionado. Clique em Transcrever.")

    def start_transcription(self) -> None:
        if self.audio_path is None:
            return
        self._set_busy(True)
        self.output.clear()
        self.status_label.setText("Preparando… Na primeira vez, o modelo será baixado.")
        self.worker_thread = QThread(self)
        self.worker = TranscriptionWorker(
            self.audio_path,
            self.model_combo.currentData(),
            self.language_combo.currentData(),
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.status.connect(self.status_label.setText)
        self.worker.completed.connect(self.transcription_done)
        self.worker.failed.connect(self.transcription_failed)
        self.worker.completed.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def transcription_done(self, result: TranscriptResult) -> None:
        self.output.setPlainText(result.text)
        minutes, seconds = divmod(round(result.duration_seconds), 60)
        confidence = round(result.language_probability * 100)
        self.status_label.setText(
            f"Concluído • {minutes}:{seconds:02d} • idioma {result.language} ({confidence}%)"
        )
        self.copy_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self._set_busy(False)

    def transcription_failed(self, message: str) -> None:
        self.status_label.setText("Não foi possível transcrever.")
        QMessageBox.critical(
            self,
            "Erro na transcrição",
            f"{message}\n\nSe for o primeiro uso, verifique a conexão com a internet.",
        )
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self.transcribe_button.setEnabled(not busy and self.audio_path is not None)
        self.choose_button.setEnabled(not busy)
        self.model_combo.setEnabled(not busy)
        self.language_combo.setEnabled(not busy)

    def copy_text(self) -> None:
        QApplication.clipboard().setText(self.output.toPlainText())
        self.status_label.setText("Texto copiado.")

    def save_text(self) -> None:
        suggested = self.audio_path.with_suffix(".txt").name if self.audio_path else "transcricao.txt"
        filename, _ = QFileDialog.getSaveFileName(self, "Salvar transcrição", suggested, "Texto (*.txt)")
        if filename:
            Path(filename).write_text(self.output.toPlainText(), encoding="utf-8")
            self.status_label.setText(f"Texto salvo em {Path(filename).name}.")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Áudio para Texto")
    app.setOrganizationName("Áudio para Texto")
    app.setStyleSheet(APP_STYLE)
    font = QFont()
    font.setFamilies(["Inter", "SF Pro Text", "Segoe UI", "Arial"])
    app.setFont(font)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

