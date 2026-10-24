import os
import tempfile

LIGHT = {
    "bg": "#f3f5f9",
    "card": "#ffffff",
    "text": "#1b2330",
    "muted": "#6b7686",
    "border": "#e1e6ee",
    "hover": "#eef2f9",
    "accent": "#2563eb",
    "accent_hover": "#1d4fd0",
    "accent_text": "#ffffff",
    "plot1": "#2563eb",
    "plot2": "#e11d48",
    "grid": "#e8ecf3",
    "ok": "#15803d",
    "bad": "#dc2626",
}

DARK = {
    "bg": "#0e1420",
    "card": "#18202f",
    "text": "#e6eaf2",
    "muted": "#8a96aa",
    "border": "#2a3447",
    "hover": "#222c3f",
    "accent": "#3b82f6",
    "accent_hover": "#5b96f8",
    "accent_text": "#ffffff",
    "plot1": "#60a5fa",
    "plot2": "#fb7185",
    "grid": "#263044",
    "ok": "#4ade80",
    "bad": "#f87171",
}


def arrow_icon(c):
    from PyQt5.QtCore import Qt, QPointF
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QPolygonF

    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(c["muted"]))
    painter.drawPolygon(QPolygonF([QPointF(5, 8), QPointF(15, 8), QPointF(10, 13)]))
    painter.end()

    path = os.path.join(tempfile.gettempdir(), f"dsp_arrow_{c['muted'][1:]}.png")
    pixmap.save(path)
    return path.replace("\\", "/")


def stylesheet(c):
    return f"""
    QWidget {{
        color: {c['text']};
        font-size: 10pt;
    }}
    QMainWindow, QDialog, QMessageBox, QInputDialog {{
        background: {c['bg']};
    }}
    QToolTip {{
        background: {c['card']};
        color: {c['text']};
        border: 1px solid {c['border']};
        padding: 4px 6px;
    }}

    QFrame#card {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 14px;
    }}
    QFrame#card[active="true"] {{
        border: 1px solid {c['accent']};
    }}
    QFrame#sidebar {{
        background: {c['card']};
        border-right: 1px solid {c['border']};
    }}
    QFrame#topbar, QFrame#infobar {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    QFrame#segment {{
        background: {c['hover']};
        border-radius: 10px;
    }}
    QWidget#sidebarContent, QScrollArea {{
        background: transparent;
        border: none;
    }}

    QLabel {{
        background: transparent;
    }}
    QLabel#appTitle {{
        font-size: 15pt;
        font-weight: 700;
    }}
    QLabel#cardTitle {{
        font-size: 11pt;
        font-weight: 600;
    }}
    QLabel#sectionLabel {{
        color: {c['muted']};
        font-size: 8pt;
        font-weight: 700;
        padding: 14px 6px 4px 6px;
    }}
    QLabel#muted {{
        color: {c['muted']};
        font-size: 9pt;
    }}

    QPushButton {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 7px 12px;
        text-align: left;
    }}
    QPushButton:hover {{
        background: {c['hover']};
    }}
    QPushButton:pressed {{
        background: {c['border']};
    }}
    QPushButton:disabled {{
        color: {c['muted']};
        background: transparent;
    }}
    QPushButton#primary {{
        background: {c['accent']};
        color: {c['accent_text']};
        font-weight: 600;
        text-align: center;
        padding: 9px 12px;
    }}
    QPushButton#primary:hover {{
        background: {c['accent_hover']};
    }}
    QPushButton#tool {{
        border: 1px solid {c['border']};
        padding: 3px 9px;
        font-size: 9pt;
        text-align: center;
    }}
    QPushButton#tool:checked {{
        background: {c['accent']};
        color: {c['accent_text']};
        border-color: {c['accent']};
    }}
    QPushButton#seg {{
        padding: 6px 16px;
        text-align: center;
        margin: 3px;
    }}
    QPushButton#seg:checked {{
        background: {c['card']};
        color: {c['accent']};
    }}
    QPushButton#seg:disabled {{
        color: {c['muted']};
    }}
    QPushButton#ghost {{
        border: 1px solid {c['border']};
        text-align: center;
    }}

    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 6px 10px;
        selection-background-color: {c['accent']};
    }}
    QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {{
        border: 1px solid {c['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 26px;
    }}
    QComboBox::down-arrow {{
        image: url({arrow_icon(c)});
        width: 14px;
        height: 14px;
        margin-right: 8px;
    }}
    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
        width: 0;
        border: none;
    }}
    QDialogButtonBox QPushButton {{
        border: 1px solid {c['border']};
        text-align: center;
        min-width: 72px;
        padding: 6px 14px;
    }}
    QDialogButtonBox QPushButton:default {{
        background: {c['accent']};
        color: {c['accent_text']};
        border-color: {c['accent']};
        font-weight: 600;
    }}
    QComboBox QAbstractItemView {{
        background: {c['card']};
        border: 1px solid {c['border']};
        selection-background-color: {c['accent']};
        selection-color: {c['accent_text']};
        outline: none;
    }}

    QMenuBar {{
        background: {c['card']};
        border-bottom: 1px solid {c['border']};
        padding: 2px 6px;
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 6px 10px;
        border-radius: 6px;
    }}
    QMenuBar::item:selected {{
        background: {c['hover']};
    }}
    QMenu {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 6px 26px 6px 12px;
        border-radius: 6px;
    }}
    QMenu::item:selected {{
        background: {c['accent']};
        color: {c['accent_text']};
    }}
    QMenu::item:disabled {{
        color: {c['muted']};
    }}
    QMenu::separator {{
        height: 1px;
        background: {c['border']};
        margin: 5px 8px;
    }}

    QStatusBar {{
        background: {c['card']};
        border-top: 1px solid {c['border']};
        color: {c['muted']};
    }}

    QTableWidget {{
        background: {c['card']};
        alternate-background-color: {c['hover']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        gridline-color: {c['border']};
    }}
    QHeaderView::section {{
        background: {c['hover']};
        color: {c['muted']};
        font-weight: 600;
        border: none;
        padding: 6px;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['border']};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['muted']};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        height: 0;
        width: 0;
    }}
    """


def style_axes(ax, c):
    ax.figure.set_facecolor(c["card"])
    ax.set_facecolor(c["card"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["border"])
    ax.tick_params(colors=c["muted"], labelsize=9, length=3)
    ax.xaxis.label.set_color(c["muted"])
    ax.yaxis.label.set_color(c["muted"])
    ax.title.set_color(c["text"])
    ax.grid(True, color=c["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
