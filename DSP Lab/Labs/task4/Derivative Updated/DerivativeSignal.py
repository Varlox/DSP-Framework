import os
import sys

def DerivativeSignal():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    import dsp_logic

    InputSignal=[float(i) for i in range(1, 101)]
    expectedOutput_first = [1] * 99
    expectedOutput_second = [0] * 98

    """
    Write your Code here:
    Start
    """

    indices = list(range(len(InputSignal)))
    first_x, FirstDrev = dsp_logic.first_derivative(indices, InputSignal)
    second_x, SecondDrev = dsp_logic.second_derivative(indices, InputSignal)

    """
    End
    """

    """
    Testing your Code
    """
    if( (len(FirstDrev)!=len(expectedOutput_first)) or (len(SecondDrev)!=len(expectedOutput_second))):
        print("mismatch in length")
        return False
    first=second=True
    for i in range(len(expectedOutput_first)):
        if abs(FirstDrev[i] - expectedOutput_first[i]) < 0.01:
            continue
        else:
            first=False
            print("1st derivative wrong")
            return False
    for i in range(len(expectedOutput_second)):
        if abs(SecondDrev[i] - expectedOutput_second[i]) < 0.01:
            continue
        else:
            second=False
            print("2nd derivative wrong")
            return False
    if(first and second):
        print("Derivative Test case passed successfully")
        return True
    else:
        print("Derivative Test case failed")
        return False

if __name__ == '__main__':
    DerivativeSignal()
