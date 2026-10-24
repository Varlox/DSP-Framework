import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QAction, QFileDialog, QInputDialog, 
                             QMessageBox, QRadioButton, QButtonGroup, QLabel, 
                             QGroupBox, QDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
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

class QuantizationTableDialog(QDialog):
    def __init__(self, x, intervals, orig_y, q_y, errors, encoded, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quantization Results")
        self.resize(700, 420)
        
        layout = QVBoxLayout(self)
        table = QTableWidget()
        table.setRowCount(len(x))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Index", "Interval", "Encoded", "Quantized Amplitude", "Error"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate table with quantization data
        for i in range(len(x)):
            table.setItem(i, 0, QTableWidgetItem(str(x[i])))
            inter_val = str(intervals[i]) if i < len(intervals) else "-"
            table.setItem(i, 1, QTableWidgetItem(inter_val))
            table.setItem(i, 2, QTableWidgetItem(encoded[i]))
            table.setItem(i, 3, QTableWidgetItem(f"{q_y[i]:.4f}"))
            table.setItem(i, 4, QTableWidgetItem(f"{errors[i]:.4f}"))
            
        layout.addWidget(table)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced DSP Framework")
        self.setGeometry(100, 100, 1100, 600)
        
        # State variables
        self.signal1_data = None # Tuple of (X, Y)
        self.signal2_data = None # Tuple of (X, Y)
        self.is_continuous = True
        self.spectrum = None # Tuple of (amplitudes, phases)
        self.fs = 1.0

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
        
        sub_action = QAction('Subtraction...', self)
        sub_action.triggered.connect(self.action_subtraction)
        arithmetic_menu.addAction(sub_action)
        
        mul_action = QAction('Multiplication...', self)
        mul_action.triggered.connect(self.action_multiplication)
        arithmetic_menu.addAction(mul_action)
        
        square_action = QAction('Squaring...', self)
        square_action.triggered.connect(self.action_squaring)
        arithmetic_menu.addAction(square_action)
        
        norm_action = QAction('Normalization...', self)
        norm_action.triggered.connect(self.action_normalization)
        arithmetic_menu.addAction(norm_action)
        
        acc_action = QAction('Accumulation...', self)
        acc_action.triggered.connect(self.action_accumulation)
        arithmetic_menu.addAction(acc_action)
        
        # Quantization Menu
        quant_menu = menubar.addMenu('Quantization')
        
        quant_action = QAction('Quantize Signal...', self)
        quant_action.triggered.connect(self.action_quantization)
        quant_menu.addAction(quant_action)
        
        # Frequency Domain Menu
        freq_menu = menubar.addMenu('Frequency Domain')

        dft_action = QAction('Apply DFT...', self)
        dft_action.triggered.connect(self.action_dft)
        freq_menu.addAction(dft_action)

        dominant_action = QAction('Show Dominant Frequencies', self)
        dominant_action.triggered.connect(self.action_dominant_frequencies)
        freq_menu.addAction(dominant_action)

        modify_action = QAction('Modify Amplitude / Phase...', self)
        modify_action.triggered.connect(self.action_modify_component)
        freq_menu.addAction(modify_action)

        remove_dc_action = QAction('Remove DC Component...', self)
        remove_dc_action.triggered.connect(self.action_remove_dc)
        freq_menu.addAction(remove_dc_action)

        idft_action = QAction('Reconstruct Signal (IDFT)', self)
        idft_action.triggered.connect(self.action_idft)
        freq_menu.addAction(idft_action)

        freq_menu.addSeparator()

        load_freq_action = QAction('Load Frequency-Domain File...', self)
        load_freq_action.triggered.connect(self.action_load_freq_file)
        freq_menu.addAction(load_freq_action)

        save_freq_action = QAction('Save Frequency-Domain File...', self)
        save_freq_action.triggered.connect(self.action_save_freq_file)
        freq_menu.addAction(save_freq_action)

        # Testing Menu
        test_menu = menubar.addMenu('Testing')
        
        run_task1_action = QAction('Run Task 1 TA Verification...', self)
        run_task1_action.triggered.connect(self.action_run_task1_tests)
        test_menu.addAction(run_task1_action)
        
        run_quan1_action = QAction('Run Quantization Test 1 (Bits = 3)...', self)
        run_quan1_action.triggered.connect(self.action_run_quan1_test)
        test_menu.addAction(run_quan1_action)
        
        run_quan2_action = QAction('Run Quantization Test 2 (Levels = 4)...', self)
        run_quan2_action.triggered.connect(self.action_run_quan2_test)
        test_menu.addAction(run_quan2_action)
        
        run_dft_test_action = QAction('Run DFT Test...', self)
        run_dft_test_action.triggered.connect(self.action_run_dft_test)
        test_menu.addAction(run_dft_test_action)

        run_idft_test_action = QAction('Run IDFT Test...', self)
        run_idft_test_action.triggered.connect(self.action_run_idft_test)
        test_menu.addAction(run_idft_test_action)

        run_dc_test_action = QAction('Run Remove DC Test...', self)
        run_dc_test_action.triggered.connect(self.action_run_dc_test)
        test_menu.addAction(run_dc_test_action)

        test_menu.addSeparator()

        run_all_action = QAction('Run All TA Tests (Tasks 1, 2 & 4)...', self)
        run_all_action.triggered.connect(self.action_run_all_tests)
        test_menu.addAction(run_all_action)

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

    # --- Operation Actions ---

    def action_addition(self):
        options = QFileDialog.Options()
        filepaths, _ = QFileDialog.getOpenFileNames(self, "Select Signals to Add", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if not filepaths: return
            
        signals = []
        for path in filepaths:
            try:
                x, y = dsp_logic.read_signal(path)
                signals.append((x, y))
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load {os.path.basename(path)}: {str(e)}")
                
        if not signals: return
            
        res_x, res_y = dsp_logic.add_multiple_signals(signals)
        self.signal1_data = (res_x, res_y)
        self.update_plots()
        QMessageBox.information(self, "Success", f"Successfully added {len(signals)} signals. Result plotted in Signal 1.")

    def action_subtraction(self):
        options = QFileDialog.Options()
        file1, _ = QFileDialog.getOpenFileName(self, "Select Minuend Signal (Signal 1)", "", "Text Files (*.txt);;All Files (*)", options=options)
        if not file1: return
        
        file2, _ = QFileDialog.getOpenFileName(self, "Select Subtrahend Signal (Signal 2)", "", "Text Files (*.txt);;All Files (*)", options=options)
        if not file2: return
        
        try:
            sig1 = dsp_logic.read_signal(file1)
            sig2 = dsp_logic.read_signal(file2)
            res_x, res_y = dsp_logic.subtract_signals(sig1, sig2)
            self.signal1_data = (res_x, res_y)
            self.update_plots()
            QMessageBox.information(self, "Success", "Subtraction completed (Signal 1 - Signal 2). Result plotted in Signal 1.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {str(e)}")

    def action_multiplication(self):
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")
        
        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first before multiplying.")
            return
            
        item, ok = QInputDialog.getItem(self, "Select Signal", "Which signal to multiply?", items, 0, False)
        if not ok or not item: return
            
        scalar, ok = QInputDialog.getDouble(self, "Input Scalar", "Enter a constant value to multiply (e.g. -1 to invert):", 1.0)
        if not ok: return
            
        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        res_x, res_y = dsp_logic.multiply_signal(data[0], data[1], scalar)
        
        if item == "Signal 1": self.signal1_data = (res_x, res_y)
        else: self.signal2_data = (res_x, res_y)
            
        self.update_plots()
        QMessageBox.information(self, "Success", f"{item} successfully multiplied by {scalar}.")

    def action_squaring(self):
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")
        
        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first.")
            return
            
        item, ok = QInputDialog.getItem(self, "Select Signal", "Which signal to square?", items, 0, False)
        if not ok or not item: return
            
        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        res_x, res_y = dsp_logic.square_signal(data[0], data[1])
        
        if item == "Signal 1": self.signal1_data = (res_x, res_y)
        else: self.signal2_data = (res_x, res_y)
            
        self.update_plots()
        QMessageBox.information(self, "Success", f"{item} successfully squared.")

    def action_normalization(self):
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")
        
        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first.")
            return
            
        item, ok = QInputDialog.getItem(self, "Select Signal", "Which signal to normalize?", items, 0, False)
        if not ok or not item: return
        
        norm_types = ["0 to 1", "-1 to 1"]
        n_type, ok2 = QInputDialog.getItem(self, "Select Normalization Type", "Normalize to:", norm_types, 0, False)
        if not ok2 or not n_type: return
        
        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        res_x, res_y = dsp_logic.normalize_signal(data[0], data[1], n_type)
        
        if item == "Signal 1": self.signal1_data = (res_x, res_y)
        else: self.signal2_data = (res_x, res_y)
            
        self.update_plots()
        QMessageBox.information(self, "Success", f"{item} successfully normalized from {n_type}.")

    def action_accumulation(self):
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")
        
        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first.")
            return
            
        item, ok = QInputDialog.getItem(self, "Select Signal", "Which signal to accumulate?", items, 0, False)
        if not ok or not item: return
        
        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        res_x, res_y = dsp_logic.accumulate_signal(data[0], data[1])
        
        if item == "Signal 1": self.signal1_data = (res_x, res_y)
        else: self.signal2_data = (res_x, res_y)
            
        self.update_plots()
        QMessageBox.information(self, "Success", f"{item} successfully accumulated.")

    def action_quantization(self):
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")
        
        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first.")
            return
            
        item, ok = QInputDialog.getItem(self, "Select Signal", "Which signal to quantize?", items, 0, False)
        if not ok or not item: return
        
        choices = ["Levels", "Bits"]
        q_choice, ok = QInputDialog.getItem(self, "Input Type", "Provide Levels or Bits?", choices, 0, False)
        if not ok or not q_choice: return
        
        levels, bits = None, None
        if q_choice == "Levels":
            val, ok = QInputDialog.getInt(self, "Quantization", "Enter number of levels:", 4, 1)
            if not ok: return
            levels = val
        else:
            val, ok = QInputDialog.getInt(self, "Quantization", "Enter number of bits:", 2, 1)
            if not ok: return
            bits = val
            
        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        q_x, intervals, q_y, errors, encoded = dsp_logic.quantize_signal(data[0], data[1], levels=levels, bits=bits)
        
        if not q_y:
            QMessageBox.warning(self, "Warning", "Failed to quantize signal.")
            return
            
        # Plot Quantized on Signal 1, Error on Signal 2
        self.signal1_data = (q_x, q_y)
        self.signal2_data = (q_x, errors)
        self.update_plots()
        
        QMessageBox.information(self, "Success", "Signal quantized. Quantized signal plotted in Signal 1, Error plotted in Signal 2.")
        
        # Display the detailed table
        dialog = QuantizationTableDialog(q_x, intervals, data[1], q_y, errors, encoded, self)
        dialog.exec_()

    # --- Frequency Domain Actions ---

    def pick_loaded_signal(self, prompt):
        items = []
        if self.signal1_data: items.append("Signal 1")
        if self.signal2_data: items.append("Signal 2")

        if not items:
            QMessageBox.warning(self, "Warning", "Please load a signal first.")
            return None, None

        item, ok = QInputDialog.getItem(self, "Select Signal", prompt, items, 0, False)
        if not ok or not item: return None, None

        data = self.signal1_data if item == "Signal 1" else self.signal2_data
        return item, data

    def plot_spectrum(self):
        if self.spectrum is None: return

        amplitudes, phases = self.spectrum
        freqs = np.array(dsp_logic.frequencies(len(amplitudes), self.fs))
        normalized = np.array(dsp_logic.normalize_amplitudes(amplitudes))

        self.canvas1.ax.clear()
        self.canvas1.ax.stem(freqs, normalized, linefmt='#1f77b4', markerfmt='bo', basefmt='k-')
        self.canvas1.ax.set_title("Frequency vs Amplitude (normalized)", fontweight="bold")
        self.canvas1.ax.set_xlabel('Frequency (Hz)')
        self.canvas1.ax.set_ylabel('Normalized Amplitude')
        self.canvas1.ax.grid(True, linestyle='--', alpha=0.7)
        self.canvas1.fig.tight_layout()
        self.canvas1.draw()

        self.canvas2.ax.clear()
        self.canvas2.ax.stem(freqs, np.array(phases), linefmt='#d62728', markerfmt='ro', basefmt='k-')
        self.canvas2.ax.set_title("Frequency vs Phase", fontweight="bold")
        self.canvas2.ax.set_xlabel('Frequency (Hz)')
        self.canvas2.ax.set_ylabel('Phase (radians)')
        self.canvas2.ax.grid(True, linestyle='--', alpha=0.7)
        self.canvas2.fig.tight_layout()
        self.canvas2.draw()

    def show_dominant_frequencies(self):
        amplitudes, phases = self.spectrum
        freqs = dsp_logic.frequencies(len(amplitudes), self.fs)
        dominant = dsp_logic.dominant_frequencies(freqs, amplitudes)

        if dominant:
            lines = "\n".join(f"{f:.4f} Hz" for f in dominant)
            QMessageBox.information(self, "Dominant Frequencies", f"Frequencies with normalized amplitude > 0.5:\n\n{lines}")
        else:
            QMessageBox.information(self, "Dominant Frequencies", "No frequency has normalized amplitude > 0.5.")

    def action_dft(self):
        item, data = self.pick_loaded_signal("Which signal to transform?")
        if data is None: return

        fs, ok = QInputDialog.getDouble(self, "Sampling Frequency", "Enter sampling frequency (Hz):", 100.0, 0.0001, 1e9, 4)
        if not ok: return

        self.fs = fs
        self.spectrum = dsp_logic.dft(data[1])
        self.plot_spectrum()
        self.show_dominant_frequencies()

    def action_dominant_frequencies(self):
        if self.spectrum is None:
            QMessageBox.warning(self, "Warning", "Apply DFT or load a frequency-domain file first.")
            return
        self.show_dominant_frequencies()

    def action_modify_component(self):
        if self.spectrum is None:
            QMessageBox.warning(self, "Warning", "Apply DFT or load a frequency-domain file first.")
            return

        amplitudes, phases = self.spectrum
        k, ok = QInputDialog.getInt(self, "Select Component", f"Enter component index k (0 to {len(amplitudes) - 1}):", 0, 0, len(amplitudes) - 1)
        if not ok: return

        new_amp, ok = QInputDialog.getDouble(self, "Modify Amplitude", f"Amplitude of k = {k} ({k * self.fs / len(amplitudes):.4f} Hz):", amplitudes[k], 0, 1e12, 6)
        if not ok: return

        new_phase, ok = QInputDialog.getDouble(self, "Modify Phase", f"Phase of k = {k} (radians):", phases[k], -1e6, 1e6, 6)
        if not ok: return

        amplitudes[k] = new_amp
        phases[k] = new_phase
        self.spectrum = (amplitudes, phases)
        self.plot_spectrum()

    def action_remove_dc(self):
        item, data = self.pick_loaded_signal("Remove DC component from which signal?")
        if data is None: return

        res_y = dsp_logic.remove_dc_component(data[1])

        if item == "Signal 1": self.signal1_data = (data[0], res_y)
        else: self.signal2_data = (data[0], res_y)

        self.update_plots()
        QMessageBox.information(self, "Success", f"DC component removed from {item}.")

    def action_idft(self):
        if self.spectrum is None:
            QMessageBox.warning(self, "Warning", "Apply DFT or load a frequency-domain file first.")
            return

        amplitudes, phases = self.spectrum
        samples = dsp_logic.idft(amplitudes, phases)
        self.signal1_data = (list(range(len(samples))), samples)
        self.update_plots()
        QMessageBox.information(self, "Success", "Signal reconstructed using IDFT. Result plotted in Signal 1.")

    def action_load_freq_file(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Frequency-Domain File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if not filepath: return

        fs, ok = QInputDialog.getDouble(self, "Sampling Frequency", "Enter sampling frequency (Hz):", self.fs, 0.0001, 1e9, 4)
        if not ok: return

        try:
            amplitudes, phases = dsp_logic.read_freq_signal(filepath)
            self.fs = fs
            self.spectrum = (amplitudes, phases)
            self.plot_spectrum()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load frequency-domain file: {str(e)}")

    def action_save_freq_file(self):
        if self.spectrum is None:
            QMessageBox.warning(self, "Warning", "No frequency-domain data to save.")
            return

        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Frequency-Domain File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filepath:
            try:
                if not filepath.endswith('.txt'):
                    filepath += '.txt'
                dsp_logic.save_freq_signal(filepath, self.spectrum[0], self.spectrum[1])
                QMessageBox.information(self, "Success", f"Saved to {os.path.basename(filepath)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")

    # --- Test Suite Actions ---

    def load_task4_tests(self):
        task4_dir = os.path.join(os.path.dirname(__file__), "Labs", "Task & Files-20261024T083112Z-1-001", "Task & Files")
        compare_dir = os.path.join(task4_dir, "Test Cases-20261024T083237Z-1-001", "Test Cases")
        dc_dir = os.path.join(task4_dir, "Remove DC component-20261024T083221Z-1-001", "Remove DC component")
        for path in (compare_dir, dc_dir):
            if path not in sys.path:
                sys.path.insert(0, path)
        import signalcompare, CompareSignals
        return signalcompare, CompareSignals

    def action_run_dft_test(self):
        try:
            signalcompare, _ = self.load_task4_tests()
            passed = signalcompare.run_dft_test()
            if passed:
                QMessageBox.information(self, "DFT Test", "DFT Test (Amplitude & Phase) PASSED successfully!")
            else:
                QMessageBox.warning(self, "DFT Test", "DFT Test FAILED!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute DFT test: {str(e)}")

    def action_run_idft_test(self):
        try:
            signalcompare, _ = self.load_task4_tests()
            passed = signalcompare.run_idft_test()
            if passed:
                QMessageBox.information(self, "IDFT Test", "IDFT Test PASSED successfully!")
            else:
                QMessageBox.warning(self, "IDFT Test", "IDFT Test FAILED!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute IDFT test: {str(e)}")

    def action_run_dc_test(self):
        try:
            _, compare_signals = self.load_task4_tests()
            passed = compare_signals.run_dc_test()
            if passed:
                QMessageBox.information(self, "Remove DC Test", "Remove DC Component Test PASSED successfully!")
            else:
                QMessageBox.warning(self, "Remove DC Test", "Remove DC Component Test FAILED!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute Remove DC test: {str(e)}")

    def action_run_task1_tests(self):
        try:
            test_script_dir = os.path.join(os.path.dirname(__file__), "Labs", "Task1 files+test-20260930T203736Z-1-001")
            if test_script_dir not in sys.path:
                sys.path.insert(0, test_script_dir)
            import Task1Test
            
            results = Task1Test.run_all_tests()
            report_lines = []
            all_passed = True
            for test_name, passed in results:
                status = "PASSED" if passed else "FAILED"
                report_lines.append(f"• {test_name}: {status}")
                if not passed:
                    all_passed = False
                    
            summary = "\n".join(report_lines)
            if all_passed:
                QMessageBox.information(self, "Task 1 Tests", f"All Task 1 tests passed successfully!\n\n{summary}")
            else:
                QMessageBox.warning(self, "Task 1 Tests", f"Some tests failed:\n\n{summary}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute Task 1 test suite: {str(e)}")

    def action_run_quan1_test(self):
        try:
            quan_dir = os.path.join(os.path.dirname(__file__), "Quantization-20261011T152410Z-1-001", "Quantization")
            if quan_dir not in sys.path:
                sys.path.insert(0, quan_dir)
            import QuanTest1
            
            passed = QuanTest1.run_test1()
            if passed:
                QMessageBox.information(self, "Quantization Test 1", "Quantization Test 1 (Bits = 3) PASSED successfully!")
            else:
                QMessageBox.warning(self, "Quantization Test 1", "Quantization Test 1 FAILED!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute Quantization Test 1: {str(e)}")

    def action_run_quan2_test(self):
        try:
            quan_dir = os.path.join(os.path.dirname(__file__), "Quantization-20261011T152410Z-1-001", "Quantization")
            if quan_dir not in sys.path:
                sys.path.insert(0, quan_dir)
            import QuanTest2
            
            passed = QuanTest2.run_test2()
            if passed:
                QMessageBox.information(self, "Quantization Test 2", "Quantization Test 2 (Levels = 4) PASSED successfully!")
            else:
                QMessageBox.warning(self, "Quantization Test 2", "Quantization Test 2 FAILED!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute Quantization Test 2: {str(e)}")

    def action_run_all_tests(self):
        try:
            report_lines = []
            all_passed = True
            
            # Task 1 tests
            test_script_dir = os.path.join(os.path.dirname(__file__), "Labs", "Task1 files+test-20260930T203736Z-1-001")
            if test_script_dir not in sys.path:
                sys.path.insert(0, test_script_dir)
            import Task1Test
            t1_res = Task1Test.run_all_tests()
            for name, passed in t1_res:
                report_lines.append(f"• {name}: {'PASSED' if passed else 'FAILED'}")
                if not passed: all_passed = False
                
            # Quantization tests
            quan_dir = os.path.join(os.path.dirname(__file__), "Quantization-20261011T152410Z-1-001", "Quantization")
            if quan_dir not in sys.path:
                sys.path.insert(0, quan_dir)
            import QuanTest1, QuanTest2
            
            q1_passed = QuanTest1.run_test1()
            report_lines.append(f"• Quantization Test 1 (Bits=3): {'PASSED' if q1_passed else 'FAILED'}")
            if not q1_passed: all_passed = False
            
            q2_passed = QuanTest2.run_test2()
            report_lines.append(f"• Quantization Test 2 (Levels=4): {'PASSED' if q2_passed else 'FAILED'}")
            if not q2_passed: all_passed = False

            # Task 4 tests
            signalcompare, compare_signals = self.load_task4_tests()
            for name, passed in [("DFT (Amplitude & Phase)", signalcompare.run_dft_test()),
                                 ("IDFT", signalcompare.run_idft_test()),
                                 ("Remove DC Component", compare_signals.run_dc_test())]:
                report_lines.append(f"• {name}: {'PASSED' if passed else 'FAILED'}")
                if not passed: all_passed = False

            summary = "\n".join(report_lines)
            if all_passed:
                QMessageBox.information(self, "All TA Tests", f"All TA verification tests passed successfully!\n\n{summary}")
            else:
                QMessageBox.warning(self, "All TA Tests", f"Some tests failed:\n\n{summary}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute all tests: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
