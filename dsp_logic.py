import math

def read_signal(filepath):
    x_indices = []
    y_amplitudes = []
    
    with open(filepath, 'r') as f:
        for _ in range(3):
            f.readline()
            
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                index = int(float(parts[0]))
                amplitude = float(parts[1])
                
                x_indices.append(index)
                y_amplitudes.append(amplitude)
                
    return x_indices, y_amplitudes

def save_signal(filepath, x, y):
    with open(filepath, 'w') as f:
        f.write("0\n")
        f.write("0\n")
        f.write(f"{len(x)}\n")
        for i in range(len(x)):
            f.write(f"{x[i]} {y[i]}\n")

def multiply_signal(x, y, scalar):
    new_y = []
    for amplitude in y:
        new_y.append(amplitude * scalar)
    return x, new_y

def add_multiple_signals(signals):
    if not signals:
        return [], []
        
    global_min_idx = float('inf')
    global_max_idx = float('-inf')
    
    for x_list, y_list in signals:
        if x_list:
            current_min = min(x_list)
            current_max = max(x_list)
            if current_min < global_min_idx:
                global_min_idx = current_min
            if current_max > global_max_idx:
                global_max_idx = current_max
                
    if global_min_idx == float('inf'):
        return [], []
        
    result_x = list(range(int(global_min_idx), int(global_max_idx) + 1))
    result_y = [0.0] * len(result_x)
    
    for x_list, y_list in signals:
        for i in range(len(x_list)):
            current_x = x_list[i]
            current_y = y_list[i]
            position = int(current_x - global_min_idx)
            result_y[position] += current_y
            
    return result_x, result_y

def subtract_signals(sig1, sig2):
    x_list1, y_list1 = sig1
    x_list2, y_list2 = sig2
    
    global_min_idx = min(min(x_list1) if x_list1 else float('inf'), 
                         min(x_list2) if x_list2 else float('inf'))
    global_max_idx = max(max(x_list1) if x_list1 else float('-inf'), 
                         max(x_list2) if x_list2 else float('-inf'))
                         
    if global_min_idx == float('inf'):
        return [], []
        
    result_x = list(range(int(global_min_idx), int(global_max_idx) + 1))
    result_y = [0.0] * len(result_x)
    
    for i in range(len(x_list1)):
        pos = int(x_list1[i] - global_min_idx)
        result_y[pos] += y_list1[i]
        
    for i in range(len(x_list2)):
        pos = int(x_list2[i] - global_min_idx)
        result_y[pos] -= y_list2[i]
        
    return result_x, result_y

def square_signal(x, y):
    new_y = [val ** 2 for val in y]
    return x, new_y

def normalize_signal(x, y, norm_type):
    if not y: return x, y
    min_y = min(y)
    max_y = max(y)
    
    if min_y == max_y:
        if norm_type == "0 to 1":
            return x, [0.0]*len(y)
        else:
            return x, [0.0]*len(y)
            
    range_y = max_y - min_y
    new_y = []
    for val in y:
        norm_val = (val - min_y) / range_y
        if norm_type == "-1 to 1":
            norm_val = 2 * norm_val - 1
        new_y.append(norm_val)
    return x, new_y

def accumulate_signal(x, y):
    new_y = []
    current_sum = 0.0
    for val in y:
        current_sum += val
        new_y.append(current_sum)
    return x, new_y

def quantize_signal(x, y, levels=None, bits=None):
    if bits is not None:
        levels = 2 ** bits
        
    if not y or levels is None or levels <= 0:
        return x, [], y, [], []
        
    min_y = min(y)
    max_y = max(y)
    
    if levels == 1:
        delta = 0
    else:
        delta = (max_y - min_y) / levels
    
    intervals = []
    quantized_y = []
    errors = []
    encoded = []
    
    for val in y:
        if delta == 0:
            interval = 0
        else:
            interval = int((val - min_y) / delta)
            
        if interval >= levels:
            interval = levels - 1
            
        q_val = min_y + delta * (interval + 0.5)
        
        intervals.append(interval + 1)
        quantized_y.append(q_val)
        errors.append(q_val - val)
        
        if bits is not None:
            enc_str = format(interval, f'0{bits}b')
        else:
            b = math.ceil(math.log2(levels)) if levels > 1 else 1
            enc_str = format(interval, f'0{b}b')
            
        encoded.append(enc_str)
        
    return x, intervals, quantized_y, errors, encoded
