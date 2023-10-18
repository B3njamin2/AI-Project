from enums import *
from game import Game
from coord import Coord, CoordPair
import copy

def doMoreDamage(result: str) -> bool:
    if "damage" not in result:
        return False

    [damageTaken, damageDone] = [int(s) for s in result.split() if s.isdigit()]
    return damageDone > damageTaken


def generateStates(game: Game) -> list[Game]:
    nextPlayer = game.next_player
    nextStates = []

    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == nextPlayer:
                srcCoord = Coord(i, j)
                for dstCoord in srcCoord.iter_adjacent():
                    if game.is_valid_coord(dstCoord):
                        nextState = copy.deepcopy(game)
                        (success, result) = nextState.perform_move(CoordPair(srcCoord, dstCoord))
                        if success:
                            #by default we know that viruses and techs are each player's most powerful pieces so insert that state in front
                            #if a move to a state does more damage to opponent than to itself insert that state in front
                            if (nextPlayer == Player.Attacker and curUnit.type == UnitType.Virus) or (nextPlayer == Player.Defender and curUnit.type == UnitType.Tech) or doMoreDamage(result):
                                if not nextStates: ##### Making sure no None values are passed
                                     return
                                temp = nextStates[0]
                                nextState.next_turn()
                                nextStates[0] = nextState
                                nextStates.append(temp)
                            else:
                                nextState.next_turn()
                                nextStates.append(nextState)
                selfDestructState = copy.deepcopy(game)
                (success, result) = selfDestructState.perform_move(CoordPair(srcCoord, srcCoord))
                if success:
                    selfDestructState.next_turn()
                    nextStates.append(selfDestructState)
    return nextStates
