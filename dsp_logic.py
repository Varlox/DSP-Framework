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
    # The x (indices) array remains exactly the same
    new_y = []
    
    # Iterate through the amplitudes and multiply each by the scalar
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
        
    # Step 1: Find the global minimum and maximum indices across all signals
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
                
    # If no valid indices were found (e.g., all signals were empty)
    if global_min_idx == float('inf'):
        return [], []
        
    # Step 2: Create a unified X array spanning from global_min to global_max
    result_x = list(range(int(global_min_idx), int(global_max_idx) + 1))
    
    # Step 3: Create a zero-filled Y array of the same length
    result_y = [0.0] * len(result_x)
    
    # Step 4: Add each signal's values to the zero-filled array at the correct positions
    for x_list, y_list in signals:
        for i in range(len(x_list)):
            current_x = x_list[i]
            current_y = y_list[i]
            
            # Find the correct position in our unified result_x array
            # The offset is simply (current_x - global_min_idx)
            position = int(current_x - global_min_idx)
            
            # Add the amplitude to our accumulating result_y array
            result_y[position] += current_y
            
    return result_x, result_y
