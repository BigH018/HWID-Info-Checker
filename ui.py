from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGroupBox, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from hardware import LoaderThread, read_error_log, clear_error_log

# ── Theme ──────────────────────────────────────────────────────────────────────

ACCENT   = "#00aaff"        # bright blue
ACCENT_H = "#33bbff"        # hover
ACCENT_P = "#007acc"        # pressed
BG       = "#0a0a0a"        # near-black window
SURFACE  = "#111111"        # card background
SURFACE2 = "#161616"        # inset (log bg)
BORDER   = "#2a2a2a"        # subtle border
TEXT     = "#e8e8e8"        # primary text
SUBTEXT  = "#666666"        # muted labels
DIM      = "#3a3a3a"        # disabled / secondary button
ERROR    = "#ff4f4f"        # error text
MONO     = QFont("Consolas", 10)

_CARD_STYLE = f"""
    QGroupBox {{
        color: {SUBTEXT};
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1.5px;
        border: 1px solid {BORDER};
        border-radius: 6px;
        margin-top: 12px;
        padding: 8px 12px 10px 12px;
        background: {SURFACE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        background: {BG};
    }}
"""

_BTN_SECONDARY = f"""
    QPushButton {{
        background: {DIM};
        color: {TEXT};
        border: none;
        border-radius: 5px;
        font-size: 11px;
    }}
    QPushButton:hover   {{ background: #484848; }}
    QPushButton:pressed  {{ background: #222222; }}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def _accent_button(label: str, on_click, w=52, h=26) -> QPushButton:
    btn = QPushButton(label)
    btn.setFixedSize(w, h)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {ACCENT};
            color: #000000;
            border: none;
            border-radius: 5px;
            font-size: 11px;
            font-weight: bold;
        }}
        QPushButton:hover   {{ background: {ACCENT_H}; }}
        QPushButton:pressed  {{ background: {ACCENT_P}; color: #ffffff; }}
    """)
    btn.clicked.connect(on_click)
    return btn


def _secondary_button(label: str, on_click, w=72, h=26) -> QPushButton:
    btn = QPushButton(label)
    btn.setFixedSize(w, h)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(_BTN_SECONDARY)
    btn.clicked.connect(on_click)
    return btn


def make_info_card(title: str) -> tuple:
    """Single-line read-only field + Copy. Returns (card, QLineEdit)."""
    card = QGroupBox(title)
    card.setStyleSheet(_CARD_STYLE)

    field = QLineEdit()
    field.setReadOnly(True)
    field.setFont(MONO)
    field.setStyleSheet(f"""
        QLineEdit {{
            background: transparent;
            border: none;
            color: {TEXT};
            padding: 2px 0;
            selection-background-color: {ACCENT};
            selection-color: #000000;
        }}
    """)
    field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    row = QHBoxLayout()
    row.addWidget(field)
    row.addWidget(_accent_button("Copy", lambda: QApplication.clipboard().setText(field.text())))
    card.setLayout(row)
    return card, field


def make_multiline_card(title: str) -> tuple:
    """Multi-line label + Copy. Returns (card, QLabel)."""
    card = QGroupBox(title)
    card.setStyleSheet(_CARD_STYLE)

    label = QLabel("Loading…")
    label.setFont(MONO)
    label.setStyleSheet(f"color: {TEXT}; padding: 2px 0;")
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    label.setWordWrap(True)

    row = QHBoxLayout()
    row.addWidget(label)
    row.addWidget(
        _accent_button("Copy", lambda: QApplication.clipboard().setText(label.text())),
        alignment=Qt.AlignTop
    )
    card.setLayout(row)
    return card, label


# ── Main Window ────────────────────────────────────────────────────────────────

class HWIDWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HWID Info Checker")
        self.setMinimumWidth(600)
        self.resize(660, 860)
        self.setStyleSheet(f"background: {BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {SURFACE};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {DIM};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        self.setCentralWidget(scroll)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        scroll.setWidget(body)

        self._layout = QVBoxLayout(body)
        self._layout.setContentsMargins(28, 24, 28, 24)
        self._layout.setSpacing(6)

        self._build_header()
        self._build_cards()
        self._build_copy_all_btn()
        self._build_error_log()
        self._build_refresh_btn()
        self._build_footer()
        self._layout.addStretch()

        self.load_data()

    # ── Layout builders ────────────────────────────────────────────────────────

    def _build_header(self):
        title = QLabel("HWID Info Checker  —  By BigH")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT};")
        self._layout.addWidget(title)

        sub = QLabel("Hardware identifiers for this machine")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet(f"color: {SUBTEXT}; margin-bottom: 4px;")
        self._layout.addWidget(sub)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {BORDER}; margin: 4px 0;")
        sep.setFixedHeight(1)
        self._layout.addWidget(sep)

    def _build_cards(self):
        disk_card, self.disk_val = make_multiline_card("DISK SERIAL NUMBERS")
        mac_card,  self.mac_val  = make_info_card("MAC ADDRESS")
        mb_card,   self.mb_val   = make_info_card("MOTHERBOARD")
        cpu_card,  self.cpu_val  = make_info_card("CPU ID")
        vol_card,  self.vol_val  = make_multiline_card("VOLUME IDs")

        for card in (disk_card, mac_card, mb_card, cpu_card, vol_card):
            self._layout.addWidget(card)

    def _build_copy_all_btn(self):
        self.copy_all_btn = QPushButton("Copy All")
        self.copy_all_btn.setFixedHeight(32)
        self.copy_all_btn.setCursor(Qt.PointingHandCursor)
        self.copy_all_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE};
                color: {ACCENT};
                border: 1px solid {ACCENT};
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                margin-top: 6px;
            }}
            QPushButton:hover   {{ background: #001a2e; }}
            QPushButton:pressed  {{ background: #002a44; }}
        """)
        self.copy_all_btn.clicked.connect(self._copy_all)
        self._layout.addWidget(self.copy_all_btn)

    def _build_error_log(self):
        log_card = QGroupBox("ERROR LOG")
        log_card.setStyleSheet(_CARD_STYLE)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.log_view.setFixedHeight(88)
        self.log_view.setStyleSheet(f"""
            QTextEdit {{
                background: {SURFACE2};
                color: {ERROR};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 5px;
            }}
        """)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(_accent_button(
            "Copy", lambda: QApplication.clipboard().setText(self.log_view.toPlainText())
        ))
        btn_row.addWidget(_secondary_button("Clear", self._clear_log, w=56))

        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(self.log_view)
        col.addLayout(btn_row)
        log_card.setLayout(col)

        self._layout.addWidget(log_card)

    def _build_refresh_btn(self):
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedHeight(38)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: #000000;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 4px;
            }}
            QPushButton:hover   {{ background: {ACCENT_H}; }}
            QPushButton:pressed  {{ background: {ACCENT_P}; color: #ffffff; }}
            QPushButton:disabled {{ background: {DIM}; color: {SUBTEXT}; }}
        """)
        self.refresh_btn.clicked.connect(self.load_data)
        self._layout.addWidget(self.refresh_btn)

    def _build_footer(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {BORDER}; margin: 6px 0 2px 0;")
        sep.setFixedHeight(1)
        self._layout.addWidget(sep)

        footer = QLabel("By BigH")
        footer.setFont(QFont("Segoe UI", 9))
        footer.setStyleSheet(f"color: {SUBTEXT};")
        footer.setAlignment(Qt.AlignRight)
        self._layout.addWidget(footer)

    # ── Actions ────────────────────────────────────────────────────────────────

    def load_data(self):
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Loading…")
        for w in (self.disk_val, self.vol_val, self.mac_val, self.mb_val, self.cpu_val):
            w.setText("Loading…")

        self._thread = LoaderThread()
        self._thread.done.connect(self._on_data_loaded)
        self._thread.start()

    def _on_data_loaded(self, data: dict):
        self._data = data
        self.disk_val.setText(data["disk"])
        self.mac_val.setText(data["mac"])
        self.mb_val.setText(data["motherboard"])
        self.cpu_val.setText(data["cpu"])
        self.vol_val.setText(data["volume"])
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Refresh")
        self._refresh_log()

    def _copy_all(self):
        d = getattr(self, "_data", {})
        if not d:
            return
        lines = [
            "=== HWID Info ===",
            f"Disk Serial Numbers:\n  {d.get('disk', '').replace(chr(10), chr(10) + '  ')}",
            f"MAC Address:  {d.get('mac', '')}",
            f"Motherboard:  {d.get('motherboard', '')}",
            f"CPU ID:       {d.get('cpu', '')}",
            f"Volume IDs:\n  {d.get('volume', '').replace(chr(10), chr(10) + '  ')}",
            "=================",
        ]
        QApplication.clipboard().setText("\n".join(lines))

    def _refresh_log(self):
        content = read_error_log()
        self.log_view.setPlainText(content if content else "No errors.")

    def _clear_log(self):
        clear_error_log()
        self.log_view.setPlainText("No errors.")
