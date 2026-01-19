from __future__ import annotations

import json
import os
import random
import string
from dataclasses import replace
from pathlib import Path
from typing import Optional

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QTimer,
    Qt,
    QParallelAnimationGroup,
)
from PySide6.QtGui import QAction, QColor, QIcon, QKeySequence, QPainter, QPixmap, QPen, QKeySequence
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from password_strength_checker.core.evaluate import evaluate
from password_strength_checker.core.models import Policy


APPLE_QSS = """
QMainWindow { background: #F5F5F7; }
QWidget { color: #111827; font-size: 13px; font-family: -apple-system, "SF Pro Display", "SF Pro Text", "Segoe UI", Arial; }

QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
}

QLabel#Title { font-size: 18px; font-weight: 800; }
QLabel#Muted { color: #6B7280; }

QLineEdit, QTextEdit, QComboBox, QSpinBox, QTableWidget {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 10px;
    selection-background-color: #DBEAFE;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #3B82F6; }

QPushButton, QToolButton {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 10px 12px;
    font-weight: 700;
}
QPushButton:hover, QToolButton:hover { background: #F9FAFB; }
QPushButton:pressed, QToolButton:pressed { background: #F3F4F6; }

QPushButton#Primary {
    background: #2563EB;
    border: 1px solid #2563EB;
    color: white;
}
QPushButton#Primary:hover { background: #1D4ED8; border-color: #1D4ED8; }

QPushButton#Danger {
    background: #FFFFFF;
    border: 1px solid #FCA5A5;
    color: #991B1B;
}
QPushButton#Danger:hover { background: #FEF2F2; }

QCheckBox { spacing: 10px; color: #111827; }
QCheckBox::indicator { width: 16px; height: 16px; }

QProgressBar {
    border: 1px solid #E5E7EB;
    border-radius: 999px;
    text-align: center;
    background: #F3F4F6;
    height: 18px;
    font-weight: 700;
    color: #111827;
}
QProgressBar::chunk {
    border-radius: 999px;
    background: #3B82F6;
}

QTabWidget::pane {
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    background: #FFFFFF;
    padding: 10px;
    top: -1px;
}
QTabBar::tab {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    padding: 10px 14px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    margin-right: 6px;
    color: #111827;
    font-weight: 700;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    border-bottom-color: #FFFFFF;
}

QLabel#PillOk {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    color: #065F46;
    padding: 6px 10px;
    border-radius: 999px;
    font-weight: 800;
}
QLabel#PillNo {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    color: #991B1B;
    padding: 6px 10px;
    border-radius: 999px;
    font-weight: 800;
}

/* Icon buttons (mac-like) */
QToolButton#IconBtn {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 8px;
}
QToolButton#IconBtn:hover { background: #F9FAFB; }
QToolButton#IconBtn:pressed { background: #F3F4F6; }

/* Toast */
QFrame#Toast {
    background: rgba(17, 24, 39, 235);
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 14px;
}
QLabel#ToastText {
    color: white;
    font-weight: 700;
    padding: 10px 12px;
}

/* Filters */
QLineEdit#FilterBox {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 13px;
}
QComboBox#SevCombo {
  padding: 10px 12px;
  border-radius: 12px;
}

/* Table readability */
QTableWidget {
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  background: #FFFFFF;
  gridline-color: transparent;
  font-size: 13px;
  alternate-background-color: #FBFDFF;
}
QHeaderView::section {
  background: #F9FAFB;
  border: none;
  border-bottom: 1px solid #E5E7EB;
  padding: 12px 10px;
  font-size: 13px;
  font-weight: 900;
  color: #111827;
}
QTableWidget::item {
  padding: 12px 10px;
  border-bottom: 1px solid #EEF2F7;
}
QTableWidget::item:selected {
  background: #DBEAFE;
  color: #111827;
}

/* Bigger scrollbars */
QScrollBar:vertical {
  width: 12px;
  background: transparent;
  margin: 6px 4px 6px 0px;
}
QScrollBar::handle:vertical {
  background: #D1D5DB;
  border-radius: 6px;
  min-height: 28px;
}
QScrollBar::handle:vertical:hover { background: #9CA3AF; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""


SVG_COPY = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none">
  <path d="M9 9h10v10H9V9Z" stroke="CURRENT" stroke-width="2" stroke-linejoin="round"/>
  <path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"
        stroke="CURRENT" stroke-width="2" stroke-linecap="round"/>
</svg>
"""

