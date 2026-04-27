"""First-run onboarding wizard."""
from __future__ import annotations
import json
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFileDialog, QPushButton, QCheckBox,
)
from . import theme as t

ONBOARD_FLAG = Path.home() / ".veo_pipeline" / "onboarded.json"


def needs_onboarding() -> bool:
    return not ONBOARD_FLAG.exists()


def mark_onboarded(data: dict):
    ONBOARD_FLAG.parent.mkdir(parents=True, exist_ok=True)
    ONBOARD_FLAG.write_text(json.dumps(data, indent=2))


class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(f"Welcome to {t.APP_NAME}")
        self.setSubTitle(t.APP_TAGLINE)
        layout = QVBoxLayout(self)
        msg = QLabel(
            f"This wizard will set up:\n"
            f"  • Output folder for generated videos\n"
            f"  • Drive sync (optional)\n"
            f"  • Telegram notifications (optional)\n\n"
            f"Takes ~1 minute. You can skip and configure later in Settings."
        )
        msg.setWordWrap(True)
        layout.addWidget(msg)


class OutputPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Output Folder")
        self.setSubTitle("Where generated videos will be saved")
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.path = QLineEdit(str(Path.home() / "Videos" / "VEO_Output"))
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._browse)
        row.addWidget(self.path); row.addWidget(browse)
        layout.addLayout(row)
        self.registerField("output_dir", self.path)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select output folder", self.path.text())
        if d: self.path.setText(d)


class IntegrationsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Integrations (optional)")
        self.setSubTitle("Drive sync + Telegram notify — skip if not needed")
        layout = QVBoxLayout(self)

        self.drive_id = QLineEdit()
        self.drive_id.setPlaceholderText("Google Drive folder ID (optional)")
        self.drive_cred = QLineEdit()
        self.drive_cred.setPlaceholderText("Path to drive_credentials.json (optional)")
        cred_btn = QPushButton("Browse...")
        cred_btn.clicked.connect(self._browse_cred)
        self.tg_bot = QLineEdit()
        self.tg_bot.setPlaceholderText("Telegram bot token (optional)")
        self.tg_chat = QLineEdit()
        self.tg_chat.setPlaceholderText("Telegram chat ID (optional)")
        self.auto_update = QCheckBox("Enable auto-update from GitHub every 6h")
        self.auto_update.setChecked(True)

        layout.addWidget(QLabel("Drive folder ID:"))
        layout.addWidget(self.drive_id)
        layout.addWidget(QLabel("Drive service account JSON:"))
        cred_row = QHBoxLayout()
        cred_row.addWidget(self.drive_cred)
        cred_row.addWidget(cred_btn)
        layout.addLayout(cred_row)
        layout.addWidget(QLabel("Telegram bot token:"))
        layout.addWidget(self.tg_bot)
        layout.addWidget(QLabel("Telegram chat ID:"))
        layout.addWidget(self.tg_chat)
        layout.addWidget(self.auto_update)

        self.registerField("drive_id", self.drive_id)
        self.registerField("drive_cred", self.drive_cred)
        self.registerField("tg_bot", self.tg_bot)
        self.registerField("tg_chat", self.tg_chat)
        self.registerField("auto_update", self.auto_update)

    def _browse_cred(self):
        f, _ = QFileDialog.getOpenFileName(self, "Drive service account JSON", "", "JSON (*.json)")
        if f: self.drive_cred.setText(f)


class FinishPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("All set!")
        self.setSubTitle("Click Finish to start using VEO Pipeline Pro")
        layout = QVBoxLayout(self)
        msg = QLabel(
            f"Setup complete. You can change these settings anytime in the Settings tab.\n\n"
            f"Need help?\n"
            f"  • Documentation: docs/setup.md\n"
            f"  • Support: Zalo {t.AUTHOR_ZALO}\n"
            f"  • Author: {t.AUTHOR}"
        )
        msg.setWordWrap(True)
        layout.addWidget(msg)


class OnboardingWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{t.APP_NAME} — First Run Setup")
        self.setMinimumSize(640, 460)
        self.addPage(WelcomePage())
        self.addPage(OutputPage())
        self.addPage(IntegrationsPage())
        self.addPage(FinishPage())
        self.setStyleSheet(f"""
            QWizard {{ background: {t.BG_DARK}; }}
            QLabel {{ color: {t.TEXT_PRIMARY}; }}
            QLineEdit, QCheckBox {{
                background: {t.BG_LIGHT}; border: 1px solid {t.BORDER};
                border-radius: 6px; padding: 8px 12px; color: {t.TEXT_PRIMARY};
            }}
            QPushButton {{
                background: {t.BG_LIGHT}; border: 1px solid {t.BORDER};
                border-radius: 6px; padding: 8px 16px; color: {t.TEXT_PRIMARY};
            }}
            QPushButton:hover {{ background: {t.BG_MID}; border-color: {t.PRIMARY}; }}
        """)

    def collect(self) -> dict:
        def _txt(name):
            v = self.field(name)
            if hasattr(v, "text"): return v.text()
            return str(v) if v is not None else ""
        return {
            "output_dir": _txt("output_dir"),
            "drive_id": _txt("drive_id"),
            "drive_cred": _txt("drive_cred"),
            "tg_bot": _txt("tg_bot"),
            "tg_chat": _txt("tg_chat"),
            "auto_update": bool(self.field("auto_update")),
        }
