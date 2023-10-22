from unit import Unit
from coord import *
from enums import *

INFINITY = 99999999

def hasAttackerWon(game) -> bool:
    return game.has_winner() is not None and game.has_winner() == Player.Attacker

def hasDefenderWon(game) -> bool:
    return game.has_winner() is not None and game.has_winner() == Player.Defender

def inOpening(game) -> bool:
    return game.turns_played < (game.options.max_turns/3)

def inEndgame(game) -> bool:
    return game.turns_played > (3*(game.options.max_turns/4))

def basicEvaluateForAttacker(game, attackerPiecesTogetherMultiplier: int) -> int:
    score = 0
    enemyAICoord = getDefenderAICoord(game)

    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == Player.Attacker:
                score += moveAttackingPiecesTowardsEnemyAIScore(game, i, j, enemyAICoord)
                score += attackerPiecesTogetherScore(game, i, j, attackerPiecesTogetherMultiplier)
                if curUnit.type == UnitType.AI:
                    score += 1000 * curUnit.health
                elif curUnit.type == UnitType.Virus:
                    score += 100 * curUnit.health
                elif curUnit.type == UnitType.Tech:
                    score += 100 * curUnit.health
                elif curUnit.type == UnitType.Program:
                    score += 50 * curUnit.health
                elif curUnit.type == UnitType.Firewall:
                    score += 20 * curUnit.health
    return score

def getDefenderAICoord(game) -> Coord:
    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == Player.Defender and curUnit.type == UnitType.AI:
                return Coord(i,j)

#encourage AI to move attacker's pieces towards the defender's AI
def moveAttackingPiecesTowardsEnemyAIScore(game, row: int, col: int, enemyAICoord: Coord) -> int:
    curUnit = game.board[row][col]
    multiplier = -5
    return multiplier * (row + col)

#encourage AI to keep attacking pieces together
def attackerPiecesTogetherScore(game, i: int, j: int, multiplier: int) -> int:
    score = 0
    curUnit = game.board[i][j]
    srcCoord = Coord(i, j)
    for dstCoord in srcCoord.iter_adjacent():
        if game.is_valid_coord(dstCoord):
            adjUnit = game.board[dstCoord.row][dstCoord.col]
            if adjUnit is not None and adjUnit.player == Player.Attacker:
                score += 1
                # TODO: test to make sure that pieces move to attack instead of solely protect AI
                '''
                if curUnit.type == UnitType.AI:
                        score += 50
                '''
                if curUnit.type == UnitType.Program and adjUnit.type == UnitType.Virus:
                    score += 2
    return multiplier * score

def basicEvaluateForDefender(game) -> int:
    score = 0
    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == Player.Defender:
                score += defenderPieceFlanksCoveredScore(game, i, j)
                if curUnit.type == UnitType.AI:
                    score += 1000 * curUnit.health
                elif curUnit.type == UnitType.Virus:
                    score += 100 * curUnit.health
                elif curUnit.type == UnitType.Tech:
                    score += 100 * curUnit.health
                elif curUnit.type == UnitType.Program:
                    score += 50 * curUnit.health
                elif curUnit.type == UnitType.Firewall:
                    score += 20 * curUnit.health
    return score

def closeToFinishScore(game) -> int:
    return game.turns_played - (3*(game.options.max_turns/4))


#encourage AI to keep num of adjacent coords as small as possible & num of defender pieces in adjacent coords as high as possible (specifically for ai) & pieces together (specifically tech & program)
def defenderPieceFlanksCoveredScore(game, i: int, j: int) -> int:
    score = 0
    curUnit = game.board[i][j]
    srcCoord = Coord(i, j)
    for dstCoord in srcCoord.iter_adjacent():
        if game.is_valid_coord(dstCoord):
            adjUnit = game.board[dstCoord.row][dstCoord.col]
            if adjUnit is not None:
                if adjUnit.player == Player.Defender:
                    score += 2
                    if curUnit.type == UnitType.AI:
                        score += 5
                    if curUnit.type == UnitType.Program and adjUnit.type == UnitType.Tech:
                        score += 5
                elif adjUnit.player == Player.Attacker:
                    #TODO: can make this more complicated
                    score -= 5
            else:
                score -= 2
        else:
            if curUnit.type == UnitType.AI:
                score += 10
            else:
                score += 5
    return score


def evaluateForAttacker(game) -> int:
    score = 0
    # TODO: test multiplier in func below with mult below to ensure that attacking pieces are encouraged to move towards ai instead of staying together
    attackerPiecesTogetherMultiplier = 0
    if inOpening(game):
        attackerPiecesTogetherMultiplier = 1
    else:
        attackerPiecesTogetherMultiplier = 3
    score += basicEvaluateForAttacker(game, attackerPiecesTogetherMultiplier)
    return score


def evaluateForDefender(game) -> int:
    score = 0
    score += basicEvaluateForDefender(game)
    if inEndgame(game):
        score += closeToFinishScore(game)
    return score

def evaluateScore(game) -> int:
    if hasAttackerWon(game):
        return INFINITY
    elif hasDefenderWon(game):
        return -INFINITY

    else:
        return evaluateForAttacker(game) - evaluateForDefender(game)


def healthTimesAttackRepairPointsScore(game, player: Player) -> int:
    score = 0
    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == player:
                if curUnit.type == UnitType.AI:
                    score += 15 * curUnit.health
                elif curUnit.type == UnitType.Virus:
                    score += 23 * curUnit.health
                elif curUnit.type == UnitType.Tech:
                    score += 19 * curUnit.health
                elif curUnit.type == UnitType.Program:
                    score += 13 * curUnit.health
                elif curUnit.type == UnitType.Firewall:
                    score += 5 * curUnit.health
    return score

#more basic eval function that is simpler but allows minimax to go deeper
def evaluateScoreV2(game) -> int:
    if hasAttackerWon(game):
        return INFINITY
    elif hasDefenderWon(game):
        return -INFINITY
    else:
        score = 0
        score += healthTimesAttackRepairPointsScore(game, Player.Attacker) - healthTimesAttackRepairPointsScore(game, Player.Defender)
        return score

'''
e0 in assignment description
'''
def evaluateScore0(game) -> int:
    score = 0
    for i in range(len(game.board)):
        for j in range(len(game.board[i])):
            curUnit = game.board[i][j]
            if curUnit is not None and curUnit.player == Player.Attacker:
                if curUnit.type == UnitType.AI:
                    score += 9999
                elif curUnit.type == UnitType.Virus:
                    score += 3
                elif curUnit.type == UnitType.Tech:
                    score += 3
                elif curUnit.type == UnitType.Firewall:
                    score += 3
                elif curUnit.type == UnitType.Program:
                    score += 3
            elif curUnit is not None and curUnit.player == Player.Defender:
                if curUnit.type == UnitType.AI:
                    score -= 9999
                elif curUnit.type == UnitType.Virus:
                    score -= 3
                elif curUnit.type == UnitType.Tech:
                    score -= 3
                elif curUnit.type == UnitType.Firewall:
                    score -= 3
                elif curUnit.type == UnitType.Program:
                    score -= 3
    return score
