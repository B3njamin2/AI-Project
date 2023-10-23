from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple
import random
import requests
from datetime import datetime
from time import sleep
from enums import *
from unit import Unit 
from coord import *
from stats import Stats
from options import Options
from heuristic_algorithm import minimax_timer, alpha_beta_timer, get_minimum_depth
from evaluate import evaluateScore0, evaluateScoreV2, evaluateScore


@dataclass(slots=True)
class Game:
    """Representation of the game state."""
    board: list[list[Unit | None]] = field(default_factory=list)
    next_player: Player = Player.Attacker
    turns_played : int = 0
    options: Options = field(default_factory=Options)
    stats: Stats = field(default_factory=Stats)
    _attacker_has_ai : bool = True
    _defender_has_ai : bool = True
    latest_move: CoordPair = None
    '''attacker_pieces_locations: list[Coord] = None
    defender_pieces_locations: list[Coord] = None'''

    def __post_init__(self):
        """Automatically called after class init to set up the default board state."""
        dim = self.options.dim
        self.board = [[None for _ in range(dim)] for _ in range(dim)]
        md = dim-1
        self.set(Coord(0,0),Unit(player=Player.Defender,type=UnitType.AI))
        self.set(Coord(1,0),Unit(player=Player.Defender,type=UnitType.Tech))
        self.set(Coord(0,1),Unit(player=Player.Defender,type=UnitType.Tech))
        self.set(Coord(2,0),Unit(player=Player.Defender,type=UnitType.Firewall))
        self.set(Coord(0,2),Unit(player=Player.Defender,type=UnitType.Firewall))
        self.set(Coord(1,1),Unit(player=Player.Defender,type=UnitType.Program))
        self.set(Coord(md,md),Unit(player=Player.Attacker,type=UnitType.AI))
        self.set(Coord(md-1,md),Unit(player=Player.Attacker,type=UnitType.Virus))
        self.set(Coord(md,md-1),Unit(player=Player.Attacker,type=UnitType.Virus))
        self.set(Coord(md-2,md),Unit(player=Player.Attacker,type=UnitType.Program))
        self.set(Coord(md,md-2),Unit(player=Player.Attacker,type=UnitType.Program))
        self.set(Coord(md-1,md-1),Unit(player=Player.Attacker,type=UnitType.Firewall))

        '''self.defender_pieces_locations = []
        self.attacker_pieces_locations = []

        self.defender_pieces_locations.append(Coord(0, 0))
        self.defender_pieces_locations.append(Coord(1, 0))
        self.defender_pieces_locations.append(Coord(0, 1))
        self.defender_pieces_locations.append(Coord(2, 0))
        self.defender_pieces_locations.append(Coord(0, 2))
        self.defender_pieces_locations.append(Coord(1, 1))
        self.attacker_pieces_locations.append(Coord(md, md))
        self.attacker_pieces_locations.append(Coord(md - 1, md))
        self.attacker_pieces_locations.append(Coord(md, md - 1))
        self.attacker_pieces_locations.append(Coord(md - 2, md))
        self.attacker_pieces_locations.append(Coord(md, md - 2))
        self.attacker_pieces_locations.append(Coord(md - 1, md - 1))'''

    def clone(self) -> Game:
        """Make a new copy of a game for minimax recursion.

        Shallow copy of everything except the board (options and stats are shared).
        """
        new = copy.copy(self)
        new.board = copy.deepcopy(self.board)
        return new

    def is_empty(self, coord : Coord) -> bool:
        """Check if contents of a board cell of the game at Coord is empty (must be valid coord)."""
        return self.board[coord.row][coord.col] is None

    def get(self, coord : Coord) -> Unit | None:
        """Get contents of a board cell of the game at Coord."""
        if self.is_valid_coord(coord):
            return self.board[coord.row][coord.col]
        else:
            return None

    def set(self, coord : Coord, unit : Unit | None):
        """Set contents of a board cell of the game at Coord."""
        if self.is_valid_coord(coord):
            self.board[coord.row][coord.col] = unit

    def remove_dead(self, coord: Coord):
        """Remove unit at Coord if dead."""
        unit = self.get(coord)
        if unit is not None and not unit.is_alive():
            self.set(coord,None)
            '''for location in self.attacker_pieces_locations:
                if location == coord:
                    self.attacker_pieces_locations.remove(location)
            for location in self.defender_pieces_locations:
                if location == coord:
                    self.defender_pieces_locations.remove(location)'''
            if unit.type == UnitType.AI:
                if unit.player == Player.Attacker:
                    self._attacker_has_ai = False
                else:
                    self._defender_has_ai = False

    def mod_health(self, coord : Coord, health_delta : int):
        """Modify health of unit at Coord (positive or negative delta)."""
        target = self.get(coord)
        if target is not None:
            target.mod_health(health_delta)
            self.remove_dead(coord)

    def is_adjacent_move(self, coords: CoordPair) -> bool:
        if coords.src.row == coords.dst.row:
            if abs(coords.src.col - coords.dst.col) == 1:
                return True
        elif coords.src.col == coords.dst.col:
            if abs(coords.src.row - coords.dst.row) == 1:
                return True
        return False

    def is_self_move(self, coords: CoordPair) -> bool:
        return (coords.src == coords.dst)

    def is_adjacent_move_or_self_move(self, coords: CoordPair) -> bool:
        return self.is_adjacent_move(coords) or self.is_self_move(coords)

    def is_valid_move(self, coords: CoordPair) -> bool:
        """Validate a move expressed as a CoordPair. TODO: WRITE MISSING CODE!!!"""
        if not self.is_valid_coord(coords.src) or not self.is_valid_coord(coords.dst):
            return False
        unit = self.get(coords.src)
        if unit is None or unit.player != self.next_player:
            return False
        '''
        TODO everything above is good but below we need to instead of checking if the destination is empty
        we check if the destination is one away in any direction relative to src
        so call function is_adjacent_move
        
        unit = self.get(coords.dst)
        return (unit is None)
        '''
        return self.is_adjacent_move_or_self_move(coords)

    def is_AI_Firewall_Program(self, coords: CoordPair) -> bool:
        unit = self.get(coords.src)
        return (unit.type == UnitType.AI) or (unit.type == UnitType.Firewall) or (unit.type == UnitType.Program)

    def is_engaged_in_combat(self, coords: CoordPair) -> bool:
        for currentCoord in coords.src.iter_adjacent():
            current_unit = self.get(currentCoord)
            if current_unit is None:
                continue
            if current_unit.player != self.next_player:
                return True
        return False

    def is_moving_in_right_direction(self, coords: CoordPair) -> bool:
        unit = self.get(coords.src)
        if unit.player == Player.Attacker:
            return (coords.dst.col - coords.src.col == -1) or (coords.dst.row - coords.src.row == -1)
        else:
            return (coords.dst.col - coords.src.col == 1) or (coords.dst.row - coords.src.row == 1)

    def perform_movement(self, coords: CoordPair) -> Tuple[bool, str]:
        if self.is_AI_Firewall_Program(coords):

            if self.is_engaged_in_combat(coords):
                return (False,"Invalid move: Unit is engaged in combat.")

            if not self.is_moving_in_right_direction(coords):
                return (False, "Invalid move: Unit cannot move backwards.")

        self.set(coords.dst, self.get(coords.src))
        self.set(coords.src, None)
        '''if self.next_player == Player.Attacker:
            for index in range(len(self.attacker_pieces_locations)):
                if self.attacker_pieces_locations[index] == coords.src:
                    self.attacker_pieces_locations[index] = coords.dst
        else:
            for index in range(len(self.defender_pieces_locations)):
                if self.defender_pieces_locations[index] == coords.src:
                    self.defender_pieces_locations[index] = coords.dst'''

        self.latest_move = coords
        return (True, "Movement successful\n")

    def perform_attack(self, coords: CoordPair) -> Tuple[bool, str]:
        srcUnit = self.get(coords.src)
        dstUnit = self.get(coords.dst)
        src_damage_taken = dstUnit.damage_amount(srcUnit)
        dst_damage_taken = srcUnit.damage_amount(dstUnit)
        self.mod_health(coords.src, -src_damage_taken)
        self.mod_health(coords.dst, -dst_damage_taken)
        self.latest_move = coords
        return (True, f"{src_damage_taken} damage taken and {dst_damage_taken} damage done")

    def perform_repair(self, coords: CoordPair) -> Tuple[bool, str]:
        start_U = self.get(coords.src)
        target_U = self.get(coords.dst)
        added_value = start_U.repair_amount(target_U)
        if (added_value == 0):
            return (False, "Invalid move: Unit cannot repair or repair leads to no change.\n")
        
        self.mod_health(coords.dst, added_value)
        self.latest_move = coords
        return (True, f"Repaired {added_value} heath point(s)\n")
        

    def perform_self_destruct(self, coords: CoordPair) -> Tuple[bool, str]:

        coordsToCheck = [
            Coord(coords.src.row, coords.src.col + 1),
            Coord(coords.src.row, coords.src.col - 1),
            Coord(coords.src.row + 1, coords.src.col),
            Coord(coords.src.row - 1, coords.src.col),
            Coord(coords.src.row + 1, coords.src.col + 1),
            Coord(coords.src.row - 1, coords.src.col - 1),
            Coord(coords.src.row + 1, coords.src.col - 1),
            Coord(coords.src.row - 1, coords.src.col + 1),
        ]

        for currentCord in coordsToCheck:
            self.mod_health(currentCord, -2)

        self.mod_health(coords.src, -9)
        self.latest_move = coords
        return (True, f"{coords.src} self destructed")

    def perform_move(self, coords: CoordPair) -> Tuple[bool, str]:
        """Validate and perform a move expressed as a CoordPair. TODO: WRITE MISSING CODE!!!"""
        if self.is_valid_move(coords):
            if self.is_empty(coords.dst):
                return self.perform_movement(coords)
            elif self.next_player != self.get(coords.dst).player:
                return self.perform_attack(coords)
            elif self.is_self_move(coords):
                return self.perform_self_destruct(coords)
            else:
                return self.perform_repair(coords)
        return (False, "Invalid move")

    def next_turn(self):
        """Transitions game to the next turn."""
        self.next_player = self.next_player.next()
        self.turns_played += 1

    def to_string(self) -> str:
        """Pretty text representation of the game."""
        dim = self.options.dim
        output = ""
        output += f"Next player: {self.next_player.name}\n"
        output += f"Turns played: {self.turns_played}\n"
        coord = Coord()
        output += "\n   "
        for col in range(dim):
            coord.col = col
            label = coord.col_string()
            output += f"{label:^3} "
        output += "\n"
        for row in range(dim):
            coord.row = row
            label = coord.row_string()
            output += f"{label}: "
            for col in range(dim):
                coord.col = col
                unit = self.get(coord)
                if unit is None:
                    output += " .  "
                else:
                    output += f"{str(unit):^3} "
            output += "\n"
        return output

    def __str__(self) -> str:
        """Default string representation of a game."""
        return self.to_string()
    
    def is_valid_coord(self, coord: Coord) -> bool:
        """Check if a Coord is valid within out board dimensions."""
        dim = self.options.dim
        if coord.row < 0 or coord.row >= dim or coord.col < 0 or coord.col >= dim:
            return False
        return True

    def read_move(self) -> CoordPair:
        """Read a move from keyboard and return as a CoordPair."""
        while True:
            s = input(F'Player {self.next_player.name}, enter your move: ')
            coords = CoordPair.from_string(s)
            if coords is not None and self.is_valid_coord(coords.src) and self.is_valid_coord(coords.dst):
                return coords
            else:
                print('Invalid coordinates! Try again.')
    
    def human_turn(self):
        """Human player plays a move (or get via broker)."""
        mv = None
        if self.options.broker is not None:
            print("Getting next move with auto-retry from game broker...")
            while True:
                mv = self.get_move_from_broker()
                if mv is not None:
                    (success,result) = self.perform_move(mv)
                    print(f"Broker {self.next_player.name}: ",end='')
                    print(result)
                    if success:
                        self.next_turn()
                        break
                sleep(0.1)
        else:
            while True:
                mv = self.read_move()
                (success,result) = self.perform_move(mv)
                if success:
                    print(f"Player {self.next_player.name}: ",end='')
                    print(result)
                    self.next_turn()
                    break
                else:
                    print(result + " Try again.")
        self.latest_move = mv
        return
    def computer_turn(self) -> CoordPair | None:
        """Computer plays a move."""
        mv = self.suggest_move()
        if mv is not None:
            (success,result) = self.perform_move(mv)
            if success:
                print(f"Computer {self.next_player.name}: ",end='')
                print(result)
                self.next_turn()
            else: # Print something if mv is an illegal move we need to throw error 
                print("\nInvalid move. Try again!!!")
        self.latest_move = mv
        return mv

    def player_units(self, player: Player) -> Iterable[Tuple[Coord,Unit]]:
        """Iterates over all units belonging to a player."""
        for coord in CoordPair.from_dim(self.options.dim).iter_rectangle():
            unit = self.get(coord)
            if unit is not None and unit.player == player:
                yield (coord,unit)

    def is_finished(self) -> bool:
        """Check if the game is over."""
        return self.has_winner() is not None

    def has_winner(self) -> Player | None:
        """Check if the game is over and returns winner"""
        if self.options.max_turns is not None and self.turns_played >= self.options.max_turns:
            return Player.Defender
        if self._attacker_has_ai:
            if self._defender_has_ai:
                return None
            else:
                return Player.Attacker    
        return Player.Defender

    def move_candidates(self) -> Iterable[CoordPair]:
        """Generate valid move candidates for the next player."""
        move = CoordPair()
        for (src,_) in self.player_units(self.next_player):
            move.src = src
            for dst in src.iter_adjacent():
                move.dst = dst
                clone = self.clone()
                valid, temp = clone.perform_move(move)
                if valid:
                    yield move.clone()
            move.dst = src
            yield move.clone()

    def random_move(self) -> Tuple[int, CoordPair | None]:
        """Returns a random move."""
        move_candidates = list(self.move_candidates())
        random.shuffle(move_candidates)
        if len(move_candidates) > 0:
            return (0, move_candidates[0])
        else:
            return (0, None)
        

    def suggest_move(self) -> CoordPair | None:
        """Suggest the next move using minimax alpha beta. TODO: REPLACE RANDOM_MOVE WITH PROPER GAME LOGIC!!!"""
        is_maximizing_player = self.next_player == Player.Attacker
        max_depth = self.options.max_depth
        max_time = self.options.max_time

        evalfunc = None

        min_depth = get_minimum_depth(max_time, self.options.alpha_beta, self.options.heuristic)
        #check to see if min_depth is bigger than max_depth
        if min_depth > max_depth:
            min_depth = 1

        if self.options.heuristic == Heuristics.e0:
            evalfunc = evaluateScore0
        elif self.options.heuristic == Heuristics.e1:
            evalfunc = evaluateScore
        elif self.options.heuristic == Heuristics.e2:
            evalfunc = evaluateScoreV2

        start_time = datetime.now()
        if self.options.alpha_beta:
            (score, move) = alpha_beta_timer(self, is_maximizing_player, evalfunc, max_depth, max_time, min_depth)
        else:
            (score, move) = minimax_timer(self, is_maximizing_player, evalfunc, max_depth, max_time, min_depth)
        elapsed_seconds = (datetime.now() - start_time).total_seconds()
        self.stats.total_seconds += elapsed_seconds
        print(f"Heuristic score: {score}")
        print(f"Evals per depth: ",end='')
        for k in sorted(self.stats.evaluations_per_depth.keys()):
            print(f"{k}:{self.stats.evaluations_per_depth[k]} ",end='')
        print()
        total_evals = sum(self.stats.evaluations_per_depth.values())
        if self.stats.total_seconds > 0:
            print(f"Eval perf.: {total_evals/self.stats.total_seconds/1000:0.1f}k/s")
        print(f"Elapsed time: {elapsed_seconds:0.1f}s")
        print("\n")
        return move

    def post_move_to_broker(self, move: CoordPair):
        """Send a move to the game broker."""
        if self.options.broker is None:
            return
        data = {
            "from": {"row": move.src.row, "col": move.src.col},
            "to": {"row": move.dst.row, "col": move.dst.col},
            "turn": self.turns_played
        }
        try:
            r = requests.post(self.options.broker, json=data)
            if r.status_code == 200 and r.json()['success'] and r.json()['data'] == data:
                # print(f"Sent move to broker: {move}")
                pass
            else:
                print(f"Broker error: status code: {r.status_code}, response: {r.json()}")
        except Exception as error:
            print(f"Broker error: {error}")

    def get_move_from_broker(self) -> CoordPair | None:
        """Get a move from the game broker."""
        if self.options.broker is None:
            return None
        headers = {'Accept': 'application/json'}
        try:
            r = requests.get(self.options.broker, headers=headers)
            if r.status_code == 200 and r.json()['success']:
                data = r.json()['data']
                if data is not None:
                    if data['turn'] == self.turns_played+1:
                        move = CoordPair(
                            Coord(data['from']['row'],data['from']['col']),
                            Coord(data['to']['row'],data['to']['col'])
                        )
                        print(f"Got move from broker: {move}")
                        return move
                    else:
                        # print("Got broker data for wrong turn.")
                        # print(f"Wanted {self.turns_played+1}, got {data['turn']}")
                        pass
                else:
                    # print("Got no data from broker")
                    pass
            else:
                print(f"Broker error: status code: {r.status_code}, response: {r.json()}")
        except Exception as error:
            print(f"Broker error: {error}")
        return None
    
