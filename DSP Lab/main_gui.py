import sys
import os
import math
import importlib
import numpy as np
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QAction, QFileDialog, QInputDialog, QMessageBox,
                             QLabel, QFrame, QPushButton, QButtonGroup, QComboBox, QScrollArea,
                             QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import dsp_logic
import gui_theme

ROOT = os.path.dirname(os.path.abspath(__file__))
TASK1_DIR = os.path.join(ROOT, "Labs", "Task1 files+test-20260930T203736Z-1-001")
QUAN_DIR = os.path.join(ROOT, "Quantization-20261011T152410Z-1-001", "Quantization")
TASK4_DIR = os.path.join(ROOT, "Labs", "Task & Files-20261024T083112Z-1-001", "Task & Files")
COMPARE_DIR = os.path.join(TASK4_DIR, "Test Cases-20261024T083237Z-1-001", "Test Cases")
DC_DIR = os.path.join(TASK4_DIR, "Remove DC component-20261024T083221Z-1-001", "Remove DC component")

STEM_LIMIT = 300
HISTORY_LIMIT = 30
FILE_FILTER = "Text Files (*.txt);;All Files (*)"

SECTIONS = [
    ("Signals", ["load", "save"]),
    ("Arithmetic", ["add", "sub", "add_files", "mul", "square", "norm", "acc"]),
    ("Quantization", ["quant"]),
    ("Frequency Domain", ["dft", "dominant", "modify", "remove_dc", "idft", "load_freq", "save_freq"]),
]


def load_module(folder, name):
    if folder not in sys.path:
        sys.path.insert(0, folder)
    return importlib.import_module(name)


def run_task1():
    return load_module(TASK1_DIR, "Task1Test").run_all_tests()

def run_quan1():
    return [("Quantization Test 1 (Bits = 3)", load_module(QUAN_DIR, "QuanTest1").run_test1())]

def run_quan2():
    return [("Quantization Test 2 (Levels = 4)", load_module(QUAN_DIR, "QuanTest2").run_test2())]

def run_dft():
    return [("DFT - Amplitude & Phase", load_module(COMPARE_DIR, "signalcompare").run_dft_test())]

def run_idft():
    return [("IDFT - Reconstruction", load_module(COMPARE_DIR, "signalcompare").run_idft_test())]

def run_dc():
    return [("Remove DC Component", load_module(DC_DIR, "CompareSignals").run_dc_test())]


TEST_SUITES = [
    ("Task 1 Tests", run_task1),
    ("Quantization Test 1 (Bits = 3)", run_quan1),
    ("Quantization Test 2 (Levels = 4)", run_quan2),
    ("DFT Test", run_dft),
    ("IDFT Test", run_idft),
    ("Remove DC Test", run_dc),
]


