import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QAction, QFileDialog, QInputDialog, 
                             QMessageBox, QRadioButton, QButtonGroup, QLabel, QGroupBox)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import dsp_logic

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced DSP Framework")
        self.setGeometry(100, 100, 1100, 600)
        
        # State variables
        self.signal1_data = None # Tuple of (X, Y)
        self.signal2_data = None # Tuple of (X, Y)
        self.is_continuous = True
        
        self.init_ui()
        
    def init_ui(self):
        # --- Central Widget & Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Controls Area ---
        controls_group = QGroupBox("Signal Representation Settings")
        controls_layout = QHBoxLayout()
        
        self.radio_continuous = QRadioButton("Continuous (Line Graph)")
        self.radio_discrete = QRadioButton("Discrete (Stem Graph)")
        self.radio_continuous.setChecked(True)
        
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_continuous)
        self.radio_group.addButton(self.radio_discrete)
        
        self.radio_continuous.toggled.connect(self.update_plots)
        
        controls_layout.addWidget(self.radio_continuous)
        controls_layout.addWidget(self.radio_discrete)
        controls_layout.addStretch()
        
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)
        
        # --- Plotting Area ---
        plot_layout = QHBoxLayout()
        
        # Canvas 1
        self.canvas1 = MplCanvas(self, width=5, height=4, dpi=100)
        plot_layout.addWidget(self.canvas1)
        
        # Canvas 2
        self.canvas2 = MplCanvas(self, width=5, height=4, dpi=100)
        plot_layout.addWidget(self.canvas2)
        
        main_layout.addLayout(plot_layout)
        
        # --- Menu Bar ---
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        load_sig1_action = QAction('Load Signal 1...', self)
        load_sig1_action.triggered.connect(lambda: self.load_signal(1))
        file_menu.addAction(load_sig1_action)
        
        load_sig2_action = QAction('Load Signal 2...', self)
        load_sig2_action.triggered.connect(lambda: self.load_signal(2))
        file_menu.addAction(load_sig2_action)
        
        file_menu.addSeparator()
        
        save_sig1_action = QAction('Save Signal 1...', self)
        save_sig1_action.triggered.connect(lambda: self.save_signal_to_file(1))
        file_menu.addAction(save_sig1_action)
        
        save_sig2_action = QAction('Save Signal 2...', self)
        save_sig2_action.triggered.connect(lambda: self.save_signal_to_file(2))
        file_menu.addAction(save_sig2_action)
        
        # Arithmetic Operations Menu
        arithmetic_menu = menubar.addMenu('Arithmetic Operations')
        
        add_action = QAction('Addition...', self)
        add_action.triggered.connect(self.action_addition)
        arithmetic_menu.addAction(add_action)
        
        mul_action = QAction('Multiplication...', self)
        mul_action.triggered.connect(self.action_multiplication)
        arithmetic_menu.addAction(mul_action)

    def load_signal(self, slot):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, f"Load Signal {slot}", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filepath:
            try:
                x, y = dsp_logic.read_signal(filepath)
                if slot == 1:
                    self.signal1_data = (x, y)
                else:
                    self.signal2_data = (x, y)
                self.update_plots()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load signal: {str(e)}")

    def save_signal_to_file(self, slot):
        data = self.signal1_data if slot == 1 else self.signal2_data
        if data is None:
            QMessageBox.warning(self, "Warning", f"No data in Signal {slot} to save.")
            return
            
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getSaveFileName(self, f"Save Signal {slot}", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filepath:
            try:
                # Ensure it ends with .txt
                if not filepath.endswith('.txt'):
                    filepath += '.txt'
                dsp_logic.save_signal(filepath, data[0], data[1])
                QMessageBox.information(self, "Success", f"Signal {slot} saved successfully to {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save signal: {str(e)}")

    def update_plots(self):
        self.is_continuous = self.radio_continuous.isChecked()
        
        self.plot_signal(self.canvas1, self.signal1_data, "Signal 1")
        self.plot_signal(self.canvas2, self.signal2_data, "Signal 2")

    def plot_signal(self, canvas, data, title):
        canvas.ax.clear()
        if data is not None:
            # Use NumPy arrays for plotting as requested by framework constraints
            x = np.array(data[0])
            y = np.array(data[1])
            
            if self.is_continuous:
                canvas.ax.plot(x, y, color='#1f77b4', linewidth=2)
            else:
                canvas.ax.stem(x, y, linefmt='#1f77b4', markerfmt='bo', basefmt='k-')
            
            canvas.ax.set_title(title, fontweight="bold")
            canvas.ax.set_xlabel('Index')
            canvas.ax.set_ylabel('Amplitude')
            canvas.ax.grid(True, linestyle='--', alpha=0.7)
        else:
            canvas.ax.set_title(f"{title} (Empty Data)", color="gray")
            canvas.ax.set_xticks([])
            canvas.ax.set_yticks([])
            
        canvas.fig.tight_layout()
        canvas.draw()

    def action_addition(self):
        options = QFileDialog.Options()
        # Allow selecting multiple files for addition
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Select Signals to Add", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if not filepaths:
            return
            
        signals = []
        for path in filepaths:
            try:
                x, y = dsp_logic.read_signal(path)
                signals.append((x, y))
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load {os.path.basename(path)}: {str(e)}")
                
        if not signals:
            QMessageBox.critical(self, "Error", "No valid signals loaded for addition.")
            return
            
        # Perform addition using our simple logic
        res_x, res_y = dsp_logic.add_multiple_signals(signals)
        
        # Load into Signal 1 for display
        self.signal1_data = (res_x, res_y)
        self.update_plots()
        QMessageBox.information(self, "Success", f"Successfully added {len(signals)} signals. Result plotted in Signal 1.")

    def action_multiplication(self):
        # Let user choose which signal to multiply
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")
        
        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first before multiplying.")
            return
            
        item, ok = QInputDialog.getItem(self, "Select Signal", "Which signal to multiply?", items, 0, False)
        if not ok or not item:
            return
            
        scalar, ok = QInputDialog.getDouble(self, "Input Scalar", "Enter a constant value to multiply (e.g. -1 to invert):", 1.0)
        if not ok:
            return
            
        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        x, y = data
        
        res_x, res_y = dsp_logic.multiply_signal(x, y, scalar)
        
        # Update the selected signal
        if item == "Signal 1":
            self.signal1_data = (res_x, res_y)
        else:
            self.signal2_data = (res_x, res_y)
            
        self.update_plots()
        QMessageBox.information(self, "Success", f"{item} successfully multiplied by {scalar}.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Modern style
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
