"""Bulk auto-login dialog — import email|password file, login all accounts sequentially."""
from __future__ import annotations
import sys
import threading
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar,
)
from . import theme as t


def parse_accounts_file(path: Path) -> list[tuple[str, str]]:
    """Parse `email|password` per line. Strips empty + comment lines."""
    accounts = []
    if not path.exists():
        return accounts
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            continue
        email, pwd = line.split("|", 1)
        email = email.strip()
        pwd = pwd.strip()
        if email and pwd:
            accounts.append((email, pwd))
    return accounts


class _BulkWorker(QObject):
    log = pyqtSignal(str)
    account_started = pyqtSignal(int, str)  # idx, email
    account_done = pyqtSignal(int, str, bool, str)  # idx, email, success, msg
    finished = pyqtSignal()

    def __init__(self, accounts: list[tuple[str, str]]):
        super().__init__()
        self._accounts = accounts
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        try:
            from login import auto_login_veo3
        except Exception as e:
            self.log.emit(f"❌ Cannot import login module: {e}")
            self.finished.emit()
            return

        for i, (email, pwd) in enumerate(self._accounts):
            if self._stop.is_set():
                self.log.emit("🛑 Stopped by user")
                break

            profile = f"PROFILE_{i+1}"
            self.account_started.emit(i, email)
            self.log.emit(f"\n=== [{i+1}/{len(self._accounts)}] {email} → {profile} ===")

            try:
                result = auto_login_veo3(
                    email, pwd,
                    profile_name=profile,
                    logger=lambda msg: self.log.emit(f"  {msg}"),
                    stop_check=self._stop.is_set,
                )
                ok = bool(result.get("success"))
                msg = result.get("message") or ""
                self.account_done.emit(i, email, ok, msg)
                if ok:
                    self.log.emit(f"✅ {email} OK")
                else:
                    self.log.emit(f"❌ {email}: {msg}")
            except Exception as e:
                self.account_done.emit(i, email, False, str(e))
                self.log.emit(f"❌ {email} exception: {e}")

        self.finished.emit()


class BulkLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Auto-Login VEO3")
        self.setMinimumSize(900, 640)
        self.setStyleSheet(f"""
            QDialog {{ background: {t.BG_DARK}; }}
            QLabel {{ color: {t.TEXT_PRIMARY}; }}
            QPushButton {{
                background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
                border: 1px solid {t.BORDER}; border-radius: 6px;
                padding: 8px 16px; font-size: 12px;
            }}
            QPushButton:hover {{ background: {t.BG_MID}; border-color: {t.PRIMARY}; }}
            QPushButton#primary {{
                background: {t.PRIMARY}; color: white; border: none;
                font-weight: 600; padding: 10px 20px;
            }}
            QPushButton#primary:hover {{ background: {t.PRIMARY_HOVER}; }}
            QTextEdit {{
                background: #0F0F0F; color: #DCDCDC;
                border: 1px solid {t.BORDER}; border-radius: 6px;
                font-family: 'Cascadia Mono', Consolas, monospace; font-size: 11px;
            }}
            QTableWidget {{
                background: {t.BG_CARD}; color: {t.TEXT_PRIMARY};
                gridline-color: {t.BORDER}; border: 1px solid {t.BORDER};
                border-radius: 6px;
            }}
            QHeaderView::section {{
                background: {t.BG_MID}; color: {t.TEXT_SECONDARY};
                border: none; padding: 6px 10px; font-weight: 600;
            }}
            QProgressBar {{
                background: {t.BG_LIGHT}; border: none; border-radius: 4px;
                text-align: center; height: 8px; color: white;
            }}
            QProgressBar::chunk {{ background: {t.PRIMARY}; border-radius: 4px; }}
        """)

        self._accounts: list[tuple[str, str]] = []
        self._worker = None
        self._thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        title = QLabel("Bulk Auto-Login")
        title.setStyleSheet(f"font-family: '{t.FONT_HEADING}'; font-size: 18px; font-weight: 700;")
        sub = QLabel("Import .txt file (one line per account, format: email|password)")
        sub.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(title)
        layout.addWidget(sub)

        # File picker row
        file_row = QHBoxLayout()
        self.btn_pick = QPushButton("📂 Choose accounts file (.txt)")
        self.btn_pick.clicked.connect(self._pick_file)
        self.btn_paste = QPushButton("📋 Paste from clipboard")
        self.btn_paste.clicked.connect(self._paste_clipboard)
        self.lbl_count = QLabel("0 accounts loaded")
        self.lbl_count.setStyleSheet(f"color: {t.TEXT_SECONDARY};")
        file_row.addWidget(self.btn_pick)
        file_row.addWidget(self.btn_paste)
        file_row.addStretch()
        file_row.addWidget(self.lbl_count)
        layout.addLayout(file_row)

        # Accounts table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Email", "Profile", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMaximumHeight(220)
        layout.addWidget(self.table)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(200)
        layout.addWidget(self.log, 1)

        # Bottom buttons
        btm = QHBoxLayout()
        self.btn_start = QPushButton("▶ Start Login All")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._start)
        self.btn_start.setEnabled(False)
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.clicked.connect(self._stop)
        self.btn_stop.setEnabled(False)
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btm.addWidget(self.btn_start)
        btm.addWidget(self.btn_stop)
        btm.addStretch()
        btm.addWidget(self.btn_close)
        layout.addLayout(btm)

    def _pick_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select accounts file", "", "Text files (*.txt);;All (*)")
        if f:
            self._load_accounts(parse_accounts_file(Path(f)))

    def _paste_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        text = QApplication.clipboard().text()
        accs = []
        for line in text.splitlines():
            line = line.strip()
            if "|" in line:
                e, p = line.split("|", 1)
                if e.strip() and p.strip():
                    accs.append((e.strip(), p.strip()))
        self._load_accounts(accs)

    def _load_accounts(self, accs):
        self._accounts = accs
        self.table.setRowCount(len(accs))
        for i, (email, _) in enumerate(accs):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(email))
            self.table.setItem(i, 2, QTableWidgetItem(f"PROFILE_{i+1}"))
            self.table.setItem(i, 3, QTableWidgetItem("⏳ Pending"))
        self.lbl_count.setText(f"{len(accs)} accounts loaded")
        self.btn_start.setEnabled(len(accs) > 0)
        self.log.append(f"📥 Loaded {len(accs)} accounts")
        self.progress.setMaximum(max(len(accs), 1))
        self.progress.setValue(0)

    def _start(self):
        if not self._accounts:
            return
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_pick.setEnabled(False)
        self.btn_paste.setEnabled(False)
        self.log.clear()
        self.log.append(f"▶ Starting bulk login for {len(self._accounts)} accounts\n")

        self._thread = QThread(self)
        self._worker = _BulkWorker(list(self._accounts))
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self.log.append)
        self._worker.account_started.connect(self._on_account_started)
        self._worker.account_done.connect(self._on_account_done)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _stop(self):
        if self._worker:
            self._worker.stop()
            self.log.append("\n🛑 Stop requested...")
            self.btn_stop.setEnabled(False)

    def _on_account_started(self, idx: int, email: str):
        self.table.setItem(idx, 3, QTableWidgetItem("⚡ Running..."))

    def _on_account_done(self, idx: int, email: str, ok: bool, msg: str):
        status = "✅ Success" if ok else f"❌ {msg[:40]}"
        self.table.setItem(idx, 3, QTableWidgetItem(status))
        self.progress.setValue(idx + 1)

    def _on_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_pick.setEnabled(True)
        self.btn_paste.setEnabled(True)
        self.log.append("\n=== All accounts processed ===")
        self._worker = None
        self._thread = None
