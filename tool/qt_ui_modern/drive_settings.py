"""Drive Settings dialog — configure Drive sync from inside app.

No need to manually edit JSON. Saves to ~/.veo_pipeline/onboarded.json.
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QMessageBox,
)
from . import theme as t

CONFIG_FILE = Path.home() / ".veo_pipeline" / "onboarded.json"
CRED_FILE = Path.home() / ".veo_pipeline" / "drive_credentials.json"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text())
        except: pass
    return {}


def save_config(d: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    tmp.replace(CONFIG_FILE)


class DriveSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Drive Sync Settings")
        self.setMinimumSize(720, 480)
        self.setStyleSheet(f"""
            QDialog {{ background: {t.BG_DARK}; }}
            QLabel {{ color: {t.TEXT_PRIMARY}; }}
            QLineEdit {{
                background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
                border: 1px solid {t.BORDER}; border-radius: 6px;
                padding: 8px 12px; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {t.PRIMARY}; }}
            QCheckBox {{ color: {t.TEXT_PRIMARY}; padding: 4px; }}
            QPushButton {{
                background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
                border: 1px solid {t.BORDER}; border-radius: 6px;
                padding: 8px 16px; font-size: 12px; min-height: 16px;
            }}
            QPushButton:hover {{ background: {t.BG_MID}; border-color: {t.PRIMARY}; }}
            QPushButton#primary {{
                background: {t.PRIMARY}; color: white; border: none;
                font-weight: 600; padding: 10px 20px;
            }}
            QPushButton#primary:hover {{ background: {t.PRIMARY_HOVER}; }}
        """)

        cfg = load_config()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Drive Sync Settings")
        title.setStyleSheet(f"font-family: '{t.FONT_HEADING}'; font-size: 20px; font-weight: 700;")
        sub = QLabel("Auto-upload generated videos to Google Drive folder.")
        sub.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(8)

        # Watch folder (auto-detect button)
        layout.addWidget(self._lbl("Output folder to watch (auto-detect from app dir if empty)"))
        self.output_dir = QLineEdit(cfg.get("output_dir", ""))
        self.output_dir.setPlaceholderText("e.g. C:\\Users\\you\\Downloads\\VEO_Pipeline_Pro_Windows\\downloads\\video")
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_dir)
        out_browse = QPushButton("Browse")
        out_browse.clicked.connect(self._browse_output)
        out_auto = QPushButton("Auto-detect")
        out_auto.clicked.connect(self._auto_detect)
        out_row.addWidget(out_browse)
        out_row.addWidget(out_auto)
        layout.addLayout(out_row)

        # Drive folder ID
        layout.addWidget(self._lbl("Google Drive folder ID"))
        self.drive_id = QLineEdit(cfg.get("drive_id", ""))
        self.drive_id.setPlaceholderText("Copy from Drive URL: drive.google.com/drive/folders/<THIS_PART>")
        layout.addWidget(self.drive_id)

        # Drive credentials JSON
        layout.addWidget(self._lbl("Service account JSON file"))
        self.cred_path = QLineEdit()
        if CRED_FILE.exists():
            self.cred_path.setText(str(CRED_FILE) + "  (already configured)")
            self.cred_path.setReadOnly(True)
        else:
            self.cred_path.setPlaceholderText("Path to JSON downloaded from Google Cloud Console")
        cred_row = QHBoxLayout()
        cred_row.addWidget(self.cred_path)
        cred_browse = QPushButton("Browse")
        cred_browse.clicked.connect(self._browse_cred)
        cred_row.addWidget(cred_browse)
        layout.addLayout(cred_row)

        # Telegram (optional)
        layout.addWidget(self._lbl("Telegram bot token (optional, for notifications)"))
        self.tg_bot = QLineEdit(cfg.get("tg_bot", ""))
        self.tg_bot.setPlaceholderText("123456:AAFun_...")
        layout.addWidget(self.tg_bot)

        layout.addWidget(self._lbl("Telegram chat ID (optional)"))
        self.tg_chat = QLineEdit(cfg.get("tg_chat", ""))
        self.tg_chat.setPlaceholderText("-100123...")
        layout.addWidget(self.tg_chat)

        layout.addSpacing(8)
        self.auto_update = QCheckBox("Enable auto-update from GitHub Releases")
        self.auto_update.setChecked(cfg.get("auto_update", True))
        layout.addWidget(self.auto_update)

        layout.addStretch()

        # Help link
        help_label = QLabel(
            f'<a href="https://github.com/ankaibua-spec/veo-pipeline/blob/main/docs/setup.md" '
            f'style="color: {t.PRIMARY}">📖 Setup guide — how to create service account</a>'
        )
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(help_label)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _lbl(self, txt: str) -> QLabel:
        l = QLabel(txt)
        l.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px; font-weight: 500;")
        return l

    def _browse_output(self):
        d = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_dir.text() or str(Path.home()))
        if d: self.output_dir.setText(d)

    def _browse_cred(self):
        f, _ = QFileDialog.getOpenFileName(self, "Service account JSON", "", "JSON (*.json)")
        if f: self.cred_path.setText(f)

    def _auto_detect(self):
        from .drive_sync import _autodetect_output_dir
        d = _autodetect_output_dir()
        if d: self.output_dir.setText(str(d))
        else: QMessageBox.information(self, "Auto-detect", "No downloads folder found. Run tool to gen at least 1 video first.")

    def _save(self):
        cfg = {
            "output_dir": self.output_dir.text().strip(),
            "drive_id": self.drive_id.text().strip(),
            "tg_bot": self.tg_bot.text().strip(),
            "tg_chat": self.tg_chat.text().strip(),
            "auto_update": self.auto_update.isChecked(),
        }

        # Copy credentials if user picked new file
        cred_text = self.cred_path.text().strip()
        if cred_text and not cred_text.endswith("(already configured)") and Path(cred_text).exists():
            try:
                CRED_FILE.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cred_text, CRED_FILE)
            except Exception as e:
                QMessageBox.warning(self, "Cred copy failed", str(e))
                return

        save_config(cfg)
        QMessageBox.information(self, "Saved",
            "Settings saved to:\n" + str(CONFIG_FILE) +
            "\n\nRestart app to apply Drive sync.")
        self.accept()
