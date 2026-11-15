import os
import sys

def run_moving_average_tests():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    dsp_dir = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
    compare_dir = os.path.join(dsp_dir, "Labs", "Task & Files-20261024T083112Z-1-001", "Task & Files",
                               "Remove DC component-20261024T083221Z-1-001", "Remove DC component")
    for folder in (dsp_dir, compare_dir):
        if folder not in sys.path:
            sys.path.insert(0, folder)
    import dsp_logic
    import CompareSignals

    task2_input_dir = os.path.join(dsp_dir, "Labs", "Task1 files+test-20260930T203736Z-1-001", "input")
    cases = [
        ("Moving Average Test 1 (window = 3)", "Signal1.txt", 3, "OutMovAvgTest1.txt"),
        ("Moving Average Test 2 (window = 5)", "Signal2.txt", 5, "OutMovAvgTest2.txt"),
    ]

    results = []
    for name, input_file, window, output_file in cases:
        x, y = dsp_logic.read_signal(os.path.join(task2_input_dir, input_file))
        out_x, out_y = dsp_logic.moving_average(x, y, window)
        passed = CompareSignals.SignalsAreEqual(name, os.path.join(curr_dir, output_file), out_x, out_y)
        results.append((name, passed))
    return results

if __name__ == '__main__':
    run_moving_average_tests()