SVG_EXPORT = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none">
  <path d="M12 3v10" stroke="CURRENT" stroke-width="2" stroke-linecap="round"/>
  <path d="M8 7l4-4 4 4" stroke="CURRENT" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" stroke="CURRENT" stroke-width="2" stroke-linecap="round"/>
</svg>
"""


def svg_icon(svg: str, size: int = 18, color: str = "#111827") -> QIcon:
    svg = svg.replace("CURRENT", color)
    renderer = QSvgRenderer(bytearray(svg, encoding="utf-8"))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    renderer.render(p)
    p.end()
    return QIcon(pm)


def score_color(score: int) -> str:
    if score < 30:
        return "#EF4444"
    if score < 50:
        return "#F97316"
    if score < 70:
        return "#EAB308"
    if score < 85:
        return "#22C55E"
    return "#06B6D4"


def generate_strong_password(length: int = 18) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.?"
    base = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()-_=+[]{};:,.?"),
    ]
    while len(base) < length:
        base.append(random.choice(chars))
    random.shuffle(base)
    return "".join(base)


def generate_passphrase(words: int = 4) -> str:
    syll = ["ra", "ko", "mi", "ta", "lu", "zen", "phi", "no", "ka", "tri", "so", "ve", "di", "mon", "shi"]
    parts = []
    for _ in range(words):
        w = "".join(random.choice(syll) for _ in range(random.randint(2, 3)))
        parts.append(w)
    sep = random.choice(["-", " "])
    tail = random.choice(["", "", f"{random.randint(10, 99)}", f"!{random.randint(10, 99)}"])
    return sep.join(parts) + tail


def add_shadow(w: QWidget, blur: int = 22, y: int = 8, alpha: int = 25) -> None:
    sh = QGraphicsDropShadowEffect(w)
    sh.setBlurRadius(blur)
    sh.setOffset(0, y)
    sh.setColor(QColor(0, 0, 0, alpha))
    w.setGraphicsEffect(sh)


class Card(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


class ScoreRing(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        self.setFixedSize(64, 64)

    def set_value(self, v: int) -> None:
        self._value = max(0, min(100, int(v)))
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self.rect().adjusted(6, 6, -6, -6)

        pen = QPen(QColor("#E5E7EB"), 6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(r, 0, 360 * 16)

        col = QColor(score_color(self._value))
        pen2 = QPen(col, 6)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen2)
        span = int(-360 * 16 * (self._value / 100))
        p.drawArc(r, 90 * 16, span)

        p.setPen(QColor("#111827"))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self._value))
        p.end()


class Toast(QFrame):
    def __init__(self, parent: QWidget, text: str) -> None:
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(text)
        lbl.setObjectName("ToastText")
        layout.addWidget(lbl)

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

        self.anim_in = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim_in.setDuration(180)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_out = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim_out.setDuration(220)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_out.finished.connect(self.close)

        self.anim_pos = QPropertyAnimation(self, b"pos", self)
        self.anim_pos.setDuration(220)
        self.anim_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

    def show_bottom_right(self, margin: int = 18) -> None:
        self.adjustSize()
        parent = self.parentWidget()
        if not parent:
            return
        pr = parent.rect()
        x = pr.right() - self.width() - margin
        y = pr.bottom() - self.height() - margin

        end = parent.mapToGlobal(QPoint(x, y))
        start = parent.mapToGlobal(QPoint(x + 14, y + 14))

        self.move(start)
        self.show()

        self.anim_pos.setStartValue(start)
        self.anim_pos.setEndValue(end)

        self.anim_in.start()
        self.anim_pos.start()
        QTimer.singleShot(1200, self.anim_out.start)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Password Strength Checker")
        self.resize(1200, 860)

        self._policy_path: Optional[Path] = None
        self._loaded_policy: Policy = Policy()
        self._last_result_json: str = ""

        self._setup_menu()

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        # ---------------- Top bar ----------------
        top = Card()
        add_shadow(top)
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(16, 14, 16, 14)
        top_l.setSpacing(12)

        title = QLabel("Password Strength Checker")
        title.setObjectName("Title")
        top_l.addWidget(title, 1)

        self.pill = QLabel("—")
        self.pill.setObjectName("PillNo")
        top_l.addWidget(self.pill)

        self.policy_label = QLabel("Policy: défaut")
        self.policy_label.setObjectName("Muted")
        top_l.addWidget(self.policy_label)

        layout.addWidget(top)

        # ---------------- Input card ----------------
        input_card = Card()
        add_shadow(input_card)
        ic = QGridLayout(input_card)
        ic.setContentsMargins(16, 16, 16, 16)
        ic.setHorizontalSpacing(12)
        ic.setVerticalSpacing(12)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Tape un mot de passe… (local uniquement)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setText("Afficher")
        self.toggle_btn.setCheckable(True)

        self.eval_btn = QPushButton("Évaluer")
        self.eval_btn.setObjectName("Primary")

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("Danger")

        self.strict_cb = QCheckBox("Strict (WARNING => non conforme)")

        self.load_policy_btn = QPushButton("Charger policy.json")
        self.save_policy_btn = QPushButton("Sauver policy.json")
        self.save_policy_btn.setEnabled(False)

        self.gen_pass_btn = QPushButton("Passphrase")
        self.gen_pwd_btn = QPushButton("Password")
        self.gen_len_sb = QSpinBox()
        self.gen_len_sb.setRange(8, 64)
        self.gen_len_sb.setValue(18)

        ic.addWidget(QLabel("Mot de passe"), 0, 0)
        ic.addWidget(self.password_input, 0, 1, 1, 5)
        ic.addWidget(self.toggle_btn, 0, 6)

        ic.addWidget(self.eval_btn, 1, 1, 1, 3)
        ic.addWidget(self.clear_btn, 1, 4, 1, 3)

        ic.addWidget(self.strict_cb, 2, 1, 1, 6)

        ic.addWidget(self.load_policy_btn, 3, 1, 1, 2)
        ic.addWidget(self.save_policy_btn, 3, 3, 1, 2)

        ic.addWidget(QLabel("Len"), 3, 5)
        ic.addWidget(self.gen_len_sb, 3, 6)
        ic.addWidget(self.gen_pass_btn, 4, 5, 1, 1)
        ic.addWidget(self.gen_pwd_btn, 4, 6, 1, 1)

        layout.addWidget(input_card)

        # ---------------- Score card ----------------
        score_card = Card()
        add_shadow(score_card)
        sc = QVBoxLayout(score_card)
        sc.setContentsMargins(16, 16, 16, 16)
        sc.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        self.ring = ScoreRing()
        top_row.addWidget(self.ring)

        text_col = QVBoxLayout()
        self.score_title = QLabel("Score: - / 100  •  Niveau: -")
        self.score_title.setStyleSheet("font-size: 14px; font-weight: 900;")
        text_col.addWidget(self.score_title)

        self.best_est = QLabel("Résistance (slow hash): -")
        self.best_est.setObjectName("Muted")
        text_col.addWidget(self.best_est)

        top_row.addLayout(text_col, 1)
        sc.addLayout(top_row)

        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        self.score_bar.setValue(0)
        sc.addWidget(self.score_bar)

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setFixedHeight(104)
        self.summary.setPlaceholderText("Résumé…")
        sc.addWidget(self.summary)

        layout.addWidget(score_card)

        # ---------------- Tabs ----------------
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        # Diagnostics tab
        diag = QWidget()
        dl = QVBoxLayout(diag)
        dl.setContentsMargins(14, 14, 14, 14)
        dl.setSpacing(12)

        filt_row = QHBoxLayout()
        self.findings_filter = QLineEdit()
        self.findings_filter.setObjectName("FilterBox")
        self.findings_filter.setPlaceholderText("Filtrer (code, message)…")

        self.sev_filter = QComboBox()
        self.sev_filter.setObjectName("SevCombo")
        self.sev_filter.addItems(["Tous", "critical", "warning", "info"])

        self.hide_info_cb = QCheckBox("Masquer INFO")

        filt_row.addWidget(self.findings_filter, 1)
        filt_row.addWidget(QLabel("Sévérité"))
        filt_row.addWidget(self.sev_filter)
        filt_row.addWidget(self.hide_info_cb)
        dl.addLayout(filt_row)

        self.findings_table = QTableWidget(0, 4)
        self.findings_table.setHorizontalHeaderLabels(["Sévérité", "Code", "Message", "Impact"])
        self.findings_table.setSortingEnabled(True)
        self.findings_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.findings_table.setShowGrid(False)
        self.findings_table.verticalHeader().setVisible(False)
        self.findings_table.setAlternatingRowColors(True)
        self.findings_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.findings_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.findings_table.setWordWrap(True)
        self.findings_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.findings_table.cellDoubleClicked.connect(self._copy_cell)

        self.findings_table.verticalHeader().setDefaultSectionSize(44)
        self.findings_table.horizontalHeader().setMinimumHeight(44)
        self.findings_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        hh = self.findings_table.horizontalHeader()
        hh.setStretchLastSection(False)
        hh.setSectionResizeMode(0, hh.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, hh.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, hh.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, hh.ResizeMode.ResizeToContents)

        dl.addWidget(self.findings_table, 1)
        self.tabs.addTab(diag, "Diagnostics")

        # Estimates tab
        est = QWidget()
        el = QVBoxLayout(est)
        el.setContentsMargins(14, 14, 14, 14)
        el.setSpacing(12)

        self.estimates_table = QTableWidget(0, 3)
        self.estimates_table.setHorizontalHeaderLabels(["Scénario", "Essais/s", "Temps"])
        self.estimates_table.setSortingEnabled(True)
        self.estimates_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.estimates_table.setShowGrid(False)
        self.estimates_table.verticalHeader().setVisible(False)
        self.estimates_table.setAlternatingRowColors(True)
        self.estimates_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.estimates_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.estimates_table.setWordWrap(True)
        self.estimates_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.estimates_table.cellDoubleClicked.connect(self._copy_cell)

        self.estimates_table.verticalHeader().setDefaultSectionSize(44)
        self.estimates_table.horizontalHeader().setMinimumHeight(44)
        self.estimates_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        eh = self.estimates_table.horizontalHeader()
        eh.setSectionResizeMode(0, eh.ResizeMode.Stretch)
        eh.setSectionResizeMode(1, eh.ResizeMode.ResizeToContents)
        eh.setSectionResizeMode(2, eh.ResizeMode.ResizeToContents)

        el.addWidget(self.estimates_table, 1)
        self.tabs.addTab(est, "Estimates")

        # Recos tab
        reco = QWidget()
        rl = QVBoxLayout(reco)
        rl.setContentsMargins(14, 14, 14, 14)
        rl.setSpacing(12)

        btns = QHBoxLayout()
        self.export_report_btn = QToolButton()
        self.export_report_btn.setObjectName("IconBtn")
        self.export_report_btn.setIcon(svg_icon(SVG_EXPORT, 18))
        self.export_report_btn.setToolTip("Exporter report.json")

        self.copy_reco_btn = QToolButton()
        self.copy_reco_btn.setObjectName("IconBtn")
        self.copy_reco_btn.setIcon(svg_icon(SVG_COPY, 18))
        self.copy_reco_btn.setToolTip("Copier recommandations")

        btns.addStretch(1)
        btns.addWidget(self.export_report_btn)
        btns.addWidget(self.copy_reco_btn)
        rl.addLayout(btns)

        self.reco_text = QTextEdit()
        self.reco_text.setReadOnly(True)
        rl.addWidget(self.reco_text, 1)

        self.tabs.addTab(reco, "Recommandations")

        # JSON tab
        js = QWidget()
        jl = QVBoxLayout(js)
        jl.setContentsMargins(14, 14, 14, 14)
        jl.setSpacing(12)

        jtop = QHBoxLayout()
        jtop.addStretch(1)

        self.copy_json_btn = QToolButton()
        self.copy_json_btn.setObjectName("IconBtn")
        self.copy_json_btn.setIcon(svg_icon(SVG_COPY, 18))
        self.copy_json_btn.setToolTip("Copier JSON")
        jtop.addWidget(self.copy_json_btn)

        jl.addLayout(jtop)

        self.json_text = QTextEdit()
        self.json_text.setReadOnly(True)
        jl.addWidget(self.json_text, 1)

        self.tabs.addTab(js, "JSON")

        # ---------------- Debounce + signals ----------------
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(220)
        self._debounce.timeout.connect(self.run_evaluate)

        self.toggle_btn.toggled.connect(self._toggle_password_visibility)
        self.eval_btn.clicked.connect(self.run_evaluate)
        self.clear_btn.clicked.connect(self._clear)
        self.load_policy_btn.clicked.connect(self._choose_policy)
        self.save_policy_btn.clicked.connect(self._save_policy)

        self.gen_pass_btn.clicked.connect(self._gen_passphrase)
        self.gen_pwd_btn.clicked.connect(self._gen_password)

        self.copy_reco_btn.clicked.connect(self._copy_recos)
        self.copy_json_btn.clicked.connect(self._copy_json)
        self.export_report_btn.clicked.connect(self._export_report)

        self.password_input.textChanged.connect(lambda *_: self._debounce.start())
        self.findings_filter.textChanged.connect(lambda *_: self._debounce.start())

        self.sev_filter.currentIndexChanged.connect(lambda *_: self._debounce.start())
        self.hide_info_cb.toggled.connect(lambda *_: self._debounce.start())
        self.strict_cb.toggled.connect(lambda *_: self._debounce.start())

        # Spotlight Ctrl+K (focus filter)
        act_spot = QAction("Focus Search", self)
        act_spot.setShortcut(QKeySequence("Ctrl+K"))
        act_spot.triggered.connect(lambda: (self.tabs.setCurrentIndex(0), self.findings_filter.setFocus()))
        self.addAction(act_spot)

        # Tab animations
        self._last_tab_index = self.tabs.currentIndex()
        self._tabs_stack: Optional[QStackedWidget] = self.tabs.findChild(QStackedWidget)
        self.tabs.currentChanged.connect(self._animate_tab_change)

        self.run_evaluate()

    def _setup_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Fichier")

        act_open = QAction("Charger policy…", self)
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self._choose_policy)
        file_menu.addAction(act_open)

        act_save = QAction("Sauver policy…", self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self._save_policy)
        file_menu.addAction(act_save)

        file_menu.addSeparator()

        act_export = QAction("Exporter report…", self)
        act_export.setShortcut(QKeySequence("Ctrl+E"))
        act_export.triggered.connect(self._export_report)
        file_menu.addAction(act_export)

        file_menu.addSeparator()

        act_quit = QAction("Quitter", self)
        act_quit.setShortcut(QKeySequence.Quit)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

    def _toast(self, msg: str) -> None:
        Toast(self, msg).show_bottom_right()

    def _copy_cell(self, row: int, col: int) -> None:
        table = self.sender()
        if not isinstance(table, QTableWidget):
            return
        item = table.item(row, col)
        if not item:
            return
        QApplication.clipboard().setText(item.text())
        self._toast("Copié")

    def _get_open_json_path(self) -> Optional[Path]:
        # Native dialog (system) => always readable + no stylesheet issues
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir policy.json",
            "",
            "JSON (*.json)",
            options=QFileDialog.Option.DontUseCustomDirectoryIcons,
        )
        return Path(path_str) if path_str else None

    def _get_save_json_path(self, default_name: str) -> Optional[Path]:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Sauver fichier",
            default_name,
            "JSON (*.json)",
            options=QFileDialog.Option.DontUseCustomDirectoryIcons,
        )
        return Path(path_str) if path_str else None

    def _animate_tab_change(self, index: int) -> None:
        if not self._tabs_stack:
            return
        w = self._tabs_stack.currentWidget()
        if not w:
            return

        direction = 1 if index > self._last_tab_index else -1
        self._last_tab_index = index

        eff = QGraphicsOpacityEffect(w)
        w.setGraphicsEffect(eff)
        eff.setOpacity(0.0)

        fade = QPropertyAnimation(eff, b"opacity", self)
        fade.setDuration(180)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        start_pos = w.pos() + QPoint(22 * direction, 0)
        end_pos = w.pos()
        w.move(start_pos)

        slide = QPropertyAnimation(w, b"pos", self)
        slide.setDuration(200)
        slide.setStartValue(start_pos)
        slide.setEndValue(end_pos)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade)
        group.addAnimation(slide)

        def cleanup() -> None:
            w.setGraphicsEffect(None)

        group.finished.connect(cleanup)
        group.start()

    def _toggle_password_visibility(self, checked: bool) -> None:
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
        self.toggle_btn.setText("Masquer" if checked else "Afficher")

    def _clear(self) -> None:
        self.password_input.clear()
        self._toast("Champ effacé")

    def _gen_passphrase(self) -> None:
        self.password_input.setText(generate_passphrase(4))
        self._toast("Passphrase générée")

    def _gen_password(self) -> None:
        self.password_input.setText(generate_strong_password(int(self.gen_len_sb.value())))
        self._toast("Mot de passe généré")

    def _copy_recos(self) -> None:
        QApplication.clipboard().setText(self.reco_text.toPlainText())
        self._toast("Recommandations copiées")

    def _copy_json(self) -> None:
        QApplication.clipboard().setText(self._last_result_json or self.json_text.toPlainText())
        self._toast("JSON copié")

    def _choose_policy(self) -> None:
        path = self._get_open_json_path()
        if not path:
            return
        self._load_policy_path(path)

    def _load_policy_path(self, path: Path) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            allowed = {
                "min_length",
                "strong_length",
                "forbid_sequences_len",
                "max_repeated_run",
                "forbid_dictionary",
                "min_classes",
                "banned_words",
                "enabled_rules",
            }
            cleaned = {k: v for k, v in data.items() if k in allowed}
            self._loaded_policy = replace(Policy(), **cleaned)
            self._policy_path = path
            self.policy_label.setText(f"Policy: {path.name}")
            self.save_policy_btn.setEnabled(True)
            self._toast("Policy chargée")
            self.run_evaluate()
        except Exception as e:
            QMessageBox.critical(self, "Erreur policy.json", f"Impossible de charger la policy:\n{e}")

    def _save_policy(self) -> None:
        policy = self._loaded_policy
        default_name = self._policy_path.name if self._policy_path else "policy.json"
        path = self._get_save_json_path(default_name)
        if not path:
            return

        try:
            payload = {
                "min_length": policy.min_length,
                "strong_length": policy.strong_length,
                "min_classes": getattr(policy, "min_classes", 3),
                "forbid_dictionary": policy.forbid_dictionary,
                "forbid_sequences_len": policy.forbid_sequences_len,
                "max_repeated_run": policy.max_repeated_run,
                "banned_words": getattr(policy, "banned_words", []),
                "enabled_rules": getattr(policy, "enabled_rules", {}),
            }
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            self._policy_path = path
            self.policy_label.setText(f"Policy: {path.name}")
            self.save_policy_btn.setEnabled(True)
            self._toast("Policy sauvegardée")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder:\n{e}")

    def _export_report(self) -> None:
        if not self._last_result_json:
            QMessageBox.information(self, "Info", "Aucun résultat à exporter.")
            return
        path = self._get_save_json_path("report.json")
        if not path:
            return
        try:
            path.write_text(self._last_result_json, encoding="utf-8")
            self._toast("Report exporté")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'exporter:\n{e}")

    def _set_findings(self, findings) -> None:
        was_sorting = self.findings_table.isSortingEnabled()
        self.findings_table.setSortingEnabled(False)

        self.findings_table.setRowCount(0)
        for f in findings:
            row = self.findings_table.rowCount()
            self.findings_table.insertRow(row)

            it0 = QTableWidgetItem(f.severity.value)
            it1 = QTableWidgetItem(f.code)
            it2 = QTableWidgetItem(f.message)
            it3 = QTableWidgetItem(str(f.penalty))

            if f.severity.value == "critical":
                bg = QColor("#FEF2F2")
            elif f.severity.value == "warning":
                bg = QColor("#FFFBEB")
            else:
                bg = QColor("#FFFFFF")

            for it in (it0, it1, it2, it3):
                it.setBackground(bg)

            self.findings_table.setItem(row, 0, it0)
            self.findings_table.setItem(row, 1, it1)
            self.findings_table.setItem(row, 2, it2)
            self.findings_table.setItem(row, 3, it3)

        self.findings_table.resizeRowsToContents()
        self.findings_table.setSortingEnabled(was_sorting)

    def _set_estimates(self, estimates: list[dict[str, object]]) -> None:
        was_sorting = self.estimates_table.isSortingEnabled()
        self.estimates_table.setSortingEnabled(False)

        self.estimates_table.setRowCount(0)
        for e in estimates:
            row = self.estimates_table.rowCount()
            self.estimates_table.insertRow(row)
            self.estimates_table.setItem(row, 0, QTableWidgetItem(str(e.get("scenario", ""))))
            self.estimates_table.setItem(row, 1, QTableWidgetItem(str(e.get("guesses_per_second", ""))))
            self.estimates_table.setItem(row, 2, QTableWidgetItem(str(e.get("time", ""))))

        self.estimates_table.resizeRowsToContents()
        self.estimates_table.setSortingEnabled(was_sorting)

    def run_evaluate(self) -> None:
        pw = self.password_input.text()
        result = evaluate(pw, policy=self._loaded_policy)

        non_compliant = any(f.severity.value == "critical" for f in result.findings)
        if self.strict_cb.isChecked():
            non_compliant = non_compliant or any(f.severity.value == "warning" for f in result.findings)

        if non_compliant:
            self.pill.setObjectName("PillNo")
            self.pill.setText("❌ Non conforme")
        else:
            self.pill.setObjectName("PillOk")
            self.pill.setText("✅ Conforme")
        self.pill.setStyleSheet("")

        score = int(result.score)
        self.ring.set_value(score)

        self.score_title.setText(f"Score: {score} / 100  •  Niveau: {result.label}")
        self.score_bar.setValue(score)
        col = score_color(score)
        self.score_bar.setStyleSheet(f"QProgressBar::chunk {{ background: {col}; border-radius: 999px; }}")

        estimates = getattr(result, "estimates", []) or []
        best = "-"
        for e in estimates:
            if "slow hash" in str(e.get("scenario", "")).lower():
                best = str(e.get("time", "-"))
                break
        self.best_est.setText(f"Résistance (slow hash): {best}")

        criticals = [f for f in result.findings if f.severity.value == "critical"]
        warnings = [f for f in result.findings if f.severity.value == "warning"]

        if not pw:
            self.summary.setPlainText("• Entre un mot de passe pour obtenir une évaluation.")
        else:
            lines: list[str] = []
            if criticals:
                lines.append(f"• Problèmes critiques: {len(criticals)}")
            if warnings:
                lines.append(f"• Avertissements: {len(warnings)}")
            if not criticals and not warnings:
                lines.append("• Aucun problème majeur détecté.")
            for f in (criticals[:2] + warnings[:2]):
                lines.append(f"• {f.code}: {f.message}")
            self.summary.setPlainText("\n".join(lines))

        text = self.findings_filter.text().strip().lower()
        sev_pick = self.sev_filter.currentText()
        hide_info = self.hide_info_cb.isChecked()

        filtered = []
        for f in result.findings:
            if hide_info and f.severity.value == "info":
                continue
            if sev_pick != "Tous" and f.severity.value != sev_pick:
                continue
            hay = f"{f.severity.value} {f.code} {f.message}".lower()
            if text and text not in hay:
                continue
            filtered.append(f)

        self._set_findings(filtered)
        self._set_estimates(estimates)

        self.reco_text.setPlainText("\n".join(f"- {r}" for r in result.recommendations))
        self._last_result_json = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        self.json_text.setPlainText(self._last_result_json)


def main() -> None:
    # --- Fix cursor/scale issues (Wayland/HiDPI) ---
    os.environ.setdefault("QT_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication([])
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app.setStyleSheet(APPLE_QSS)
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
