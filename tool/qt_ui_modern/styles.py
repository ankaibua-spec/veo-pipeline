"""QSS stylesheets — Stitch design tokens applied to PyQt6.

Material-on-dark palette: #131313 surfaces, #acc7ff primary,
hairline 1px #2a2a2a borders, Inter + JetBrains Mono.
"""
from . import theme as t

# Use the strongest accent (#4F8EF7) for filled CTA so primary buttons
# read as "actionable" against the soft #acc7ff hover/link tint.
CTA = t.PRIMARY_ACCENT

GLOBAL_QSS = f"""
* {{
    font-family: "{t.FONT_BODY}";
    color: {t.TEXT_PRIMARY};
    outline: none;
}}

QMainWindow, QWidget#mainContainer {{
    background: {t.BG_DARK};
}}

/* === Sidebar === */
QFrame#sidebar {{
    background: {t.BG_CONTAINER_LOW};
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
    font-weight: 600;
    color: {t.TEXT_PRIMARY};
    letter-spacing: -0.2px;
}}

QLabel#brandTagline {{
    font-family: "{t.FONT_MONO}";
    font-size: 10px;
    color: {t.TEXT_MUTED};
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}

QPushButton#navItem {{
    background: transparent;
    border: none;
    border-radius: {t.RADIUS_SM}px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    color: {t.TEXT_SECONDARY};
}}

QPushButton#navItem:hover {{
    background: {t.BG_CONTAINER};
    color: {t.TEXT_PRIMARY};
}}

QPushButton#navItem:checked {{
    background: {t.BG_CONTAINER_HIGH};
    color: {t.TEXT_PRIMARY};
    font-weight: 600;
    border-left: 3px solid {t.PRIMARY};
    padding-left: 13px;
}}

/* === Top bar === */
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
    letter-spacing: -0.2px;
}}

QLabel#pageSubtitle {{
    font-size: 12px;
    color: {t.TEXT_MUTED};
}}

QPushButton#topAction {{
    background: {t.BG_CONTAINER};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_SM}px;
    padding: 6px 14px;
    font-size: 12px;
    color: {t.TEXT_SECONDARY};
}}

QPushButton#topAction:hover {{
    background: {t.BG_CONTAINER_HIGH};
    color: {t.TEXT_PRIMARY};
    border-color: {t.PRIMARY};
}}

/* === Content === */
QFrame#contentArea {{
    background: {t.BG_DARK};
}}

QFrame#card {{
    background: {t.BG_CONTAINER};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_MD}px;
}}

QFrame#cardElevated {{
    background: {t.BG_CONTAINER_HIGH};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_MD}px;
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

QLabel#monoLabel {{
    font-family: "{t.FONT_MONO}";
    font-size: 10px;
    color: {t.TEXT_MUTED};
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}

/* === Inputs === */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: {t.BG_CONTAINER_LOW};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_SM}px;
    padding: 8px 12px;
    font-size: 13px;
    color: {t.TEXT_PRIMARY};
    selection-background-color: {t.PRIMARY};
    selection-color: #001a40;
}}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QComboBox:hover, QSpinBox:hover {{
    border-color: {t.BORDER_VARIANT};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border-color: {t.PRIMARY};
}}

QLineEdit[readOnly="true"] {{
    background: {t.BG_DARK};
    color: {t.TEXT_MUTED};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

/* === Buttons === */
QPushButton {{
    background: {t.BG_CONTAINER};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_SM}px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    color: {t.TEXT_PRIMARY};
}}

QPushButton:hover {{
    background: {t.BG_CONTAINER_HIGH};
    border-color: {t.BORDER_VARIANT};
}}

QPushButton:pressed {{
    background: {t.BG_CONTAINER_LOW};
}}

QPushButton:disabled {{
    background: {t.BG_CONTAINER_LOW};
    color: {t.TEXT_MUTED};
    border-color: {t.BORDER};
}}

QPushButton#primary {{
    background: {CTA};
    border: 1px solid {CTA};
    color: #ffffff;
    font-weight: 600;
    padding: 10px 24px;
}}

QPushButton#primary:hover {{
    background: {t.PRIMARY_HOVER};
    border-color: {t.PRIMARY_HOVER};
    color: #001a40;
}}

QPushButton#primary:pressed {{
    background: {t.PRIMARY_PRESSED};
}}

QPushButton#accent {{
    background: {t.ACCENT};
    border: 1px solid {t.ACCENT};
    color: #ffffff;
    font-weight: 600;
    padding: 10px 24px;
}}

QPushButton#accent:hover {{
    background: #FF8159;
    border-color: #FF8159;
}}

QPushButton#ghost {{
    background: transparent;
    border: 1px solid transparent;
    color: {t.TEXT_SECONDARY};
}}

QPushButton#ghost:hover {{
    background: {t.BG_CONTAINER};
    color: {t.TEXT_PRIMARY};
}}

QPushButton#danger {{
    background: rgba(239, 68, 68, 0.10);
    border: 1px solid rgba(239, 68, 68, 0.30);
    color: {t.ERROR};
}}

QPushButton#danger:hover {{
    background: rgba(239, 68, 68, 0.18);
    border-color: {t.ERROR};
}}

/* === Labels === */
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

/* === Status badges === */
QLabel#badgeSuccess {{
    background: rgba(34, 197, 94, 0.15);
    color: {t.SUCCESS};
    border: 1px solid rgba(34, 197, 94, 0.30);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#badgeWarning {{
    background: rgba(250, 204, 21, 0.15);
    color: {t.WARNING};
    border: 1px solid rgba(250, 204, 21, 0.30);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#badgeError {{
    background: rgba(239, 68, 68, 0.15);
    color: {t.ERROR};
    border: 1px solid rgba(239, 68, 68, 0.30);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#badgeInfo {{
    background: rgba(172, 199, 255, 0.10);
    color: {t.PRIMARY};
    border: 1px solid rgba(172, 199, 255, 0.25);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}

/* === Scrollbars (slim 6px) === */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 4px 2px 4px 0;
}}

QScrollBar::handle:vertical {{
    background: rgba(58, 57, 57, 0.5);
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(58, 57, 57, 0.9);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0 4px 2px 4px;
}}

QScrollBar::handle:horizontal {{
    background: rgba(58, 57, 57, 0.5);
    border-radius: 3px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: rgba(58, 57, 57, 0.9);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* === Tables === */
QTableView, QTreeView, QListView {{
    background: {t.BG_CONTAINER};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_SM}px;
    gridline-color: {t.BORDER};
    selection-background-color: {t.BG_CONTAINER_HIGH};
    selection-color: {t.TEXT_PRIMARY};
    alternate-background-color: {t.BG_CONTAINER_LOW};
}}

QTableView::item, QTreeView::item, QListView::item {{
    padding: 8px;
    border: none;
}}

QTableView::item:hover, QTreeView::item:hover, QListView::item:hover {{
    background: {t.BG_CONTAINER_HIGH};
}}

QHeaderView::section {{
    background: {t.BG_CONTAINER_LOW};
    color: {t.TEXT_MUTED};
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {t.BORDER};
    font-family: "{t.FONT_MONO}";
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* === Progress bar === */
QProgressBar {{
    background: {t.BG_CONTAINER_LOW};
    border: none;
    border-radius: 4px;
    text-align: center;
    height: 6px;
    color: {t.TEXT_PRIMARY};
    font-size: 10px;
}}

QProgressBar::chunk {{
    background: {CTA};
    border-radius: 4px;
}}

/* === Status bar === */
QStatusBar {{
    background: {t.BG_CONTAINER_LOW};
    border-top: 1px solid {t.BORDER};
    color: {t.TEXT_MUTED};
    font-family: "{t.FONT_MONO}";
    font-size: 11px;
    padding: 4px 12px;
    letter-spacing: 0.5px;
}}

QStatusBar::item {{
    border: none;
}}

/* === Tabs === */
QTabWidget::pane {{
    background: {t.BG_CONTAINER};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_MD}px;
    top: -1px;
}}

QTabBar::tab {{
    background: transparent;
    color: {t.TEXT_MUTED};
    padding: 10px 20px;
    border: none;
    font-size: 13px;
}}

QTabBar::tab:hover {{
    color: {t.TEXT_PRIMARY};
}}

QTabBar::tab:selected {{
    color: {t.TEXT_PRIMARY};
    font-weight: 600;
    border-bottom: 2px solid {t.PRIMARY};
}}

/* === Checkbox / Radio === */
QCheckBox, QRadioButton {{
    color: {t.TEXT_PRIMARY};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {t.BORDER_VARIANT};
    background: {t.BG_CONTAINER_LOW};
}}

QCheckBox::indicator {{
    border-radius: 4px;
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background: {CTA};
    border-color: {CTA};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border-color: {t.PRIMARY};
}}

/* === ToolTip === */
QToolTip {{
    background: {t.BG_CONTAINER_HIGH};
    color: {t.TEXT_PRIMARY};
    border: 1px solid {t.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* === Menu === */
QMenu {{
    background: {t.BG_CONTAINER};
    border: 1px solid {t.BORDER};
    border-radius: {t.RADIUS_SM}px;
    padding: 4px;
}}

QMenu::item {{
    background: transparent;
    color: {t.TEXT_PRIMARY};
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
}}

QMenu::item:selected {{
    background: {t.BG_CONTAINER_HIGH};
}}

QMenu::separator {{
    height: 1px;
    background: {t.BORDER};
    margin: 4px 8px;
}}
"""
