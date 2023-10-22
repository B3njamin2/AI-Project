# import cProfile

# from game import *

# ben = Game()
# ben2 = Game()
# print(ben)
# coord1 = Coord(1,0)
# coord2 = Coord(1,1)
# par = CoordPair(coord2,coord1)
# cProfile.run("for _ in range(10000): ben.is_engaged_in_combat(par)")
# cProfile.run("for _ in range(10000): ben2.is_engaged_in_combat2(par)")

import unittest
from game import *

class TestGameActions(unittest.TestCase):

    def setUp(self):
        # Initialize a game instance with the desired configuration
        self.game = Game()

    def test_repair_action(self):
        # Create a test scenario where a repair action is valid
        # For example, set up units and coordinates
        src_coord = Coord(0, 0)
        dst_coord = Coord(1, 0)
        self.game.set(src_coord, Unit(player=Player.Defender, type=UnitType.Tech))
        self.game.set(dst_coord, Unit(player=Player.Defender, type=UnitType.Program, health=5))

        # Perform the repair action
        repair_coords = CoordPair(src_coord, dst_coord)
        success, result = self.game.perform_repair(repair_coords)

        # Assert that the repair action was successful and the health has increased
        self.assertTrue(success)
        self.assertEqual(result, "Repaired 1 health point(s)")
        self.assertEqual(self.game.get(dst_coord).health, 6)

    def test_damage_action(self):
        # Create a test scenario where a damage action is valid
        # For example, set up units and coordinates
        src_coord = Coord(0, 0)
        dst_coord = Coord(1, 0)
        self.game.set(src_coord, Unit(player=Player.Attacker, type=UnitType.Program, health=3))
        self.game.set(dst_coord, Unit(player=Player.Defender, type=UnitType.Tech, health=7))

        # Perform the damage action
        damage_coords = CoordPair(src_coord, dst_coord)
        success, result = self.game.perform_attack(damage_coords)

        # Assert that the damage action was successful and the health has decreased
        self.assertTrue(success)
        self.assertEqual(result, "3 damage taken and 3 damage done")
        self.assertEqual(self.game.get(dst_coord).health, 4)

    def test_self_destruct_action(self):
        # Create a test scenario where a self-destruct action is valid
        # For example, set up a unit and coordinates
        src_coord = Coord(0, 0)
        self.game.set(src_coord, Unit(player=Player.Attacker, type=UnitType.Program, health=9))

        # Perform the self-destruct action
        self_destruct_coords = CoordPair(src_coord, src_coord)
        success, result = self.game.perform_self_destruct(self_destruct_coords)

        # Assert that the self-destruct action was successful and the unit is removed
        self.assertTrue(success)
        self.assertEqual(result, f"{src_coord} self destructed")
        self.assertIsNone(self.game.get(src_coord))

    def test_movement_action(self):
        # Create a test scenario where a movement action is valid
        # For example, set up a unit and coordinates
        src_coord = Coord(0, 0)
        dst_coord = Coord(0, 1)
        self.game.set(src_coord, Unit(player=Player.Attacker, type=UnitType.Program, health=5))

        # Perform the movement action
        movement_coords = CoordPair(src_coord, dst_coord)
        success, result = self.game.perform_movement(movement_coords)

        # Assert that the movement action was successful and the unit is at the destination
        self.assertTrue(success)
        self.assertEqual(result, "Movement successful")
        self.assertIsNone(self.game.get(src_coord))
        self.assertEqual(self.game.get(dst_coord).type, UnitType.Program)

if __name__ == '__main__':
    unittest.main()
