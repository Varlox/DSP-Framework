import os
import sys

def SignalsAreEqual(TaskName,given_output_filePath,Your_indices,Your_samples):
    expected_indices=[]
    expected_samples=[]
    with open(given_output_filePath, 'r') as f:
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
    if (len(expected_samples)!=len(Your_samples)) or (len(expected_indices)!=len(Your_indices)):
        print(TaskName+" Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print(TaskName+" Test case failed, your signal have different indicies from the expected one") 
            return False
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print(TaskName+" Test case failed, your signal have different values from the expected one") 
            return False
    print(TaskName+" Test case passed successfully")
    return True

def run_dc_test():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    import dsp_logic

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    x, y = dsp_logic.read_signal(os.path.join(curr_dir, "DC_component_input.txt"))
    result = dsp_logic.remove_dc_component(y)
    return SignalsAreEqual("DC Component", os.path.join(curr_dir, "DC_component_output.txt"), x, result)

if __name__ == '__main__':
    run_dc_test()