class PlotCard(QFrame):
    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("card")
        self.setAcceptDrops(True)
        self.home = None

        self.fig = Figure(figsize=(5, 4), dpi=100, layout="constrained")
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumSize(300, 240)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.hide()

        self.title = QLabel()
        self.title.setObjectName("cardTitle")
        self.info = QLabel()
        self.info.setObjectName("muted")
        self.title.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.info.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        self.zoom_btn = self.make_tool("Zoom", "Drag a rectangle on the plot to zoom in", True)
        self.pan_btn = self.make_tool("Pan", "Drag the plot to move around", True)
        reset_btn = self.make_tool("Reset", "Restore the original view")
        save_btn = self.make_tool("Save PNG", "Save this plot as an image")
        self.zoom_btn.clicked.connect(self.toggle_zoom)
        self.pan_btn.clicked.connect(self.toggle_pan)
        reset_btn.clicked.connect(self.reset_view)
        save_btn.clicked.connect(self.save_image)

        titles = QVBoxLayout()
        titles.setSpacing(0)
        titles.addWidget(self.title)
        titles.addWidget(self.info)

        tools = QHBoxLayout()
        tools.setSpacing(6)
        tools.addStretch()
        for button in (self.zoom_btn, self.pan_btn, reset_btn, save_btn):
            tools.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.addLayout(titles)
        layout.addWidget(self.canvas, 1)
        layout.addLayout(tools)

    def make_tool(self, text, tip, checkable=False):
        button = QPushButton(text)
        button.setObjectName("tool")
        button.setToolTip(tip)
        button.setCheckable(checkable)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def mode_name(self):
        mode = self.toolbar.mode
        return getattr(mode, "name", str(mode))

    def sync_tools(self):
        mode = self.mode_name()
        self.zoom_btn.setChecked(mode == "ZOOM")
        self.pan_btn.setChecked(mode == "PAN")

    def toggle_zoom(self):
        if self.mode_name() == "PAN":
            self.toolbar.pan()
        self.toolbar.zoom()
        self.sync_tools()

    def toggle_pan(self):
        if self.mode_name() == "ZOOM":
            self.toolbar.zoom()
        self.toolbar.pan()
        self.sync_tools()

    def reset_view(self):
        if self.home is None:
            return
        self.ax.set_xlim(self.home[0])
        self.ax.set_ylim(self.home[1])
        self.canvas.draw_idle()

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "plot.png", "PNG Image (*.png);;SVG Image (*.svg)")
        if path:
            self.fig.savefig(path, dpi=200, facecolor=self.fig.get_facecolor())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                self.file_dropped.emit(path)
                break

    def finish(self, c):
        gui_theme.style_axes(self.ax, c)
        self.home = (self.ax.get_xlim(), self.ax.get_ylim())
        self.canvas.draw_idle()

    def show_empty(self, message, c):
        self.ax.clear()
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.text(0.5, 0.5, message, transform=self.ax.transAxes, ha="center", va="center",
                     color=c["muted"], fontsize=11, linespacing=1.7)
        gui_theme.style_axes(self.ax, c)
        self.ax.grid(False)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.home = None
        self.canvas.draw_idle()

    def show_time(self, x, y, discrete, c, color_key):
        ax = self.ax
        ax.clear()
        x = np.asarray(x)
        y = np.asarray(y, dtype=float)
        color = c[color_key]
        as_stems = discrete and len(x) <= STEM_LIMIT
        if as_stems:
            ax.vlines(x, 0, y, colors=color, linewidth=1.6)
            ax.plot(x, y, "o", color=color, markersize=5)
            ax.axhline(0, color=c["muted"], linewidth=0.8)
        else:
            ax.plot(x, y, color=color, linewidth=2)
        ax.set_xlabel("Index (n)")
        ax.set_ylabel("Amplitude")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.margins(x=0.04, y=0.12)
        self.finish(c)
        return as_stems

    def show_amplitude(self, freqs, normalized, c):
        ax = self.ax
        ax.clear()
        colors = np.where(normalized > 0.5, c["plot2"], c["plot1"])
        ax.vlines(freqs, 0, normalized, colors=colors, linewidth=1.6)
        ax.scatter(freqs, normalized, c=colors, s=26, zorder=3)
        ax.axhline(0.5, color=c["muted"], linestyle="--", linewidth=1)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Normalized amplitude")
        ax.margins(x=0.05)
        ax.set_ylim(0, 1.12)
        self.finish(c)

    def show_phase(self, freqs, phases, c):
        ax = self.ax
        ax.clear()
        ax.vlines(freqs, 0, phases, colors=c["plot1"], linewidth=1.6)
        ax.scatter(freqs, phases, c=c["plot1"], s=26, zorder=3)
        ax.axhline(0, color=c["muted"], linewidth=0.8)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Phase (rad)")
        ax.margins(x=0.05)
        ax.set_ylim(-math.pi * 1.15, math.pi * 1.15)
        ax.set_yticks([-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi])
        ax.set_yticklabels(["-π", "-π/2", "0", "π/2", "π"])
        self.finish(c)


class QuantizeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Quantize Signal")
        self.setMinimumWidth(340)

        self.mode = QComboBox()
        self.mode.addItems(["Levels", "Bits"])
        self.value = QSpinBox()
        self.hint = QLabel()
        self.hint.setObjectName("muted")
        self.mode.currentIndexChanged.connect(self.on_mode)
        self.value.valueChanged.connect(self.update_hint)

        form = QFormLayout()
        form.addRow("Specify", self.mode)
        form.addRow("Value", self.value)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.hint)
        layout.addWidget(buttons)
        self.on_mode()

    def on_mode(self):
        if self.mode.currentText() == "Levels":
            self.value.setRange(1, 65536)
            self.value.setValue(4)
        else:
            self.value.setRange(1, 16)
            self.value.setValue(3)
        self.update_hint()

    def update_hint(self):
        value = self.value.value()
        if self.mode.currentText() == "Levels":
            bits = math.ceil(math.log2(value)) if value > 1 else 1
            self.hint.setText(f"{value} levels need {bits} bit(s) per sample")
        else:
            self.hint.setText(f"{value} bit(s) give {2 ** value} levels")

    def values(self):
        if self.mode.currentText() == "Levels":
            return self.value.value(), None
        return None, self.value.value()


