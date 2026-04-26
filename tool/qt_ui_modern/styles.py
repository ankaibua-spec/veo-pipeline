"""QSS stylesheets for Fluent commercial look."""
from . import theme as t

GLOBAL_QSS = f"""
* {{
    font-family: "{t.FONT_BODY}";
    color: {t.TEXT_PRIMARY};
    outline: none;
}}

QMainWindow, QWidget#mainContainer {{
    background: {t.BG_DARK};
}}

/* Sidebar */
QFrame#sidebar {{
    background: {t.BG_MID};
    border: none;
    border-right: 1px solid {t.BORDER};
}}

QFrame#brandHeader {{
    background: transparent;
    padding: 24px 20px 16px 20px;
}}

QLabel#brandName {{
    font-family: "{t.FONT_HEADING}";
    font-size: 20px;
    font-weight: 700;
    color: {t.TEXT_PRIMARY};
    letter-spacing: 0.5px;
}}

QLabel#brandTagline {{
    font-size: 11px;
    color: {t.TEXT_MUTED};
    letter-spacing: 0.3px;
}}

QPushButton#navItem {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    color: {t.TEXT_SECONDARY};
}}

QPushButton#navItem:hover {{
    background: {t.BG_LIGHT};
    color: {t.TEXT_PRIMARY};
}}

QPushButton#navItem:checked {{
    background: {t.PRIMARY};
    color: white;
    font-weight: 600;
}}

/* Top bar */
QFrame#topBar {{
    background: {t.BG_DARK};
    border: none;
    border-bottom: 1px solid {t.BORDER};
    min-height: 56px;
    max-height: 56px;
}}

QLabel#pageTitle {{
    font-family: "{t.FONT_HEADING}";
    font-size: 18px;
    font-weight: 600;
    color: {t.TEXT_PRIMARY};
}}

QLabel#pageSubtitle {{
    font-size: 12px;
    color: {t.TEXT_MUTED};
}}

QPushButton#topAction {{
    background: {t.BG_MID};
    border: 1px solid {t.BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    color: {t.TEXT_SECONDARY};
}}

QPushButton#topAction:hover {{
    background: {t.BG_LIGHT};
    color: {t.TEXT_PRIMARY};
    border-color: {t.PRIMARY};
}}

/* Content area */
QFrame#contentArea {{
    background: {t.BG_DARK};
}}

QFrame#card {{
    background: {t.BG_CARD};
    border: 1px solid {t.BORDER};
    border-radius: 12px;
}}

QLabel#cardTitle {{
    font-size: 14px;
    font-weight: 600;
    color: {t.TEXT_PRIMARY};
    padding: 4px 0;
}}

QLabel#cardSubtitle {{
    font-size: 12px;
    color: {t.TEXT_SECONDARY};
}}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
    background: {t.BG_LIGHT};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {t.TEXT_PRIMARY};
    selection-background-color: {t.PRIMARY};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border-color: {t.PRIMARY};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

/* Buttons */
QPushButton {{
    background: {t.BG_LIGHT};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    color: {t.TEXT_PRIMARY};
}}

QPushButton:hover {{
    background: {t.BG_MID};
    border-color: {t.PRIMARY};
}}

QPushButton:pressed {{
    background: {t.BG_DARK};
}}

QPushButton:disabled {{
    background: {t.BG_MID};
    color: {t.TEXT_MUTED};
    border-color: {t.BORDER};
}}

QPushButton#primary {{
    background: {t.PRIMARY};
    border: 1px solid {t.PRIMARY};
    color: white;
    font-weight: 600;
    padding: 10px 24px;
}}

QPushButton#primary:hover {{
    background: {t.PRIMARY_HOVER};
    border-color: {t.PRIMARY_HOVER};
}}

QPushButton#primary:pressed {{
    background: {t.PRIMARY_PRESSED};
}}

QPushButton#accent {{
    background: {t.ACCENT};
    border: 1px solid {t.ACCENT};
    color: white;
    font-weight: 600;
    padding: 10px 24px;
}}

/* Labels */
QLabel {{
    color: {t.TEXT_PRIMARY};
}}

QLabel#fieldLabel {{
    font-size: 12px;
    font-weight: 500;
    color: {t.TEXT_SECONDARY};
    padding-bottom: 4px;
}}

QLabel#hint {{
    font-size: 11px;
    color: {t.TEXT_MUTED};
}}

/* Status badges */
QLabel#badgeSuccess {{
    background: rgba(16, 185, 129, 0.15);
    color: {t.SUCCESS};
    border: 1px solid {t.SUCCESS};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#badgeWarning {{
    background: rgba(245, 158, 11, 0.15);
    color: {t.WARNING};
    border: 1px solid {t.WARNING};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#badgeError {{
    background: rgba(239, 68, 68, 0.15);
    color: {t.ERROR};
    border: 1px solid {t.ERROR};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {t.BG_LIGHT};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t.BORDER};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* Tables */
QTableView, QTreeView, QListView {{
    background: {t.BG_CARD};
    border: 1px solid {t.BORDER};
    border-radius: 8px;
    gridline-color: {t.BORDER};
    selection-background-color: {t.PRIMARY};
}}

QHeaderView::section {{
    background: {t.BG_MID};
    color: {t.TEXT_SECONDARY};
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {t.BORDER};
    font-size: 12px;
    font-weight: 600;
}}

/* Progress bar */
QProgressBar {{
    background: {t.BG_LIGHT};
    border: none;
    border-radius: 6px;
    text-align: center;
    height: 8px;
    color: white;
    font-size: 10px;
}}

QProgressBar::chunk {{
    background: {t.PRIMARY};
    border-radius: 6px;
}}

/* Status bar */
QStatusBar {{
    background: {t.BG_MID};
    border-top: 1px solid {t.BORDER};
    color: {t.TEXT_SECONDARY};
    font-size: 11px;
    padding: 4px 12px;
}}

QStatusBar::item {{
    border: none;
}}
"""
