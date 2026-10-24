
import math

#Use to test the Amplitude of DFT and IDFT
def SignalComapreAmplitude(SignalInput = [] ,SignalOutput= []):
    if len(SignalInput) != len(SignalOutput):
        return False
    else:
        for i in range(len(SignalInput)):
            if abs(SignalInput[i]-SignalOutput[i])>0.001:
                return False
            elif SignalInput[i]!=SignalOutput[i]:
                return False
        return True

def RoundPhaseShift(P):
    while P<0:
        p+=2*math.pi
    return float(P%(2*math.pi))

#Use to test the PhaseShift of DFT
def SignalComaprePhaseShift(SignalInput = [] ,SignalOutput= []):
    if len(SignalInput) != len(SignalOutput):
        return False
    else:
        for i in range(len(SignalInput)):
            A=round(SignalInput[i])
            B=round(SignalOutput[i])
            if abs(A-B)>0.0001:
                return False
            elif A!=B:
                return False
        return True




import os
import sys

def _import_dsp_logic():
    folder = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(folder, "dsp_logic.py")):
        parent = os.path.dirname(folder)
        if parent == folder:
            raise ImportError("dsp_logic.py not found above " + __file__)
        folder = parent
    if folder not in sys.path:
        sys.path.insert(0, folder)
    import dsp_logic
    return dsp_logic

def _round_all(values):
    return [round(v, 3) for v in values]

def run_dft_test():
    dsp_logic = _import_dsp_logic()
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    x, y = dsp_logic.read_signal(os.path.join(curr_dir, "DFT", "input_Signal_DFT.txt"))
    expected_amp, expected_phase = dsp_logic.read_freq_signal(os.path.join(curr_dir, "DFT", "Output_Signal_DFT_A,Phase.txt"))

    amplitudes, phases = dsp_logic.dft(y)

    amp_ok = SignalComapreAmplitude(_round_all(amplitudes), _round_all(expected_amp))
    phase_ok = SignalComaprePhaseShift(_round_all(phases), _round_all(expected_phase))
    print("DFT Amplitude test " + ("passed successfully" if amp_ok else "failed"))
    print("DFT Phase test " + ("passed successfully" if phase_ok else "failed"))
    return amp_ok and phase_ok

def run_idft_test():
    dsp_logic = _import_dsp_logic()
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    amplitudes, phases = dsp_logic.read_freq_signal(os.path.join(curr_dir, "IDFT", "Input_Signal_IDFT_A,Phase.txt"))
    x, expected = dsp_logic.read_signal(os.path.join(curr_dir, "IDFT", "Output_Signal_IDFT.txt"))

    samples = dsp_logic.idft(amplitudes, phases)

    passed = SignalComapreAmplitude(_round_all(samples), _round_all(expected))
    print("IDFT test " + ("passed successfully" if passed else "failed"))
    return passed

if __name__ == '__main__':
    run_dft_test()
    run_idft_test()
