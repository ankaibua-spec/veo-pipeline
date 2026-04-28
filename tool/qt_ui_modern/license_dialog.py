"""Commercial license activation dialog — first-run gate."""
from __future__ import annotations
import hmac
import json
import hashlib
import os
import platform
import uuid
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox,
)
from . import theme as t

LICENSE_FILE = Path.home() / ".veo_pipeline" / "license.json"

# Per-machine key is HMAC-SHA256(secret, machine_id) → first 16 hex chars,
# formatted XXXX-XXXX-XXXX-XXXX. Secret can be overridden at build time via
# VEO_LICENSE_SECRET env (CI sets a project-specific value); otherwise a
# deterministic compile-time default is used.
_SECRET_RAW = os.environ.get("VEO_LICENSE_SECRET", "")
if not _SECRET_RAW:
    try:
        from tool.qt_ui_modern import _secret as _s  # build-injected, never committed
        _SECRET_RAW = _s.VEO_LICENSE_SECRET
    except Exception:
        pass
if not _SECRET_RAW:
    import logging
    logging.getLogger(__name__).warning(
        "VEO_LICENSE_SECRET not set — app boots in unlicensed mode"
    )
    _SECRET_RAW = None  # type: ignore[assignment]
LICENSE_SECRET = _SECRET_RAW.encode() if _SECRET_RAW else None  # type: ignore[union-attr]


def expected_key(mid: str) -> str:
    """Deterministic per-machine key. Caller (dev) generates this offline and
    sends to the user; user pastes it into the dialog."""
    digest = hmac.new(LICENSE_SECRET, mid.encode(), hashlib.sha256).hexdigest().upper()
    short = digest[:16]
    return "-".join(short[i:i + 4] for i in range(0, 16, 4))


