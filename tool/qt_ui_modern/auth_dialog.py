"""Export/Import Login State dialog — portable JSON via Playwright storage_state."""
from __future__ import annotations
import time
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QGroupBox,
    QComboBox, QLineEdit, QSizePolicy,
)
from . import theme as t


def _list_profiles() -> list:
    """List profile folders under chrome_user_data/."""
    try:
        from settings_manager import CHROME_USER_DATA_ROOT
        root = Path(CHROME_USER_DATA_ROOT)
        if not root.exists():
            return []
        return sorted(
            p.name for p in root.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )
    except Exception:
        return []


class _ExportWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, profile_name: str, out_path: str):
        super().__init__()
        self._profile = profile_name
        self._out_path = out_path

    def run(self):
        try:
            import auth_export
            result = auth_export.export_login_state(
                self._profile,
                self._out_path,
                log_callback=self.log.emit,
            )
            msg = f"Exported {result['cookies']} cookies, {result['origins']} origins"
            self.finished.emit(True, msg)
        except Exception as e:
            self.finished.emit(False, str(e))


class _ImportWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, profile_name: str, in_path: str):
        super().__init__()
        self._profile = profile_name
        self._in_path = in_path

    def run(self):
        try:
            import auth_export
            result = auth_export.import_login_state(
                self._profile,
                self._in_path,
                log_callback=self.log.emit,
            )
            msg = f"Imported {result['cookies']} cookies, {result['origins']} origins into {result['profile']}"
            self.finished.emit(True, msg)
        except Exception as e:
            self.finished.emit(False, str(e))


