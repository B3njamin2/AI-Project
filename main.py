import os
import argparse
from game import Game, GameType, Player, CoordPair, Options, Heuristics
# from evaluate import *
# from generateStates import *
# from datetime import datetime ############################
    
def main():
    #Command line example:  python main.py --max_depth 2 --max_time 5 --max_turns 20 --game_type auto
    # parse command line arguments
    parser = argparse.ArgumentParser( prog='ai_wargame', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--max_depth', type=int, help='maximum search depth')
    parser.add_argument('--max_time', type=float, help='maximum search time')
    parser.add_argument('--game_type', type=str, default="manual", help='game type: auto|attacker|defender|manual')
    parser.add_argument('--broker', type=str, help='play via a game broker')
    
    # The maximum number of turns to declare the end of the game 
    parser.add_argument('--max_turns', type=int, help='number of turns before game ends') 
    parser.add_argument('--alpha_beta', type=str, help='A Boolean to use either minimax (false) or alpha-beta (true)')
    parser.add_argument('--heuristics', type=str, help='e0, e1, e2')
    
    args = parser.parse_args()

    # parse the game type
    if args.game_type == "attacker":
        game_type = GameType.AttackerVsComp
    elif args.game_type == "defender":
        game_type = GameType.CompVsDefender
    elif args.game_type == "manual":
        game_type = GameType.AttackerVsDefender
    else:
        game_type = GameType.CompVsComp

    # set up game options
    options = Options(game_type=game_type)

    # override class defaults via command line options
    if args.max_depth is not None:
        #if max_depth is smaller than 1 it will throw an error (cant check backwards states obviously from the beginning of the game)
        if args.max_depth < 1:
            options.max_depth = 1
        else:
            options.max_depth = args.max_depth
    if args.max_time is not None:
        options.max_time = args.max_time
    if args.broker is not None:
        options.broker = args.broker
    
    # override 
    if args.max_turns is not None:
        options.max_turns = args.max_turns
        
    if args.alpha_beta == "true":
        options.alpha_beta = True
    elif args.alpha_beta == "false":
        options.alpha_beta = False

    heuristic_name = "E0"
    if  options.heuristic == "e0":
        options.heuristic = Heuristics.e0
        heuristic_name = "E0"
    elif args.heuristics == "e1":
        options.heuristic = Heuristics.e1
        heuristic_name = "E1"
    elif args.heuristics == "e2":
        options.heuristic = Heuristics.e2
        heuristic_name = "E2"
   

    # create a new game
    game = Game(options=options)

    
    # Function to generate output file
    filename = f"gameTrace-{options.alpha_beta}-{options.max_time}-{options.max_turns}.txt"
     ########################### Changeable 
    
    def make_unique_filename(filename):
            base, ext = os.path.splitext(filename)
            counter = 1
            new_filename = filename
            while os.path.exists(new_filename):
                new_filename = f"{base}({counter}){ext}"
                counter += 1
            return new_filename
    
    filename = make_unique_filename(filename)
    
    def generate_output_file(game : Game, first=True):
        game_typ = str({game_type})
        with open(filename, 'a') as file:
            if ('Comp' in game_typ): 
                file.write(f"Heuristic score: {game.stats.heuristic_score:0.2f}")
                total_evals = sum(game.stats.evaluations_per_depth.values())

                file.write(f"\nCumulative evals: {total_evals}")
                key_limit = None
                for key, value in game.stats.evaluations_per_depth.items():
                    if value == 0.00:
                        key_limit = key
                        break

                file.write(f"\nEvals per depth: ")
                for k in range(1,key_limit+1):
                    file.write(f"{k}:{game.stats.evaluations_per_depth[k]} ")
                
                file.write(f"\nCumulative Evals per depth: ")
                for k in range(1,key_limit+1):
                    file.write(f"{k}:{game.stats.evaluations_per_depth[k]/total_evals:0.2f}% ")
               
                if game.stats.total_seconds > 0:
                    file.write(f"\nEval perf.: {total_evals/game.stats.total_seconds/1000:0.1f}k/s")
                file.write(f"\nElapsed time: {game.stats.total_seconds:0.1f}s")
                file.write(f"\nAverage branching factor: {game.stats.branching_factor[1]/game.stats.branching_factor[0]:0.1f}\n")

            if (game.latest_move is not None):
                file.write(f"Action taken: {game.latest_move.src}-{game.latest_move.dst} \n\n\n")

            file.write(f"{game}\n")

            if game.has_winner() is not None:
                file.write(f"\n\n\n{game.has_winner().name} wins in {game.turns_played} turns\n")
            
    def writeheader():
        game_typ = str({game_type})
        with open(filename, 'a') as file:
            if os.path.exists(filename):
                if (os.path.getsize(filename)<= 0):
                    file.write(f"Value of the timeout in seconds: {options.max_time}sec\n")
                    file.write(f"The maximum number of turns: {options.max_turns}\n")
                    if ('Comp' in game_typ):
                        file.write(f"The alpha-beta is {options.alpha_beta}\n")
                        if game_typ.find('Comp')< game_typ.find('r') and game_typ.find('r') != -1:
                            file.write("Player 1 is AI & Player 2 is H\n")
                        elif game_typ.find('Comp')> game_typ.find('r') and game_typ.find('r') != -1:
                            file.write("Player 1 is H & Player 2 is AI\n")
                        else:
                            file.write("Player 1 is AI & Player 2 is AI\n")
                        file.write(f"The heuristic name is: {heuristic_name} \n")############### Heuristic name TBD
                    else:
                        file.write("Player 1 is H & Player 2 is H\n")
            file.write(f"\n{game}\n")

    writeheader()
    while True:
        print(game)
        
        winner = game.has_winner()
        if winner is not None:
            print(f"{winner.name} wins!")
            break
        if game.options.game_type == GameType.AttackerVsDefender:
            game.human_turn()
        elif game.options.game_type == GameType.AttackerVsComp and game.next_player == Player.Attacker:
            game.human_turn()
        elif game.options.game_type == GameType.CompVsDefender and game.next_player == Player.Defender:
            game.human_turn()
        else:
            #player = game.next_player
            move = game.computer_turn()            
            if move is not None:
                game.post_move_to_broker(move)
            else:
                print("Computer doesn't know what to do!!!")
                exit(1)  
        generate_output_file(game)      
        # if player != game.next_player:
        #     numBranching += len(generateStates(game)) #Total number of states visited for each turn played
        # if game.turns_played == 0: #Check if it is not the root 
        #      avgBranchingFactor= numBranching
        # else:
        #     avgBranchingFactor= numBranching/(game.turns_played)       
if __name__ == '__main__':
    main()  
