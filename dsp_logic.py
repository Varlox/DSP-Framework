import math

def read_signal(filepath):
    """
    Reads a signal from a .txt file.
    Skips the first 3 lines of header.
    Returns two lists: X (indices) and Y (amplitudes).
    """
    x_indices = []
    y_amplitudes = []
    
    with open(filepath, 'r') as f:
        # Skip the first 3 lines (SignalType, IsPeriodic, N1)
        for _ in range(3):
            f.readline()
            
        # Read the rest of the lines
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split by space and extract values
            parts = line.split()
            if len(parts) >= 2:
                # The first value is the index, the second is the amplitude
                index = int(float(parts[0]))
                amplitude = float(parts[1])
                
                x_indices.append(index)
                y_amplitudes.append(amplitude)
                
    return x_indices, y_amplitudes

def save_signal(filepath, x, y):
    """
    Saves a signal to a .txt file following the standard format:
    Line 1: 0 (SignalType)
    Line 2: 0 (IsPeriodic)
    Line 3: N (Number of samples)
    Line 4 onwards: Index Amplitude
    """
    with open(filepath, 'w') as f:
        f.write("0\n")  # SignalType
        f.write("0\n")  # IsPeriodic
        f.write(f"{len(x)}\n")  # N1
        for i in range(len(x)):
            f.write(f"{x[i]} {y[i]}\n")

def multiply_signal(x, y, scalar):
    """
    Multiplies the amplitude of the signal by a constant scalar.
    If the scalar is -1, it inverts the signal.
    """
    new_y = []
    for amplitude in y:
        new_y.append(amplitude * scalar)
    return x, new_y

def add_multiple_signals(signals):
    """
    Adds multiple signals together.
    `signals` is a list of tuples, where each tuple is (x_list, y_list).
    Handles zero-padding by finding the global min and max indices.
    """
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
    """
    Subtracts sig2 from sig1: Result = sig1 - sig2
    Handles zero-padding similar to addition.
    """
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
    
    # Add sig1
    for i in range(len(x_list1)):
        pos = int(x_list1[i] - global_min_idx)
        result_y[pos] += y_list1[i]
        
    # Subtract sig2
    for i in range(len(x_list2)):
        pos = int(x_list2[i] - global_min_idx)
        result_y[pos] -= y_list2[i]
        
    return result_x, result_y

def square_signal(x, y):
    """
    Squares the amplitude of the signal.
    """
    new_y = [val ** 2 for val in y]
    return x, new_y

def normalize_signal(x, y, norm_type):
    """
    Normalizes the signal from 0 to 1 or -1 to 1 depending on user choice.
    """
    if not y: return x, y
    min_y = min(y)
    max_y = max(y)
    
    # Handle division by zero if all values are identical
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
    """
    Accumulates the signal values: y(n) = sum_{k=-inf}^{n} x(k)
    """
    new_y = []
    current_sum = 0.0
    for val in y:
        current_sum += val
        new_y.append(current_sum)
    return x, new_y

def quantize_signal(x, y, levels=None, bits=None):
    """
    Quantizes an input signal based on levels or bits.
    Returns quantized signal, errors, and encoded signal (binary).
    """
    if bits is not None:
        levels = 2 ** bits
        
    if not y or levels is None or levels <= 0:
        return x, y, [], []
        
    min_y = min(y)
    max_y = max(y)
    
    # Delta (step size)
    if levels == 1:
        delta = 0
    else:
        delta = (max_y - min_y) / levels
    
    quantized_y = []
    errors = []
    encoded = []
    
    for val in y:
        # Determine the quantization interval
        if delta == 0:
            interval = 0
        else:
            interval = int((val - min_y) / delta)
            
        # Cap interval at levels - 1 for the maximum value
        if interval >= levels:
            interval = levels - 1
            
        # Midpoint of the interval is the quantized value
        q_val = min_y + delta * (interval + 0.5)
        
        quantized_y.append(q_val)
        errors.append(q_val - val) # Error = Quantized - Original
        
        # Encoded string (binary representation)
        if bits is not None:
            enc_str = format(interval, f'0{bits}b')
        else:
            # If bits not specified, calculate bits needed to represent 'levels'
            b = math.ceil(math.log2(levels)) if levels > 1 else 1
            enc_str = format(interval, f'0{b}b')
            
        encoded.append(enc_str)
        
    return x, quantized_y, errors, encoded
