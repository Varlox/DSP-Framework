import os
import sys

def Shift_Fold_Signal(file_name,Your_indices,Your_samples):
    expected_indices=[]
    expected_samples=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V1=int(L[0])
                V2=float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break
    print("Current Output Test file is: ")
    print(file_name)
    print("\n")
    if (len(expected_samples)!=len(Your_samples)) or (len(expected_indices)!=len(Your_indices)):
        print("Shift_Fold_Signal Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Shift_Fold_Signal Test case failed, your signal have different indicies from the expected one")
            return False
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Shift_Fold_Signal Test case failed, your signal have different values from the expected one")
            return False
    print("Shift_Fold_Signal Test case passed successfully")
    return True

def run_shift_fold_tests():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    import dsp_logic

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    x, y = dsp_logic.read_signal(os.path.join(curr_dir, "input_fold.txt"))
    folded_x, folded_y = dsp_logic.fold_signal(x, y)
    delayed_x, delayed_y = dsp_logic.shift_signal(folded_x, folded_y, 500)
    advanced_x, advanced_y = dsp_logic.shift_signal(folded_x, folded_y, -500)

    return [
        ("Fold", Shift_Fold_Signal(os.path.join(curr_dir, "Output_fold.txt"), folded_x, folded_y)),
        ("Fold + Delay by 500", Shift_Fold_Signal(os.path.join(curr_dir, "Output_ShifFoldedby500.txt"), delayed_x, delayed_y)),
        ("Fold + Advance by 500", Shift_Fold_Signal(os.path.join(curr_dir, "Output_ShiftFoldedby-500.txt"), advanced_x, advanced_y)),
    ]

if __name__ == '__main__':
    run_shift_fold_tests()
