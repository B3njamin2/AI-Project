import time
from enums import Player
from generateStates import generateStates

MAX_HEURISTIC_SCORE = 2000000000
MIN_HEURISTIC_SCORE = -2000000000

def minimax(node, depth : int, max_player : bool, eval_func , max_depth : int, start_time : float, time_limit : float, num_evals : list[int]):
    
    num_evals[0] += 1
    if (time.perf_counter() - start_time) > time_limit:
        return 0
    if depth == max_depth :
        node.stats[depth] += 1
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

def minimax_timer(initial_node, is_maximizing_player : bool, eval_func, max_depth : int, time_limit : float):
    start_time = time.perf_counter()
    time_limit *= 0.98 
    time_limit_reached = False
    best_node = None
    best_value = None
    num_evals = [0]


    if is_maximizing_player:
        for depth in range(1, max_depth + 1):
            current_depth_best_move = None
            current_best_value = float('-inf')
            # print(depth)
            # print(time.perf_counter() - start_time)
            # print(num_evals)
            for child in generateStates(initial_node):
                value = minimax(child, 1, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals)
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break

                if value > current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
            
            initial_node.stats.evaluations_per_depth[depth] = num_evals[0]

            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
            else:
                break
    else:
        for depth in range(1, max_depth + 1):
            current_depth_best_move = None
            current_best_value = float('inf')
            # print(depth)
            # print(time.perf_counter() - start_time)
            # print(num_evals)
            for child in generateStates(initial_node):
                value = minimax(child, 1, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals)
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break

                if value < current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
            
            initial_node.stats.evaluations_per_depth[depth] = num_evals[0]

            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
            else:
                break

    return (best_value , best_node.latest_move)

def alpha_beta(node, depth, alpha, beta, max_player, eval_func ,max_depth, start_time, time_limit, num_evals):
    num_evals[0] += 1

    if (time.perf_counter() - start_time) > time_limit:
        return 0
    
    if depth == max_depth:
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

def alpha_beta_timer(initial_node, is_maximizing_player : bool, eval_func, max_depth, time_limit):
    time_limit *= 0.95
    start_time = time.perf_counter()
    time_limit_reached = False
    best_node = None
    best_value = None
    num_evals = [0]
    alpha = float('-inf')
    beta = float('inf')

    if is_maximizing_player:
        for depth in range(1, max_depth + 1):
            current_depth_best_move = None
            current_best_value = float('-inf')
            # print(depth)
            # print(time.perf_counter() - start_time)
            # print(num_evals)
            for child in generateStates(initial_node):
                value = alpha_beta(child, 1, alpha, beta, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals )
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break
                
                if value > current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
                    alpha = max(alpha, current_best_value)
            
            initial_node.stats.evaluations_per_depth[depth] = num_evals[0]

            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
            else:
                break
    else:
        for depth in range(1, max_depth + 1):
            current_depth_best_move = None
            current_best_value = float('inf')
            checks = 0
            # print(depth)
            # print(time.perf_counter() - start_time)
            # print(num_evals)
            for child in generateStates(initial_node):
                value = alpha_beta(child, 1, alpha, beta, not is_maximizing_player, eval_func, depth, start_time, time_limit, num_evals )
                
                if (time.perf_counter() - start_time) > time_limit:
                    time_limit_reached = True
                    break
                
                if value < current_best_value:
                    current_best_value = value
                    current_depth_best_move = child
                    beta = min(beta, current_best_value)

            initial_node.stats.evaluations_per_depth[depth] = num_evals[0]

            if not time_limit_reached:
                best_node = current_depth_best_move
                best_value = current_best_value
            else:
                break



    return (best_value, best_node.latest_move)