def _windows_machine_guid() -> str | None:
    """Read Windows MachineGuid from registry — stable across reboots/NIC changes."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return str(guid)
    except Exception:
        return None


def machine_id() -> str:
    """Stable per-machine ID. Prefer Windows MachineGuid, fallback to node+system."""
    win_guid = _windows_machine_guid()
    if win_guid:
        raw = f"{win_guid}|{platform.system()}"
    else:
        raw = f"{uuid.getnode()}|{platform.node()}|{platform.system()}|{platform.machine()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24].upper()


def load_license() -> dict | None:
    if not LICENSE_FILE.exists():
        return None
    try:
        return json.loads(LICENSE_FILE.read_text())
    except Exception:
        return None


def save_license(key: str, mid: str):
    """Atomic write: tmp file + rename."""
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = LICENSE_FILE.with_suffix(".tmp")
    payload = json.dumps({"key": key, "machine_id": mid, "activated": True}, indent=2)
    tmp.write_text(payload)
    tmp.replace(LICENSE_FILE)  # atomic on POSIX + NTFS


def _bypass_enabled() -> bool:
    """Bypass only when an explicit dev marker is on disk AND env var is set.
    File is never created by the installer — dev creates it manually on their
    own machine. Production binaries on customers cannot enable bypass with
    just an env var."""
    if os.environ.get("VEO_BYPASS_LICENSE") != "1":
        return False
    marker = Path.home() / ".veo_pipeline" / ".dev_bypass"
    return marker.exists()


def is_licensed() -> bool:
    """Validate license: stored key must match HMAC(secret, current machine_id).
    Bypass only via dev marker file + env (see _bypass_enabled)."""
    if _bypass_enabled():
        return True
    lic = load_license()
    if not lic or not lic.get("activated"):
        return False
    stored_mid = lic.get("machine_id", "")
    stored_key = (lic.get("key", "") or "").upper()
    current = machine_id()
    if stored_mid != current:
        return False  # license bound to another machine
    return hmac.compare_digest(stored_key, expected_key(current))


class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{t.APP_NAME} — Activate")
        self.setFixedSize(680, 420)
        self.setStyleSheet(f"""
            QDialog {{ background: {t.BG_DARK}; }}
            QLabel {{ color: {t.TEXT_PRIMARY}; }}
            QLineEdit {{
                background: {t.BG_LIGHT}; border: 1px solid {t.BORDER};
                border-radius: 8px; padding: 10px 14px; font-size: 13px;
                color: {t.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{ border-color: {t.PRIMARY}; }}
            QPushButton {{
                background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
                border: 1px solid {t.BORDER}; border-radius: 8px;
                padding: 10px 16px; font-size: 12px; min-height: 18px;
            }}
            QPushButton:hover {{ background: {t.BG_MID}; border-color: {t.PRIMARY}; }}
            QPushButton#primary {{
                background: {t.PRIMARY}; border: none; border-radius: 8px;
                padding: 12px 28px; color: white; font-weight: 600; font-size: 13px;
                min-width: 120px;
            }}
            QPushButton#primary:hover {{ background: {t.PRIMARY_HOVER}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel(f"Activate {t.APP_NAME}")
        title.setStyleSheet(f"font-family: '{t.FONT_HEADING}'; font-size: 22px; font-weight: 700;")
        sub = QLabel("Enter your license key to unlock all features.")
        sub.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # Machine ID display
        mid = machine_id()
        mid_label = QLabel("Machine ID")
        mid_label.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; padding-top: 8px;")
        mid_field = QLineEdit(mid)
        mid_field.setReadOnly(True)
        mid_field.setStyleSheet(f"font-family: 'Cascadia Mono', Consolas, monospace; color: {t.PRIMARY};")
        layout.addWidget(mid_label)
        layout.addWidget(mid_field)

        # License key input
        key_label = QLabel("License Key")
        key_label.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; padding-top: 8px;")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        layout.addWidget(key_label)
        layout.addWidget(self.key_input)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        copy_btn = QPushButton("📋 Copy Machine ID")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(mid))
        contact_btn = QPushButton(f"💬 Contact {t.AUTHOR}")
        contact_btn.clicked.connect(lambda: __import__("webbrowser").open(t.SUPPORT_URL))
        activate_btn = QPushButton("✓ Activate")
        activate_btn.setObjectName("primary")
        activate_btn.setMinimumWidth(140)
        activate_btn.setMinimumHeight(40)
        activate_btn.clicked.connect(self._activate)
        btn_row.addWidget(copy_btn)
        btn_row.addWidget(contact_btn)
        btn_row.addStretch()
        btn_row.addWidget(activate_btn)
        layout.addStretch()
        layout.addLayout(btn_row)

        # Footer
        footer = QLabel(f"<a href='{t.SUPPORT_URL}' style='color:{t.PRIMARY}'>Get a license — Zalo {t.AUTHOR_ZALO}</a>")
        footer.setOpenExternalLinks(True)
        footer.setStyleSheet("font-size: 11px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def _activate(self):
        # Normalise whitespace + dashes; uppercase for HMAC compare.
        key = self.key_input.text().strip().upper().replace(" ", "")
        if "-" not in key and len(key) == 16:
            key = "-".join(key[i:i + 4] for i in range(0, 16, 4))
        mid = machine_id()
        if not hmac.compare_digest(key, expected_key(mid)):
            QMessageBox.warning(
                self,
                "License không hợp lệ",
                "License key không khớp với Machine ID.\n\n"
                "Gửi Machine ID bên dưới cho Truong Hoa qua Zalo "
                f"{t.AUTHOR_ZALO} để nhận key đúng máy này.",
            )
            return
        save_license(key, mid)
        QMessageBox.information(self, "Activated", "License đã lưu. App tiếp tục mở.")
        self.accept()


def run_license_dialog() -> bool:
    """Hien thi dialog kich hoat license. Tra ve True neu user kich hoat thanh cong."""
    from PyQt6.QtWidgets import QApplication
    import sys
    # Dam bao co QApplication truoc khi mo dialog
    app = QApplication.instance() or QApplication(sys.argv)
    dlg = LicenseDialog()
    return dlg.exec() == dlg.DialogCode.Accepted


# Lazy import to avoid pulling QApplication at module load
from PyQt6.QtWidgets import QApplication