class QuantizationTableDialog(QDialog):
    def __init__(self, x, intervals, q_y, errors, encoded, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quantization Results")
        self.resize(720, 460)

        table = QTableWidget(len(x), 5)
        table.setHorizontalHeaderLabels(["Index", "Interval", "Encoded", "Quantized Amplitude", "Error"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().hide()
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setUpdatesEnabled(False)
        for i in range(len(x)):
            row = [str(x[i]), str(intervals[i]), encoded[i], f"{q_y[i]:.4f}", f"{errors[i]:.4f}"]
            for col, text in enumerate(row):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, col, item)
        table.setUpdatesEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(table)


class ModifyComponentDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.owner = window
        self.setWindowTitle("Modify Component")
        self.setMinimumWidth(360)

        self.k = QSpinBox()
        self.freq_label = QLabel()
        self.freq_label.setObjectName("muted")
        self.amp = QDoubleSpinBox()
        self.amp.setDecimals(6)
        self.amp.setRange(0, 1e12)
        self.phase = QDoubleSpinBox()
        self.phase.setDecimals(6)
        self.phase.setRange(-1000, 1000)
        self.phase.setSuffix(" rad")
        self.k.valueChanged.connect(self.load_component)

        form = QFormLayout()
        form.addRow("Component k", self.k)
        form.addRow("", self.freq_label)
        form.addRow("Amplitude", self.amp)
        form.addRow("Phase", self.phase)

        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.apply)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.close)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(close_btn)
        buttons.addWidget(apply_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addLayout(buttons)
        self.reload()

    def reload(self):
        if self.owner.spectrum is None:
            self.close()
            return
        self.k.blockSignals(True)
        self.k.setRange(0, len(self.owner.spectrum[0]) - 1)
        self.k.blockSignals(False)
        self.load_component()

    def load_component(self):
        amplitudes, phases = self.owner.spectrum
        k = self.k.value()
        self.amp.setValue(amplitudes[k])
        self.phase.setValue(phases[k])
        self.freq_label.setText(f"Frequency: {k * self.owner.fs / len(amplitudes):.4g} Hz")

    def apply(self):
        self.owner.modify_component(self.k.value(), self.amp.value(), self.phase.value())


class TestReportDialog(QDialog):
    def __init__(self, results, colors, parent):
        super().__init__(parent)
        self.setWindowTitle("Test Results")
        self.setMinimumWidth(420)

        passed = sum(1 for _, ok in results if ok)
        all_ok = passed == len(results)
        color = colors["ok"] if all_ok else colors["bad"]

        header = QLabel(f"{passed} of {len(results)} tests passed")
        header.setObjectName("cardTitle")
        header.setStyleSheet(f"color: {color};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(8)
        layout.addWidget(header)
        for name, ok in results:
            row_color = colors["ok"] if ok else colors["bad"]
            mark = "✓ PASSED" if ok else "✗ FAILED"
            label = QLabel(f"<span style='color:{row_color}; font-weight:600'>{mark}</span>&nbsp;&nbsp;{name}")
            layout.addWidget(label)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("primary")
        close_btn.clicked.connect(self.accept)
        layout.addSpacing(8)
        layout.addWidget(close_btn)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced DSP Framework")
        self.setMinimumSize(1020, 620)

        self.settings = QSettings("DSPLab", "AdvancedDSPFramework")
        self.dark = self.settings.value("dark", False, type=bool)
        self.colors = gui_theme.DARK if self.dark else gui_theme.LIGHT

        self.signals = {1: None, 2: None}
        self.spectrum = None
        self.fs = 100.0
        self.view = "time"
        self.discrete = False
        self.undo_stack = []
        self.redo_stack = []
        self.actions = {}
        self.modify_dialog = None

        self.build_actions()
        self.build_ui()
        self.build_menus()

        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1320, 800)
        self.apply_theme()
        self.status("Ready - load a signal (Ctrl+O) or drop a .txt file onto a plot.")

    # --- Construction ---

    def build_actions(self):
        table = [
            ("load", "Load Signal...", "Ctrl+O", "Load a signal file into the target signal", self.action_load),
            ("save", "Save Signal...", "Ctrl+S", "Save the target signal to a file", self.action_save),
            ("add", "Add Signal 1 + 2", None, "Add Signal 1 and Signal 2 (result goes to the target)", lambda: self.action_binary("add")),
            ("sub", "Subtract Signal 1 - 2", None, "Subtract Signal 2 from Signal 1 (result goes to the target)", lambda: self.action_binary("sub")),
            ("add_files", "Add Multiple Files...", None, "Pick several signal files and add them together", self.action_add_files),
            ("mul", "Multiply by Constant...", None, "Multiply the target signal by a constant (-1 inverts it)", self.action_multiply),
            ("square", "Square", None, "Square every sample of the target signal", lambda: self.apply_to_target(dsp_logic.square_signal, "squared")),
            ("norm", "Normalize...", None, "Scale the target signal to 0..1 or -1..1", self.action_normalize),
            ("acc", "Accumulate", None, "Running sum of the target signal", lambda: self.apply_to_target(dsp_logic.accumulate_signal, "accumulated")),
            ("quant", "Quantize...", None, "Quantize the target signal; error goes to the other signal", self.action_quantize),
            ("dft", "Apply DFT...", "Ctrl+D", "Fourier transform of the target signal", self.action_dft),
            ("dominant", "Dominant Frequencies", None, "List frequencies with normalized amplitude above 0.5", self.action_dominant),
            ("modify", "Modify Amplitude / Phase...", "Ctrl+M", "Edit the amplitude and phase of one frequency component", self.action_modify),
            ("remove_dc", "Remove DC Component", None, "Remove F(0) from the target signal", lambda: self.apply_to_target(lambda x, y: (x, dsp_logic.remove_dc_component(y)), "DC component removed")),
            ("idft", "Reconstruct Signal (IDFT)", None, "Rebuild the time signal from the current spectrum", self.action_idft),
            ("load_freq", "Load Frequency File...", None, "Load a frequency-domain file (amplitude and phase)", self.action_load_freq),
            ("save_freq", "Save Frequency File...", None, "Save the current spectrum as amplitude and phase", self.action_save_freq),
            ("undo", "Undo", "Ctrl+Z", "Undo the last change", self.action_undo),
            ("redo", "Redo", "Ctrl+Y", "Redo the last undone change", self.action_redo),
            ("theme", "Toggle Dark Mode", "Ctrl+T", "Switch between light and dark theme", self.toggle_theme),
            ("tests", "Run All TA Tests", None, "Run every provided TA verification test", lambda: self.run_suites(TEST_SUITES)),
            ("exit", "Exit", "Ctrl+Q", "Close the application", self.close),
        ]
        for key, text, shortcut, tip, handler in table:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.setToolTip(tip)
            action.setStatusTip(tip)
            action.triggered.connect(lambda checked=False, h=handler: h())
            self.actions[key] = action

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.build_sidebar())

        content = QWidget()
        column = QVBoxLayout(content)
        column.setContentsMargins(16, 14, 16, 12)
        column.setSpacing(12)
        column.addWidget(self.build_topbar())

        self.cards = {1: PlotCard(), 2: PlotCard()}
        plots = QHBoxLayout()
        plots.setSpacing(12)
        for slot, card in self.cards.items():
            card.file_dropped.connect(lambda path, s=slot: self.load_path(s, path))
            plots.addWidget(card, 1)
        column.addLayout(plots, 1)

        self.info_bar = QFrame()
        self.info_bar.setObjectName("infobar")
        info_layout = QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(14, 8, 14, 8)
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        column.addWidget(self.info_bar)

        root.addWidget(content, 1)
        self.target_box.currentIndexChanged.connect(self.on_target_changed)

    def build_sidebar(self):
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(290)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 18, 8, 14)
        layout.setSpacing(0)

        title = QLabel("DSP Studio")
        title.setObjectName("appTitle")
        subtitle = QLabel("Signal Processing Framework")
        subtitle.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        target_label = QLabel("TARGET SIGNAL")
        target_label.setObjectName("sectionLabel")
        self.target_box = QComboBox()
        self.target_box.addItems(["Signal 1", "Signal 2"])
        self.target_box.setToolTip("Operations in the sidebar apply to this signal")
        layout.addWidget(target_label)
        layout.addWidget(self.target_box)

        content = QWidget()
        content.setObjectName("sidebarContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 6, 0)
        content_layout.setSpacing(1)
        for section, keys in SECTIONS:
            label = QLabel(section.upper())
            label.setObjectName("sectionLabel")
            content_layout.addWidget(label)
            for key in keys:
                action = self.actions[key]
                button = QPushButton(action.text())
                button.setToolTip(action.toolTip())
                button.setCursor(Qt.PointingHandCursor)
                button.clicked.connect(action.trigger)
                content_layout.addWidget(button)
        content_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        run_btn = QPushButton("Run All TA Tests")
        run_btn.setObjectName("primary")
        run_btn.setCursor(Qt.PointingHandCursor)
        run_btn.clicked.connect(self.actions["tests"].trigger)
        layout.addSpacing(8)
        layout.addWidget(run_btn)
        return frame

    def build_topbar(self):
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)

        view_segment, self.view_buttons = self.make_segment(
            [("Time Domain", "time"), ("Spectrum", "freq")], self.on_view_changed)
        repr_segment, self.repr_buttons = self.make_segment(
            [("Continuous", False), ("Discrete", True)], self.on_repr_changed)

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.setObjectName("ghost")
        self.undo_btn.clicked.connect(self.actions["undo"].trigger)
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.setObjectName("ghost")
        self.redo_btn.clicked.connect(self.actions["redo"].trigger)
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("ghost")
        self.theme_btn.clicked.connect(self.actions["theme"].trigger)

        layout.addWidget(view_segment)
        layout.addWidget(repr_segment)
        layout.addStretch()
        layout.addWidget(self.undo_btn)
        layout.addWidget(self.redo_btn)
        layout.addWidget(self.theme_btn)
        return bar

    def make_segment(self, options, handler):
        frame = QFrame()
        frame.setObjectName("segment")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        group = QButtonGroup(frame)
        group.setExclusive(True)
        buttons = {}
        for text, value in options:
            button = QPushButton(text)
            button.setObjectName("seg")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            group.addButton(button)
            layout.addWidget(button)
            button.clicked.connect(lambda checked=False, v=value: handler(v))
            buttons[value] = button
        return frame, buttons

    def build_menus(self):
        a = self.actions
        bar = self.menuBar()

        file_menu = bar.addMenu("File")
        for key in ("load", "save", None, "load_freq", "save_freq", None, "exit"):
            file_menu.addSeparator() if key is None else file_menu.addAction(a[key])

        edit_menu = bar.addMenu("Edit")
        edit_menu.addAction(a["undo"])
        edit_menu.addAction(a["redo"])

        for title, keys in (("Arithmetic Operations", SECTIONS[1][1]), ("Quantization", SECTIONS[2][1]),
                            ("Frequency Domain", SECTIONS[3][1])):
            menu = bar.addMenu(title)
            for key in keys:
                menu.addAction(a[key])

        test_menu = bar.addMenu("Testing")
        for label, runner in TEST_SUITES:
            action = QAction(f"Run {label}...", self)
            action.triggered.connect(lambda checked=False, s=[(label, runner)]: self.run_suites(s))
            test_menu.addAction(action)
        test_menu.addSeparator()
        test_menu.addAction(a["tests"])

        view_menu = bar.addMenu("View")
        view_menu.addAction(a["theme"])

    # --- State, history and refresh ---

    @property
    def target(self):
        return self.target_box.currentIndex() + 1

    def status(self, message):
        self.statusBar().showMessage(message, 9000)

    def snapshot(self):
        signals = {}
        for slot, data in self.signals.items():
            signals[slot] = (list(data[0]), list(data[1])) if data else None
        spectrum = (list(self.spectrum[0]), list(self.spectrum[1])) if self.spectrum else None
        return signals, spectrum, self.fs

    def restore(self, snap):
        self.signals, self.spectrum, self.fs = snap

    def checkpoint(self):
        self.undo_stack.append(self.snapshot())
        del self.undo_stack[:-HISTORY_LIMIT]
        self.redo_stack.clear()

    def action_undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self.snapshot())
        self.restore(self.undo_stack.pop())
        self.refresh()
        self.status("Undone")

    def action_redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self.snapshot())
        self.restore(self.redo_stack.pop())
        self.refresh()
        self.status("Redone")

    def refresh(self):
        c = self.colors
        if self.view == "freq" and self.spectrum is None:
            self.view = "time"
        if self.view == "time":
            self.draw_time(c)
        else:
            self.draw_spectrum(c)
        self.update_active_cards()
        self.update_info()

        for value, button in self.view_buttons.items():
            button.setChecked(value == self.view)
        for value, button in self.repr_buttons.items():
            button.setChecked(value == self.discrete)
            button.setEnabled(self.view == "time")

        self.undo_btn.setEnabled(bool(self.undo_stack))
        self.redo_btn.setEnabled(bool(self.redo_stack))
        self.actions["undo"].setEnabled(bool(self.undo_stack))
        self.actions["redo"].setEnabled(bool(self.redo_stack))

        if self.modify_dialog is not None and self.modify_dialog.isVisible():
            self.modify_dialog.reload()

    def draw_time(self, c):
        for slot, card in self.cards.items():
            card.title.setText(f"Signal {slot}")
            data = self.signals[slot]
            if data is None:
                card.info.setText("Empty")
                card.show_empty("No signal loaded\nPress Ctrl+O or drop a .txt file here", c)
                continue
            x, y = data
            as_stems = card.show_time(x, y, self.discrete, c, "plot1" if slot == 1 else "plot2")
            note = "" if as_stems or not self.discrete else f"  ·  line view (over {STEM_LIMIT} samples)"
            card.info.setText(f"N = {len(y)}  ·  min {min(y):.4g}  ·  max {max(y):.4g}  ·  mean {sum(y) / len(y):.4g}{note}")

    def draw_spectrum(self, c):
        amplitudes, phases = self.spectrum
        freqs = np.array(dsp_logic.frequencies(len(amplitudes), self.fs))
        normalized = np.array(dsp_logic.normalize_amplitudes(amplitudes))
        self.cards[1].title.setText("Frequency vs Amplitude")
        self.cards[1].info.setText(f"Normalized to max |X(k)| = {max(amplitudes):.4g}  ·  red = above 0.5")
        self.cards[1].show_amplitude(freqs, normalized, c)
        self.cards[2].title.setText("Frequency vs Phase")
        self.cards[2].info.setText("Radians, in the range -π to π")
        self.cards[2].show_phase(freqs, np.array(phases), c)

    def update_active_cards(self):
        for slot, card in self.cards.items():
            card.setProperty("active", self.view == "time" and slot == self.target)
            card.style().unpolish(card)
            card.style().polish(card)

    def update_info(self):
        if self.view == "freq":
            amplitudes = self.spectrum[0]
            freqs = dsp_logic.frequencies(len(amplitudes), self.fs)
            dominant = dsp_logic.dominant_frequencies(freqs, amplitudes)
            shown = ", ".join(f"{f:g} Hz" for f in dominant[:12])
            if len(dominant) > 12:
                shown += ", ..."
            self.info_label.setText(f"Fs = {self.fs:g} Hz   ·   N = {len(amplitudes)}   ·   "
                                    f"Δf = {self.fs / len(amplitudes):g} Hz   ·   "
                                    f"Dominant (> 0.5): {shown or 'none'}")
        else:
            counts = [len(self.signals[s][1]) if self.signals[s] else 0 for s in (1, 2)]
            self.info_label.setText(f"Target: Signal {self.target}   ·   Signal 1: {counts[0]} samples   ·   "
                                    f"Signal 2: {counts[1]} samples")

    def on_target_changed(self):
        self.update_active_cards()
        self.update_info()

    def on_view_changed(self, value):
        if value == "freq" and self.spectrum is None:
            self.status("No spectrum yet - use Apply DFT or load a frequency file first.")
        else:
            self.view = value
        self.refresh()

    def on_repr_changed(self, value):
        self.discrete = value
        self.refresh()

    def apply_theme(self):
        self.colors = gui_theme.DARK if self.dark else gui_theme.LIGHT
        QApplication.instance().setStyleSheet(gui_theme.stylesheet(self.colors))
        self.theme_btn.setText("Light Mode" if self.dark else "Dark Mode")
        self.refresh()

    def toggle_theme(self):
        self.dark = not self.dark
        self.settings.setValue("dark", self.dark)
        self.apply_theme()

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    # --- File actions ---

    def require(self, slot):
        data = self.signals[slot]
        if data is None:
            QMessageBox.warning(self, "No Signal", f"Signal {slot} is empty.\nLoad a signal first (Ctrl+O) or pick another target.")
        return data

    def action_load(self):
        path, _ = QFileDialog.getOpenFileName(self, f"Load into Signal {self.target}", "", FILE_FILTER)
        if path:
            self.load_path(self.target, path)

    def load_path(self, slot, path):
        try:
            with open(path, "r") as f:
                header = f.readline().strip()
            if header == "1":
                self.load_freq_path(path)
                return
            x, y = dsp_logic.read_signal(path)
            if not y:
                raise ValueError("the file contains no samples")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {os.path.basename(path)}:\n{e}")
            return
        self.checkpoint()
        self.signals[slot] = (x, y)
        self.target_box.setCurrentIndex(slot - 1)
        self.view = "time"
        self.refresh()
        self.status(f"Loaded {os.path.basename(path)} into Signal {slot} ({len(y)} samples)")

    def action_save(self):
        data = self.require(self.target)
        if data is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, f"Save Signal {self.target}", "", FILE_FILTER)
        if not path:
            return
        if not path.endswith(".txt"):
            path += ".txt"
        try:
            dsp_logic.save_signal(path, data[0], data[1])
            self.status(f"Saved Signal {self.target} to {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save signal:\n{e}")

    def ask_sampling_frequency(self):
        fs, ok = QInputDialog.getDouble(self, "Sampling Frequency", "Sampling frequency (Hz):", self.fs, 0.0001, 1e9, 4)
        return fs if ok else None

    def action_load_freq(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Frequency-Domain File", "", FILE_FILTER)
        if path:
            self.load_freq_path(path)

    def load_freq_path(self, path):
        try:
            with open(path, "r") as f:
                header = f.readline().strip()
            if header != "1":
                raise ValueError("not a frequency-domain file (its first line must be 1)")
            amplitudes, phases = dsp_logic.read_freq_signal(path)
            if not amplitudes:
                raise ValueError("the file contains no components")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {os.path.basename(path)}:\n{e}")
            return
        fs = self.ask_sampling_frequency()
        if fs is None:
            return
        self.checkpoint()
        self.spectrum = (amplitudes, phases)
        self.fs = fs
        self.view = "freq"
        self.refresh()
        self.status(f"Loaded spectrum from {os.path.basename(path)} ({len(amplitudes)} components)")

    def action_save_freq(self):
        if self.spectrum is None:
            QMessageBox.warning(self, "No Spectrum", "There is no spectrum to save.\nApply the DFT or load a frequency file first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Frequency-Domain File", "", FILE_FILTER)
        if not path:
            return
        if not path.endswith(".txt"):
            path += ".txt"
        try:
            dsp_logic.save_freq_signal(path, self.spectrum[0], self.spectrum[1])
            self.status(f"Saved spectrum to {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save spectrum:\n{e}")

    # --- Time-domain operations ---

    def apply_to_target(self, func, message):
        data = self.require(self.target)
        if data is None:
            return
        self.checkpoint()
        x, y = func(data[0], data[1])
        self.signals[self.target] = (list(x), list(y))
        self.view = "time"
        self.refresh()
        self.status(f"Signal {self.target}: {message}")

    def action_binary(self, op):
        first, second = self.signals[1], self.signals[2]
        if first is None or second is None:
            QMessageBox.warning(self, "Two Signals Needed", "Load both Signal 1 and Signal 2 first.")
            return
        self.checkpoint()
        if op == "add":
            x, y = dsp_logic.add_multiple_signals([first, second])
            text = "Signal 1 + Signal 2"
        else:
            x, y = dsp_logic.subtract_signals(first, second)
            text = "Signal 1 - Signal 2"
        self.signals[self.target] = (list(x), list(y))
        self.view = "time"
        self.refresh()
        self.status(f"{text} stored in Signal {self.target}")

    def action_add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Signals to Add", "", FILE_FILTER)
        loaded = []
        for path in paths:
            try:
                loaded.append(dsp_logic.read_signal(path))
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Skipped {os.path.basename(path)}:\n{e}")
        if not loaded:
            return
        self.checkpoint()
        x, y = dsp_logic.add_multiple_signals(loaded)
        self.signals[self.target] = (list(x), list(y))
        self.view = "time"
        self.refresh()
        self.status(f"Added {len(loaded)} signals into Signal {self.target}")

    def action_multiply(self):
        if self.require(self.target) is None:
            return
        scalar, ok = QInputDialog.getDouble(self, "Multiply", "Constant (use -1 to invert):", 1.0, -1e9, 1e9, 4)
        if ok:
            self.apply_to_target(lambda x, y: dsp_logic.multiply_signal(x, y, scalar), f"multiplied by {scalar:g}")

    def action_normalize(self):
        if self.require(self.target) is None:
            return
        kind, ok = QInputDialog.getItem(self, "Normalize", "Normalize to range:", ["0 to 1", "-1 to 1"], 0, False)
        if ok:
            self.apply_to_target(lambda x, y: dsp_logic.normalize_signal(x, y, kind), f"normalized to {kind}")

    def action_quantize(self):
        data = self.require(self.target)
        if data is None:
            return
        dialog = QuantizeDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return
        levels, bits = dialog.values()
        x, intervals, q_y, errors, encoded = dsp_logic.quantize_signal(data[0], data[1], levels=levels, bits=bits)
        if not q_y:
            QMessageBox.warning(self, "Warning", "Failed to quantize the signal.")
            return
        self.checkpoint()
        other = 2 if self.target == 1 else 1
        self.signals[self.target] = (x, q_y)
        self.signals[other] = (x, errors)
        self.view = "time"
        self.refresh()
        self.status(f"Quantized Signal {self.target}; quantization error stored in Signal {other}")
        QuantizationTableDialog(x, intervals, q_y, errors, encoded, self).exec_()

    # --- Frequency-domain operations ---

    def require_spectrum(self):
        if self.spectrum is None:
            QMessageBox.warning(self, "No Spectrum", "There is no spectrum yet.\nApply the DFT or load a frequency file first.")
        return self.spectrum

    def action_dft(self):
        data = self.require(self.target)
        if data is None:
            return
        fs = self.ask_sampling_frequency()
        if fs is None:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            amplitudes, phases = dsp_logic.dft(data[1])
        finally:
            QApplication.restoreOverrideCursor()
        self.checkpoint()
        self.spectrum = (amplitudes, phases)
        self.fs = fs
        self.view = "freq"
        self.refresh()
        self.status(f"DFT of Signal {self.target} computed ({len(amplitudes)} components, Fs = {fs:g} Hz)")

    def action_dominant(self):
        if self.require_spectrum() is None:
            return
        amplitudes = self.spectrum[0]
        freqs = dsp_logic.frequencies(len(amplitudes), self.fs)
        dominant = dsp_logic.dominant_frequencies(freqs, amplitudes)
        if dominant:
            lines = "\n".join(f"• {f:.4f} Hz" for f in dominant)
            QMessageBox.information(self, "Dominant Frequencies", f"Frequencies with normalized amplitude above 0.5:\n\n{lines}")
        else:
            QMessageBox.information(self, "Dominant Frequencies", "No frequency has a normalized amplitude above 0.5.")

    def action_modify(self):
        if self.require_spectrum() is None:
            return
        if self.modify_dialog is None:
            self.modify_dialog = ModifyComponentDialog(self)
        self.modify_dialog.reload()
        self.modify_dialog.show()
        self.modify_dialog.raise_()

    def modify_component(self, k, amplitude, phase):
        amplitudes, phases = list(self.spectrum[0]), list(self.spectrum[1])
        self.checkpoint()
        amplitudes[k] = amplitude
        phases[k] = phase
        self.spectrum = (amplitudes, phases)
        self.view = "freq"
        self.refresh()
        self.status(f"Component k = {k} set to amplitude {amplitude:g}, phase {phase:g} rad")

    def action_idft(self):
        if self.require_spectrum() is None:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            samples = dsp_logic.idft(self.spectrum[0], self.spectrum[1])
        finally:
            QApplication.restoreOverrideCursor()
        self.checkpoint()
        self.signals[self.target] = (list(range(len(samples))), samples)
        self.view = "time"
        self.refresh()
        self.status(f"Signal reconstructed with the IDFT and stored in Signal {self.target}")

    # --- Test suites ---

    def run_suites(self, suites):
        results = []
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            for label, runner in suites:
                try:
                    results.extend(runner())
                except Exception as e:
                    results.append((f"{label} (error: {e})", False))
        finally:
            QApplication.restoreOverrideCursor()
        passed = sum(1 for _, ok in results if ok)
        self.status(f"Tests: {passed} of {len(results)} passed")
        TestReportDialog(results, self.colors, self).exec_()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
