from enums import *
from coord import Coord, CoordPair

def doMoreDamage(result: str) -> bool:
    if "damage" not in result:
        return False

    [damageTaken, damageDone] = [int(s) for s in result.split() if s.isdigit()]
    return damageDone > damageTaken


def generateStates(game):
    nextPlayer = game.next_player
    nextStates = []

    '''
    in game there is a prebuilt function to determine all the possible moves but
    it uses iterables so it is slower than this method i use here
    '''
    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == nextPlayer:
                srcCoord = Coord(i, j)
                for dstCoord in srcCoord.iter_adjacent():
                    if game.is_valid_coord(dstCoord):
                        nextState = game.clone()
                        (success, result) = nextState.perform_move(CoordPair(srcCoord, dstCoord))
                        if success:
                            #by default we know that viruses and techs are each player's most powerful pieces so insert that state in front
                            #if a move to a state does more damage to opponent than to itself insert that state in front
                            if (len(nextStates) > 0 and (nextPlayer == Player.Attacker and curUnit.type == UnitType.Virus) or 
                                (nextPlayer == Player.Defender and curUnit.type == UnitType.Tech) or doMoreDamage(result)):
                                if (len(nextStates) > 0):
                                    temp = nextStates[0]
                                    nextState.next_turn()
                                    nextStates[0] = nextState
                                    nextStates.append(temp)
                            else:
                                nextState.next_turn()
                                nextStates.append(nextState)
    return nextStates
