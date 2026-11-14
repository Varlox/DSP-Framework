import os
import sys

def ConvTest(Your_indices,Your_samples):
    """
    Test inputs
    InputIndicesSignal1 =[-2, -1, 0, 1]
    InputSamplesSignal1 = [1, 2, 1, 1 ]

    InputIndicesSignal2=[0, 1, 2, 3, 4, 5 ]
    InputSamplesSignal2 = [ 1, -1, 0, 0, 1, 1 ]
    """

    expected_indices=[-2, -1, 0, 1, 2, 3, 4, 5, 6]
    expected_samples = [1, 1, -1, 0, 0, 3, 3, 2, 1 ]


    if (len(expected_samples)!=len(Your_samples)) or (len(expected_indices)!=len(Your_indices)):
        print("Conv Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Conv Test case failed, your signal have different indicies from the expected one")
            return False
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Conv Test case failed, your signal have different values from the expected one")
            return False
    print("Conv Test case passed successfully")
    return True

def run_conv_test():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    import dsp_logic

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    x1, y1 = dsp_logic.read_signal(os.path.join(curr_dir, "Input_conv_Sig1.txt"))
    x2, y2 = dsp_logic.read_signal(os.path.join(curr_dir, "Input_conv_Sig2.txt"))
    x, y = dsp_logic.convolve_signals(x1, y1, x2, y2)
    return ConvTest(x, y)

if __name__ == '__main__':
    run_conv_test()
