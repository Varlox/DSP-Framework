import os
import sys

def QuantizationTest1(file_name,Your_EncodedValues,Your_QuantizedValues):
    expectedEncodedValues=[]
    expectedQuantizedValues=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V2=str(L[0])
                V3=float(L[1])
                expectedEncodedValues.append(V2)
                expectedQuantizedValues.append(V3)
                line = f.readline()
            else:
                break
    if( (len(Your_EncodedValues)!=len(expectedEncodedValues)) or (len(Your_QuantizedValues)!=len(expectedQuantizedValues))):
        print("QuantizationTest1 Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_EncodedValues)):
        if(Your_EncodedValues[i]!=expectedEncodedValues[i]):
            print("QuantizationTest1 Test case failed, your EncodedValues have different EncodedValues from the expected one") 
            return False
    for i in range(len(expectedQuantizedValues)):
        if abs(Your_QuantizedValues[i] - expectedQuantizedValues[i]) < 0.01:
            continue
        else:
            print("QuantizationTest1 Test case failed, your QuantizedValues have different values from the expected one") 
            return False
    print("QuantizationTest1 Test case passed successfully")
    return True

def run_test1():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    import dsp_logic
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    inp_file = os.path.join(curr_dir, "Quan1_input.txt")
    out_file = os.path.join(curr_dir, "Quan1_Out.txt")
    
    x, y = dsp_logic.read_signal(inp_file)
    q_x, intervals, q_y, errors, encoded = dsp_logic.quantize_signal(x, y, bits=3)
    return QuantizationTest1(out_file, encoded, q_y)

if __name__ == '__main__':
    print("--- Running Quantization Test 1 (Bits = 3) ---")
    run_test1()