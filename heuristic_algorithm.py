import time 
from evaluate import evaluateScore0
from generateStates import generateStates

def minimax(node, depth : int, max_player : bool, max_depth : int, time_limit : float, call_count=[0]):
    call_count[0] += 1
    if depth == max_depth or time.time() > time_limit:
        return evaluateScore0(node)

    if max_player:
        best_value = float('-inf')
        for child in generateStates(node):
            value = minimax(child, depth + 1, False,  max_depth, time_limit, call_count)
            best_value = max(best_value, value)
        return best_value
    else:
        best_value = float('inf')
        for child in generateStates(node):
            value = minimax(child, depth + 1, True,  max_depth, time_limit, call_count)
            best_value = min(best_value, value)
        return best_value

def minimax_alphbeta_timer(initial_node, max_depth, time_limit):
    time_limit *= 0.98 
    best_move = None
    max_player = True
    start_time = time.perf_counter()
    time_limit_reached = False
    best_node = None
    best_value = None
    call_count=[0]

    for depth in range(1, max_depth + 1):
        current_depth_best_move = None
        current_best_value = float('-inf')
        checks = 0
        print(depth)
        print(time.perf_counter() - start_time)
        print(call_count)
        for child in generateStates(initial_node):
            value = minimax(child, 1, not max_player, depth, time_limit, call_count)
            
            if (time.perf_counter() - start_time) > time_limit:
                time_limit_reached = True
                break

            if value > current_best_value:
                current_best_value = value
                current_depth_best_move = child
        
        if not time_limit_reached:
            best_node = current_depth_best_move
            best_value = current_best_value
        else:
            break

    return (best_value ,best_node.latest_move)

