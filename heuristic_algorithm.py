import time
from enums import Player, Heuristics
from generateStates import generateStates

MAX_HEURISTIC_SCORE = 2000000000
MIN_HEURISTIC_SCORE = -2000000000

def get_minimum_depth(max_time : float, alpha_beta : bool, heuristic : Heuristics) -> int:
    if max_time < 5:
        return 1

    min_depth = 4
    if not alpha_beta:
        min_depth -= 1
    if heuristic == Heuristics.e1:
        min_depth -= 1

    return min_depth

def get_time_limit(max_depth : int) -> float:
    if max_depth > 40:
        return 0.9
    return (-0.002 * max_depth) + 0.98

def minimax(node, depth : int, max_player : bool, eval_func , max_depth : int, start_time : float, time_limit : float, num_evals : list[int]):
    num_evals[0] += 1
    if (time.perf_counter() - start_time) > time_limit:
        return 0
    if depth == max_depth :
        return eval_func(node)

    if max_player:
        best_value = float('-inf')
        for child in generateStates(node):
            value = minimax(child, depth + 1, False, eval_func, max_depth, start_time, time_limit,  num_evals,)
            best_value = max(best_value, value)
        return best_value
    else:
        best_value = float('inf')
        for child in generateStates(node):
            value = minimax(child, depth + 1, True, eval_func, max_depth, start_time, time_limit, num_evals,)
            best_value = min(best_value, value)
        return best_value

def minimax_timer(initial_node, is_maximizing_player : bool, eval_func, max_depth : int, time_limit : float, min_depth : int):
    start_time = time.perf_counter()
    time_limit *= get_time_limit(max_depth) #0.98
    time_limit_reached = False
    best_node = None
    best_value = None
    num_evals=[0]

    if is_maximizing_player:
        for depth in range(min_depth, max_depth + 1):
            current_depth_best_move = None
            current_best_value = float('-inf')
            print(depth)
            print(time.perf_counter() - start_time)
            print(num_evals)
            for child in generateStates(initial_node):
                value = minimax(child, 1, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals)
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break

                if value > current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
            
            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
                print('idek')
                print(best_node)
                print('\n')
            else:
                break
    else:
        for depth in range(min_depth, max_depth + 1):
            current_depth_best_move = None
            current_best_value = float('inf')
            print(depth)
            print(time.perf_counter() - start_time)
            print(num_evals)
            for child in generateStates(initial_node):
                value = minimax(child, 1, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals)
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break

                if value < current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
            
            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
                print('idek')
                print(best_node)
                print('\n')
            else:
                break

    return (best_value , best_node.latest_move)

def alpha_beta(node, depth, alpha, beta, max_player, eval_func ,max_depth, start_time, time_limit, num_evals):
    num_evals[0] += 1
    if depth == max_depth or (time.perf_counter() - start_time) > time_limit:
        return eval_func(node)

    if max_player:
        best_value = float('-inf')
        for child in generateStates(node):
            value = alpha_beta(child, depth + 1, alpha, beta, False, eval_func, max_depth, start_time, time_limit, num_evals)
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        return best_value
    else:
        best_value = float('inf')
        for child in generateStates(node):
            value = alpha_beta(child, depth + 1, alpha, beta, True, eval_func, max_depth, start_time, time_limit, num_evals)
            best_value = min(best_value, value)
            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return best_value

def alpha_beta_timer(initial_node, is_maximizing_player : bool, eval_func, max_depth, time_limit, min_depth):
    time_limit *= get_time_limit(max_depth) #0.95
    start_time = time.perf_counter()
    time_limit_reached = False
    best_node = None
    best_value = None
    num_evals = [0]
    alpha = float('-inf')
    beta = float('inf')

    if is_maximizing_player:
        for depth in range(min_depth, max_depth + 1):
            print('depth1: ' + str(depth))
            current_depth_best_move = None
            current_best_value = float('-inf')
            print(depth)
            print(time.perf_counter() - start_time)
            print(num_evals)
            for child in generateStates(initial_node):
                value = alpha_beta(child, 1, alpha, beta, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals )
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break

                print('value1: ' + str(value) + ' cbv: ' + str(current_best_value))
                if value > current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
                    alpha = max(alpha, current_best_value)
                    print('im going in here\n')
            
            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
                print('idek3')
                print(current_depth_best_move)
                print('idek4')
                print(best_node)
                print('\n')
            else:
                break
    else:
        for depth in range(min_depth, max_depth + 1):
            print('depth2: ' + str(depth))
            current_depth_best_move = None
            current_best_value = float('inf')
            checks = 0
            print(depth)
            print(time.perf_counter() - start_time)
            print(num_evals)
            for child in generateStates(initial_node):
                value = alpha_beta(child, 1, alpha, beta, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals )
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break

                print('value2: ' + str(value) + ' cbv: ' +str(current_best_value))
                if value < current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
                    beta = min(beta, current_best_value)
                    print('im going in here2\n')

        
            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
                print('idek')
                print(current_depth_best_move)
                print('idek2')
                print(best_node)
                print('\n')
            else:
                break



    return (best_value, best_node.latest_move)