_DIALOG_STYLE = f"""
    QDialog {{ background: {t.BG_DARK}; }}
    QLabel {{ color: {t.TEXT_PRIMARY}; }}
    QGroupBox {{
        color: {t.TEXT_SECONDARY}; border: 1px solid {t.BORDER};
        border-radius: 8px; margin-top: 12px; padding-top: 14px;
        background: {t.BG_CARD};
    }}
    QGroupBox::title {{
        color: {t.TEXT_SECONDARY}; subcontrol-origin: margin;
        left: 12px; padding: 0 6px; font-weight: 600;
    }}
    QPushButton {{
        background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER}; border-radius: 6px;
        padding: 8px 16px; font-size: 12px;
    }}
    QPushButton:hover {{ background: {t.BG_MID}; border-color: {t.PRIMARY}; }}
    QPushButton:disabled {{ color: {t.TEXT_MUTED}; border-color: {t.BORDER}; }}
    QPushButton#primary {{
        background: {t.PRIMARY}; color: white; border: none;
        font-weight: 600; padding: 10px 20px;
    }}
    QPushButton#primary:hover {{ background: {t.PRIMARY_HOVER}; }}
    QPushButton#danger {{
        background: rgba(239,68,68,0.15); color: #ef4444;
        border: 1px solid rgba(239,68,68,0.4);
    }}
    QTextEdit {{
        background: #0F0F0F; color: #DCDCDC;
        border: 1px solid {t.BORDER}; border-radius: 6px;
        font-family: 'Cascadia Mono', Consolas, monospace; font-size: 11px;
    }}
    QListWidget {{
        background: {t.BG_CARD}; color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER}; border-radius: 6px;
    }}
    QListWidget::item:selected {{ background: {t.BG_MID}; }}
    QComboBox {{
        background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER}; border-radius: 6px;
        padding: 6px 10px;
    }}
    QLineEdit {{
        background: {t.BG_LIGHT}; color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER}; border-radius: 6px;
        padding: 6px 10px;
    }}
"""


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export / Import Login State")
        self.setMinimumSize(860, 660)
        self.setStyleSheet(_DIALOG_STYLE)

        self._worker = None
        self._thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        title = QLabel("Login Backup — Export / Import")
        title.setStyleSheet(
            f"font-family: '{t.FONT_HEADING}'; font-size: 18px; font-weight: 700;"
        )
        sub = QLabel(
            "Save Google login cookies + localStorage to portable JSON. "
            "Restore to any profile without re-logging in."
        )
        sub.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-size: 11px;")
        sub.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(sub)

        # --- Export group ---
        grp_export = QGroupBox("Export — Save current login")
        exp_layout = QVBoxLayout(grp_export)

        row_prof_exp = QHBoxLayout()
        row_prof_exp.addWidget(QLabel("Profile:"))
        self.combo_export_profile = QComboBox()
        self._refresh_profiles(self.combo_export_profile)
        row_prof_exp.addWidget(self.combo_export_profile, 1)

        self.btn_check_chrome_exp = QPushButton("Check Chrome")
        self.btn_check_chrome_exp.clicked.connect(self._check_chrome_export)
        row_prof_exp.addWidget(self.btn_check_chrome_exp)
        exp_layout.addLayout(row_prof_exp)

        row_path_exp = QHBoxLayout()
        row_path_exp.addWidget(QLabel("Save to:"))
        self.edit_export_path = QLineEdit()
        self.edit_export_path.setPlaceholderText("(auto-generated if empty)")
        row_path_exp.addWidget(self.edit_export_path, 1)
        btn_browse_exp = QPushButton("Browse...")
        btn_browse_exp.clicked.connect(self._browse_export_path)
        row_path_exp.addWidget(btn_browse_exp)
        exp_layout.addLayout(row_path_exp)

        self.btn_export = QPushButton("Export Login State")
        self.btn_export.setObjectName("primary")
        self.btn_export.clicked.connect(self._start_export)
        exp_layout.addWidget(self.btn_export)

        layout.addWidget(grp_export)

        # --- Import group ---
        grp_import = QGroupBox("Import — Restore login to profile")
        imp_layout = QVBoxLayout(grp_import)

        row_prof_imp = QHBoxLayout()
        row_prof_imp.addWidget(QLabel("Target Profile:"))
        self.combo_import_profile = QComboBox()
        self._refresh_profiles(self.combo_import_profile)
        self.combo_import_profile.setEditable(True)
        self.combo_import_profile.lineEdit().setPlaceholderText("PROFILE_1 (or type new)")
        row_prof_imp.addWidget(self.combo_import_profile, 1)

        self.btn_check_chrome_imp = QPushButton("Check Chrome")
        self.btn_check_chrome_imp.clicked.connect(self._check_chrome_import)
        row_prof_imp.addWidget(self.btn_check_chrome_imp)
        imp_layout.addLayout(row_prof_imp)

        row_path_imp = QHBoxLayout()
        row_path_imp.addWidget(QLabel("State file:"))
        self.edit_import_path = QLineEdit()
        self.edit_import_path.setPlaceholderText("Select a saved .json state file")
        row_path_imp.addWidget(self.edit_import_path, 1)
        btn_browse_imp = QPushButton("Browse...")
        btn_browse_imp.clicked.connect(self._browse_import_path)
        row_path_imp.addWidget(btn_browse_imp)
        imp_layout.addLayout(row_path_imp)

        self.btn_import = QPushButton("Import to Profile")
        self.btn_import.setObjectName("primary")
        self.btn_import.clicked.connect(self._start_import)
        imp_layout.addWidget(self.btn_import)

        layout.addWidget(grp_import)

        # --- Saved states list ---
        grp_saved = QGroupBox("Saved States")
        saved_layout = QVBoxLayout(grp_saved)

        self.list_saved = QListWidget()
        self.list_saved.setMaximumHeight(120)
        self.list_saved.itemDoubleClicked.connect(self._on_saved_double_click)
        saved_layout.addWidget(self.list_saved)

        btn_row_saved = QHBoxLayout()
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self._refresh_saved)
        btn_use = QPushButton("Use Selected as Import Source")
        btn_use.clicked.connect(self._use_selected_saved)
        btn_row_saved.addWidget(btn_refresh)
        btn_row_saved.addWidget(btn_use)
        btn_row_saved.addStretch()
        saved_layout.addLayout(btn_row_saved)

        layout.addWidget(grp_saved)

        # --- Log ---
        log_lbl = QLabel("Log")
        log_lbl.setStyleSheet(f"color: {t.TEXT_SECONDARY}; font-weight: 600;")
        layout.addWidget(log_lbl)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(120)
        layout.addWidget(self.log_box, 1)

        # --- Bottom ---
        btm = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        btm.addStretch()
        btm.addWidget(btn_close)
        layout.addLayout(btm)

        self._refresh_saved()

    # ------------------------------------------------------------------ helpers

    def _refresh_profiles(self, combo: QComboBox):
        combo.clear()
        profiles = _list_profiles()
        for p in profiles:
            combo.addItem(p)
        if not profiles:
            combo.addItem("PROFILE_1")

    def _refresh_saved(self):
        self.list_saved.clear()
        try:
            import auth_export
            states = auth_export.list_saved_states()
        except Exception as e:
            self._log(f"Cannot load saved states: {e}")
            return
        for s in states:
            label = f"{s['name']}  |  {s['cookies']} cookies  |  {s['origins']} origins"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, s["path"])
            self.list_saved.addItem(item)
        if not states:
            self.list_saved.addItem("(no saved states)")

    def _log(self, msg: str):
        self.log_box.append(msg)

    def _is_busy(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def _set_busy(self, busy: bool):
        self.btn_export.setEnabled(not busy)
        self.btn_import.setEnabled(not busy)

    # ------------------------------------------------------------------ Chrome check

    def _check_chrome_for_profile(self, profile_name: str) -> bool:
        """Returns True if Chrome is running with given profile (show warning + offer kill)."""
        try:
            from chrome_process_manager import ChromeProcessManager
            if ChromeProcessManager.is_running_with_profile(profile_name):
                ret = QMessageBox.warning(
                    self,
                    "Chrome Running",
                    f"Chrome is currently running with profile '{profile_name}'.\n"
                    "Export/Import will fail while Chrome holds the profile lock.\n\n"
                    "Close Chrome now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if ret == QMessageBox.StandardButton.Yes:
                    ChromeProcessManager.kill_chrome()
                    self._log(f"Chrome killed for profile {profile_name}")
                return True
        except Exception as e:
            self._log(f"Chrome check error: {e}")
        return False

    def _check_chrome_export(self):
        profile = self.combo_export_profile.currentText().strip()
        running = self._check_chrome_for_profile(profile)
        if not running:
            self._log(f"Chrome not running with profile '{profile}' — safe to export")

    def _check_chrome_import(self):
        profile = self.combo_import_profile.currentText().strip()
        running = self._check_chrome_for_profile(profile)
        if not running:
            self._log(f"Chrome not running with profile '{profile}' — safe to import")

    # ------------------------------------------------------------------ browse

    def _browse_export_path(self):
        try:
            import auth_export
            profile = self.combo_export_profile.currentText().strip() or "PROFILE"
            default = str(auth_export.default_export_path(profile))
        except Exception:
            default = ""
        f, _ = QFileDialog.getSaveFileName(
            self, "Save login state", default, "JSON files (*.json);;All (*)"
        )
        if f:
            self.edit_export_path.setText(f)

    def _browse_import_path(self):
        try:
            import auth_export
            from settings_manager import DATA_GENERAL_DIR
            start_dir = str(DATA_GENERAL_DIR / "login_states")
        except Exception:
            start_dir = ""
        f, _ = QFileDialog.getOpenFileName(
            self, "Select login state file", start_dir, "JSON files (*.json);;All (*)"
        )
        if f:
            self.edit_import_path.setText(f)

    # ------------------------------------------------------------------ saved list

    def _on_saved_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.edit_import_path.setText(path)

    def _use_selected_saved(self):
        item = self.list_saved.currentItem()
        if item:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                self.edit_import_path.setText(path)

    # ------------------------------------------------------------------ export

    def _start_export(self):
        if self._is_busy():
            return
        profile = self.combo_export_profile.currentText().strip()
        if not profile:
            QMessageBox.warning(self, "Error", "Select a profile first.")
            return

        out_path = self.edit_export_path.text().strip()
        if not out_path:
            try:
                import auth_export
                out_path = str(auth_export.default_export_path(profile))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        # Pre-check Chrome lock
        self._check_chrome_for_profile(profile)

        self.log_box.clear()
        self._log(f"Exporting profile '{profile}' -> {out_path}")
        self._set_busy(True)

        self._thread = QThread(self)
        self._worker = _ExportWorker(profile, out_path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._log)
        self._worker.finished.connect(self._on_export_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(lambda: self._set_busy(False))
        self._thread.start()

    def _on_export_finished(self, success: bool, msg: str):
        if success:
            self._log(f"SUCCESS: {msg}")
            self._refresh_saved()
        else:
            self._log(f"FAILED: {msg}")

    # ------------------------------------------------------------------ import

    def _start_import(self):
        if self._is_busy():
            return
        profile = self.combo_import_profile.currentText().strip()
        if not profile:
            QMessageBox.warning(self, "Error", "Enter a target profile name.")
            return
        in_path = self.edit_import_path.text().strip()
        if not in_path:
            QMessageBox.warning(self, "Error", "Select a state file to import.")
            return

        # Pre-check Chrome lock
        self._check_chrome_for_profile(profile)

        self.log_box.clear()
        self._log(f"Importing '{in_path}' -> profile '{profile}'")
        self._set_busy(True)

        self._thread = QThread(self)
        self._worker = _ImportWorker(profile, in_path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._log)
        self._worker.finished.connect(self._on_import_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(lambda: self._set_busy(False))
        self._thread.start()

    def _on_import_finished(self, success: bool, msg: str):
        if success:
            self._log(f"SUCCESS: {msg}")
            self._refresh_profiles(self.combo_export_profile)
            self._refresh_profiles(self.combo_import_profile)
        else:
            self._log(f"FAILED: {msg}")
