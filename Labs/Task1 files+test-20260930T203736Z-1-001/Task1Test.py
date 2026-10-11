#!/usr/bin/env python
# coding: utf-8

import os
import sys

# Ensure dsp_logic can be imported from parent directory if needed
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import dsp_logic

def ReadSignalFile(file_name):
    expected_indices=[]
    expected_samples=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
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
    return expected_indices,expected_samples


def AddSignalSamplesAreEqual(userFirstSignal,userSecondSignal,Your_indices,Your_samples):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    if(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal2.txt'):
        file_name=os.path.join(curr_dir, "output", "Signal1+signal2.txt")
    elif(userFirstSignal=='Signal1.txt' and userSecondSignal=='Signal3.txt'):
        file_name=os.path.join(curr_dir, "output", "signal1+signal3.txt")
    else:
        print("Unknown signal pair for addition test")
        return False

    expected_indices,expected_samples=ReadSignalFile(file_name)          
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Addition Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Addition Test case failed, your signal have different indicies from the expected one") 
            return False
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Addition Test case failed, your signal have different values from the expected one") 
            return False
    print("Addition Test case passed successfully")
    return True


def MultiplySignalByConst(User_Const,Your_indices,Your_samples):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    if(User_Const==5):
        file_name=os.path.join(curr_dir, "output", "MultiplySignalByConstant-Signal1 - by 5.txt")
    elif(User_Const==10):
        file_name=os.path.join(curr_dir, "output", "MultiplySignalByConstant-signal2 - by 10.txt")
    else:
        print(f"Unknown constant {User_Const} for multiplication test")
        return False
        
    expected_indices,expected_samples=ReadSignalFile(file_name)      
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Multiply by "+str(User_Const)+ " Test case failed, your signal have different length from the expected one")
        return False
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different indicies from the expected one") 
            return False
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Multiply by "+str(User_Const)+" Test case failed, your signal have different values from the expected one") 
            return False
    print("Multiply by "+str(User_Const)+" Test case passed successfully")
    return True


def SignalSamplesAreEqual(TaskName,output_file_name,Your_indices,Your_samples):
    expected_indices=[]
    expected_samples=[]
    with open(output_file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
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
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
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


def run_all_tests():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(curr_dir, "input")
    
    sig1_file = os.path.join(input_dir, "Signal1.txt")
    sig2_file = os.path.join(input_dir, "Signal2.txt")
    sig3_file = os.path.join(input_dir, "signal3.txt")
    
    s1 = dsp_logic.read_signal(sig1_file)
    s2 = dsp_logic.read_signal(sig2_file)
    s3 = dsp_logic.read_signal(sig3_file)
    
    results = []
    
    # Test 1: Signal1 + Signal2
    x_add1, y_add1 = dsp_logic.add_multiple_signals([s1, s2])
    res1 = AddSignalSamplesAreEqual('Signal1.txt', 'Signal2.txt', x_add1, y_add1)
    results.append(("Signal1 + Signal2", res1))
    
    # Test 2: Signal1 + Signal3
    x_add2, y_add2 = dsp_logic.add_multiple_signals([s1, s3])
    res2 = AddSignalSamplesAreEqual('Signal1.txt', 'Signal3.txt', x_add2, y_add2)
    results.append(("Signal1 + Signal3", res2))
    
    # Test 3: Multiply Signal1 by 5
    x_m1, y_m1 = dsp_logic.multiply_signal(s1[0], s1[1], 5)
    res3 = MultiplySignalByConst(5, x_m1, y_m1)
    results.append(("Multiply Signal1 by 5", res3))
    
    # Test 4: Multiply Signal2 by 10
    x_m2, y_m2 = dsp_logic.multiply_signal(s2[0], s2[1], 10)
    res4 = MultiplySignalByConst(10, x_m2, y_m2)
    results.append(("Multiply Signal2 by 10", res4))
    
    return results

if __name__ == '__main__':
    print("--- Running Task 1 TA Verification Tests ---")
    run_all_tests()
