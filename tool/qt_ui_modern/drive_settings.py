"""Drive Settings dialog — configure Drive sync from inside app.

No need to manually edit JSON. Saves to ~/.veo_pipeline/onboarded.json.
Helper buttons: open Drive folder, open Google Cloud Console, import OAuth from app.trbm.shop.
"""
from __future__ import annotations
import json
import shutil
import webbrowser
import urllib.request
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QMessageBox,
)
from . import theme as t

CONFIG_FILE = Path.home() / ".veo_pipeline" / "onboarded.json"
CRED_FILE = Path.home() / ".veo_pipeline" / "drive_credentials.json"
APP_TRBM_BASE = "https://app.trbm.shop"
DRIVE_BASE = "https://drive.google.com/drive/folders/"
CLOUD_CONSOLE = "https://console.cloud.google.com/iam-admin/serviceaccounts"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text())
        except: pass
    return {}


def save_config(d: dict):
    import os as _os
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    tmp.replace(CONFIG_FILE)
    # Bao mat: chi chu so huu doc duoc file chua thong tin Drive
    try:
        _os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


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

        # Drive folder ID — with "Open Drive" helper
        layout.addWidget(self._lbl("Google Drive folder ID"))
        self.drive_id = QLineEdit(cfg.get("drive_id", ""))
        self.drive_id.setPlaceholderText("Copy from Drive URL: drive.google.com/drive/folders/<THIS_PART>")
        drive_row = QHBoxLayout()
        drive_row.addWidget(self.drive_id)
        open_drive_btn = QPushButton("📂 Open Drive")
        open_drive_btn.clicked.connect(self._open_drive)
        drive_row.addWidget(open_drive_btn)
        layout.addLayout(drive_row)

        # Drive credentials JSON — 3 ways: file picker, Cloud Console helper, import from app.trbm.shop
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

        # Helper buttons row
        helper_row = QHBoxLayout()
        cloud_btn = QPushButton("☁ Open Cloud Console")
        cloud_btn.clicked.connect(lambda: webbrowser.open(CLOUD_CONSOLE))
        cloud_btn.setToolTip("Open Google Cloud Console → IAM → Service Accounts to create JSON key")
        helper_row.addWidget(cloud_btn)

        import_btn = QPushButton("⬇ Import from app.trbm.shop")
        import_btn.clicked.connect(self._import_from_vps)
        import_btn.setToolTip("Download Drive credentials configured on VPS dashboard")
        helper_row.addWidget(import_btn)

        helper_row.addStretch()
        layout.addLayout(helper_row)

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
        upload_btn = QPushButton("⬆ Upload Now")
        upload_btn.setObjectName("Accent")
        upload_btn.setToolTip("Scan output folder + upload all *.mp4 to Drive immediately")
        upload_btn.clicked.connect(self._upload_now)
        btn_row.addWidget(upload_btn)

        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
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

    def _open_drive(self):
        fid = self.drive_id.text().strip()
        if fid:
            webbrowser.open(DRIVE_BASE + fid)
        else:
            webbrowser.open("https://drive.google.com/drive/my-drive")

    def _import_from_vps(self):
        """Fetch Drive folder + credentials from app.trbm.shop dashboard.

        Hardened: enforces HTTPS, sends the activated license key + machine_id
        as auth header. Server side must verify before returning the OAuth
        refresh_token. (Client cannot enforce server policy — this is a
        defence-in-depth signal so the endpoint can stop being open.)
        """
        if not APP_TRBM_BASE.startswith("https://"):
            QMessageBox.warning(self, "Import blocked",
                "Refusing to fetch credentials over plain HTTP. "
                "VPS endpoint must be HTTPS.")
            return
        try:
            from .license_dialog import load_license, machine_id
            lic = load_license() or {}
            req = urllib.request.Request(
                f"{APP_TRBM_BASE}/api/drive/credentials",
                headers={
                    "User-Agent": "VEO-Pipeline-Pro",
                    "X-Machine-Id": machine_id(),
                    "Authorization": f"Bearer {lic.get('key', '')}",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            QMessageBox.warning(self, "Import failed",
                f"Could not fetch from app.trbm.shop:\n{e}\n\n"
                f"VPS endpoint /api/drive/credentials must exist and accept the "
                f"license-bound auth header. Or copy JSON from Google Cloud Console.")
            return

        # Response: { drive_id, oauth: {client_id,client_secret,refresh_token}, email }
        if data.get("drive_id"):
            self.drive_id.setText(data["drive_id"])

        # Save credentials (OAuth or service account)
        cred_data = None
        if data.get("oauth"):
            o = data["oauth"]
            cred_data = {
                "type": "authorized_user",
                "client_id": o.get("client_id"),
                "client_secret": o.get("client_secret"),
                "refresh_token": o.get("refresh_token"),
            }
        elif data.get("service_account_json"):
            cred_data = data["service_account_json"]

        if cred_data:
            CRED_FILE.parent.mkdir(parents=True, exist_ok=True)
            CRED_FILE.write_text(json.dumps(cred_data, indent=2))
            # Bao mat: chi chu so huu doc duoc file chua token
            try:
                import os as _os
                _os.chmod(CRED_FILE, 0o600)
            except OSError:
                pass
            self.cred_path.setText(str(CRED_FILE) + f"  (OAuth from app.trbm.shop · {data.get('email','?')})")
            self.cred_path.setReadOnly(True)

        QMessageBox.information(self, "Import OK",
            f"Drive credentials imported.\nAccount: {data.get('email','?')}\nFolder: {data.get('drive_id','?')[:30]}...\n\nClick Save to apply.")

    def _upload_now(self):
        """One-shot upload: scan output_dir, push all *.mp4 to Drive folder."""
        from PyQt6.QtWidgets import QProgressDialog, QApplication
        out = self.output_dir.text().strip()
        fid = self.drive_id.text().strip()
        if not out or not Path(out).exists():
            QMessageBox.warning(self, "No folder", "Set output folder first (or click Auto-detect).")
            return
        if not fid:
            QMessageBox.warning(self, "No Drive folder", "Set Google Drive folder ID first.")
            return
        if not CRED_FILE.exists():
            QMessageBox.warning(self, "No credentials", "Configure Drive credentials first (Browse / Import / Cloud Console).")
            return

        files = sorted(Path(out).glob("*.mp4"))
        if not files:
            QMessageBox.information(self, "Nothing to upload", f"No *.mp4 found in:\n{out}")
            return

        # Save current settings so _drive_upload + creds loader can read them
        self._save_silent()

        from .drive_sync import _drive_upload, _load_db, _save_db, _file_hash
        db = _load_db()
        skipped = 0

        pd = QProgressDialog(f"Uploading 0 / {len(files)}...", "Cancel", 0, len(files), self)
        pd.setWindowTitle("Drive Upload")
        pd.setMinimumDuration(0)
        pd.setValue(0)
        pd.show()

        ok = 0
        fail = 0
        for i, p in enumerate(files):
            if pd.wasCanceled():
                break
            pd.setLabelText(f"Uploading {i+1} / {len(files)}: {p.name}")
            QApplication.processEvents()

            h = _file_hash(p)
            if h in db:
                skipped += 1
                pd.setValue(i + 1)
                continue

            drive_id = _drive_upload(p, fid)
            if drive_id:
                ok += 1
                db[h] = {
                    "original": p.name,
                    "renamed": p.name,
                    "size_mb": round(p.stat().st_size / 1024 / 1024, 1),
                    "drive_id": drive_id,
                    "ts": __import__("datetime").datetime.now().isoformat(),
                }
                _save_db(db)
            else:
                fail += 1
            pd.setValue(i + 1)
            QApplication.processEvents()

        pd.close()
        QMessageBox.information(self, "Upload done",
            f"✅ Uploaded: {ok}\n⏭ Skipped (already): {skipped}\n❌ Failed: {fail}\n\nFolder: {fid}")

    def _save_silent(self):
        """Save config without showing the 'Saved' popup."""
        import os as _os
        cfg = {
            "output_dir": self.output_dir.text().strip(),
            "drive_id": self.drive_id.text().strip(),
            "tg_bot": self.tg_bot.text().strip(),
            "tg_chat": self.tg_chat.text().strip(),
            "auto_update": self.auto_update.isChecked(),
        }
        cred_text = self.cred_path.text().strip()
        if cred_text and not cred_text.endswith("(already configured)") and Path(cred_text).exists():
            try:
                CRED_FILE.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cred_text, CRED_FILE)
                # Bao mat: chi chu so huu doc duoc file chua token
                try:
                    _os.chmod(CRED_FILE, 0o600)
                except OSError:
                    pass
            except Exception:
                pass
        save_config(cfg)

    def _save(self):
        import os as _os
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
                # Bao mat: chi chu so huu doc duoc file chua token
                try:
                    _os.chmod(CRED_FILE, 0o600)
                except OSError:
                    pass
            except Exception as e:
                QMessageBox.warning(self, "Cred copy failed", str(e))
                return

        save_config(cfg)
        QMessageBox.information(self, "Saved",
            "Settings saved to:\n" + str(CONFIG_FILE) +
            "\n\nRestart app to apply Drive sync.")
        self.accept()
