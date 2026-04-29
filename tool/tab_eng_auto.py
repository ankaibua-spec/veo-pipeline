"""tab_eng_auto.py — Tab UI for 'Auto English Lessons' feature.

User picks level(s) + topic + N, clicks Generate → worker thread calls
generate_batch() → prompts appended to tab Text→Video via push_to_text_to_video().
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# --- Worker thread --------------------------------------------------------

class _Worker(QThread):
    """QThread worker that calls generate_batch() in background."""

    log = pyqtSignal(str)      # progress messages
    done = pyqtSignal(list)    # list[str] prompts when finished

    def __init__(self, n: int, levels: list[str], topic: str):
        super().__init__()
        self._n = n
        self._levels = levels
        self._topic = topic
        self._stop = False

    def stop(self) -> None:
        """Signal the worker to stop after current lesson."""
        self._stop = True

    def run(self) -> None:
        try:
            from eng_auto_prompt import generate_batch
            prompts = generate_batch(
                n=self._n,
                level_filter=self._levels,
                topic_filter=self._topic,
                log_callback=lambda m: self.log.emit(m),
                stop_check=lambda: self._stop,
            )
        except Exception as e:
            self.log.emit(f"Worker error: {e}")
            prompts = []
        self.done.emit(prompts)


# --- Main tab widget -------------------------------------------------------

class EngAutoTab(QWidget):
    """Tab 'Auto English Lessons'.

    Layout:
      [Config group: Level checkboxes | Topic dropdown | N spinner]
      [Buttons: Generate | Stop | Clear log]
      [Log box (read-only)]
      [Info label]
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("EngAutoTab")
        self._worker: _Worker | None = None

        self.setStyleSheet(
            """
            QWidget#EngAutoTab {
                background: #1c1b1b;
            }
            QWidget#EngAutoTab QLabel {
                font-size: 14px;
            }
            QWidget#EngAutoTab QGroupBox {
                font-size: 14px;
                font-weight: 800;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                margin-top: 8px;
                background: #201f1f;
            }
            QWidget#EngAutoTab QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QWidget#EngAutoTab QComboBox {
                font-size: 13px;
                min-height: 32px;
                background: #1c1b1b;
            }
            QWidget#EngAutoTab QComboBox QAbstractItemView {
                background: #1c1b1b;
                selection-background-color: #2a2a2a;
                outline: none;
            }
            QWidget#EngAutoTab QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 4px 8px;
            }
            QWidget#EngAutoTab QPlainTextEdit {
                font-size: 13px;
                background: #1c1b1b;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                font-family: "JetBrains Mono", "Cascadia Mono", Consolas, monospace;
            }
            QWidget#EngAutoTab QPushButton {
                font-size: 13px;
                min-height: 32px;
                padding: 4px 16px;
                border-radius: 6px;
            }
            QWidget#EngAutoTab QCheckBox {
                font-size: 13px;
            }
            QWidget#EngAutoTab QSpinBox {
                font-size: 13px;
                min-height: 32px;
                background: #1c1b1b;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # --- Config group ---
        cfg_box = QGroupBox("Cau hinh / Configuration")
        cfg_layout = QHBoxLayout(cfg_box)
        cfg_layout.setSpacing(16)
        cfg_layout.setContentsMargins(12, 16, 12, 12)

        # Level checkboxes
        level_label = QLabel("Level:")
        level_label.setStyleSheet("font-weight: 700;")
        cfg_layout.addWidget(level_label)

        self.level_checks: dict[str, QCheckBox] = {}
        for code in ("A1", "A2", "B1"):
            cb = QCheckBox(code)
            cb.setChecked(code == "A2")  # default: A2 selected
            self.level_checks[code] = cb
            cfg_layout.addWidget(cb)

        cfg_layout.addSpacing(16)

        # Topic dropdown
        topic_label = QLabel("Topic:")
        topic_label.setStyleSheet("font-weight: 700;")
        cfg_layout.addWidget(topic_label)

        self.topic_combo = QComboBox()
        self.topic_combo.setMinimumWidth(200)
        # Populate from pool data
        topic_items = [
            ("all", "Tat ca (Random)"),
            ("food", "Ordering food"),
            ("directions", "Asking directions"),
            ("shopping", "Shopping for clothes"),
            ("interview", "Job interview"),
            ("airport", "At the airport"),
            ("doctor", "Doctor visit"),
            ("phone", "Phone conversation"),
            ("weather", "Weather small talk"),
            ("hotel", "Hotel check-in"),
            ("appearance", "Describing appearance"),
            ("routine", "Daily routine"),
            ("help", "Asking help politely"),
        ]
        for tid, tlabel in topic_items:
            self.topic_combo.addItem(tlabel, userData=tid)
        cfg_layout.addWidget(self.topic_combo)

        cfg_layout.addSpacing(16)

        # N spinner
        n_label = QLabel("So bai:")
        n_label.setStyleSheet("font-weight: 700;")
        cfg_layout.addWidget(n_label)

        self.spin_n = QSpinBox()
        self.spin_n.setRange(1, 50)
        self.spin_n.setValue(5)
        self.spin_n.setFixedWidth(80)
        cfg_layout.addWidget(self.spin_n)

        cfg_layout.addStretch()
        root.addWidget(cfg_box)

        # --- Button row ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_run = QPushButton("Generate")
        self.btn_run.setStyleSheet(
            "QPushButton { background: #4F8EF7; color: white; font-weight: 700; }"
            "QPushButton:hover { background: #6aa0f7; }"
            "QPushButton:disabled { background: #2a2a2a; color: #8c909e; }"
        )
        self.btn_run.clicked.connect(self._on_generate)
        btn_row.addWidget(self.btn_run)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet(
            "QPushButton { background: #EF4444; color: white; font-weight: 700; }"
            "QPushButton:hover { background: #f77; }"
            "QPushButton:disabled { background: #2a2a2a; color: #8c909e; }"
        )
        self.btn_stop.clicked.connect(self._on_stop)
        btn_row.addWidget(self.btn_stop)

        self.btn_clear = QPushButton("Clear log")
        self.btn_clear.clicked.connect(self._clear_log)
        btn_row.addWidget(self.btn_clear)

        btn_row.addStretch()
        root.addLayout(btn_row)

        # --- Log box ---
        log_label = QLabel("Log:")
        log_label.setStyleSheet("font-weight: 700; color: #e5e2e1;")
        root.addWidget(log_label)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Log se hien o day sau khi click Generate...")
        self.log_box.setMinimumHeight(300)
        root.addWidget(self.log_box, 1)

        # --- Info label ---
        info = QLabel(
            "Prompts se duoc them vao tab 'Text -> Video'. Mo tab do va bam Render de gen video."
        )
        info.setStyleSheet("color: #c2c6d5; font-size: 12px; padding: 4px 0;")
        info.setWordWrap(True)
        root.addWidget(info)

    # --- Slots ------------------------------------------------------------

    def _append_log(self, msg: str) -> None:
        """Append a line to log box, auto-scroll."""
        try:
            self.log_box.appendPlainText(str(msg))
        except Exception:
            pass

    def _clear_log(self) -> None:
        self.log_box.clear()

    def _on_generate(self) -> None:
        """Start worker thread."""
        levels = [code for code, cb in self.level_checks.items() if cb.isChecked()]
        if not levels:
            self._append_log("Vui long chon it nhat 1 level (A1/A2/B1).")
            return

        n = int(self.spin_n.value())
        topic = self.topic_combo.currentData() or "all"

        self._append_log(
            f"Bat dau sinh {n} bai, level={'+'.join(levels)}, topic={topic}"
        )

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self._worker = _Worker(n=n, levels=levels, topic=topic)
        self._worker.log.connect(self._append_log)
        self._worker.done.connect(self._on_batch_done)
        self._worker.start()

    def _on_stop(self) -> None:
        """Request worker to stop."""
        if self._worker is not None:
            self._worker.stop()
            self._append_log("Stop requested — waiting for current lesson to finish...")
        self.btn_stop.setEnabled(False)

    def _on_batch_done(self, prompts: list[str]) -> None:
        """Called when worker finishes. Append prompts to Text->Video tab."""
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)

        if not prompts:
            self._append_log("Khong co prompt nao duoc tao ra.")
            return

        # Push to Text->Video tab
        ok = _push_to_text_to_video(prompts)
        if ok:
            self._append_log(f"Da append {len(prompts)} prompts vao tab Text -> Video.")
        else:
            # Fallback: save to temp file
            try:
                import time as _time
                tmp_path = _fallback_save(prompts)
                self._append_log(
                    f"Khong tim thay tab Text->Video. Da luu {len(prompts)} prompts vao: {tmp_path}"
                )
            except Exception as e:
                self._append_log(f"Fallback save error: {e}")


# --- Helper: push prompts to TextToVideoTab --------------------------------

def _push_to_text_to_video(prompts: list[str]) -> bool:
    """Find TextToVideoTab in running app and call append_prompts().

    Returns True if found and called successfully.
    """
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return False
        for w in app.allWidgets():
            if w.__class__.__name__ == "TextToVideoTab":
                try:
                    w.append_prompts(prompts)
                    return True
                except Exception:
                    continue
    except Exception:
        pass
    return False


def _fallback_save(prompts: list[str]) -> str:
    """Save prompts to a tmp file when TextToVideoTab not found."""
    import time as _time
    from pathlib import Path
    path = Path(__file__).parent / f"eng_auto_prompts_{int(_time.time())}.txt"
    path.write_text("\n".join(prompts), encoding="utf-8")
    return str(path)
