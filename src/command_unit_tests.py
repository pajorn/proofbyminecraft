import unittest
from command import *
from nodes import *

class UnitTests(unittest.TestCase):
    sample_node = Node()
    sample_node.position = (0,0)
    sample_list_nodes = [sample_node]
    sample_lamp_position = (10,10)
    sample_redstone_locations = [[(1,1)],[(-1,-1)],[(0,1)]]
    Sample_Circuit = Circuit(sample_list_nodes, sample_lamp_position, sample_redstone_locations)

    def test_spawn_nodes(self):
        start_string = ["start"]
        end_string = self.Sample_Circuit.spawn_nodes(start_string)
        #print(end_string)

    def test_calculate_position(self):
        test_cases = [
            ("Down Move",  [Direction.DOWN], "~0 ~0 ~1"),
            ("Up Move",    [Direction.UP],   "~0 ~0 ~-1"),
            ("Left Move",  [Direction.LEFT], "~-1 ~0 ~0"),
            ("Right Move", [Direction.RIGHT],"~1 ~0 ~0"),
            ("Y Up Move", [Direction.Y_UP],"~0 ~1 ~0"),
            ("Y Down Move", [Direction.Y_DOWN],"~0 ~-1 ~0"),
            # Edge Cases
            ("no movement", [],               "~0 ~0 ~0"),
            ("Combo Move", [Direction.RIGHT, Direction.DOWN], "~1 ~0 ~1"),
            ("Double Right", [Direction.RIGHT, Direction.RIGHT], "~2 ~0 ~0"),
            ("multiplied Right", [Direction.RIGHT], "~1 ~0 ~0")
        ]

        for name, moves, expected in test_cases:
            with self.subTest(msg=name):
                result = calculate_position(moves)
                self.assertEqual(result, expected)

    def test_calculate_fill(self):
        test_cases = [
            ("1x1", (1,0,1), "~0 ~0 ~0 ~-0 ~0 ~-0"),
            ("3x3", (3,0,3), "~1 ~0 ~1 ~-1 ~0 ~-1"),
            ("5x5", (5,0,5), "~2 ~0 ~2 ~-2 ~0 ~-2"),
            ("3x5", (3,0,5), "~1 ~0 ~2 ~-1 ~0 ~-2")
        ]

        for name, input, expected in test_cases:
            z = input[0]
            y = input[1]
            x = input[2]
            with self.subTest(msg=name):
                result = calculate_fill(z,y,x)
                self.assertEqual(result, expected)

    def test_circuit_assembly(self):
        output_command = self.Sample_Circuit.get_command(truth_table=False, expr="AvB")
        curly_brackets = 0
        square_brackets = 0
        double_quotes = 0
        single_quotes = 0
        for c in output_command:
            if c == "{":
                curly_brackets += 1
            elif c == "}":
                curly_brackets -= 1
            
            if c == "[":
                square_brackets += 1
            elif c == "]":
                square_brackets -= 1

            if c == '''"''':
                double_quotes += 1

            if c == "'":
                single_quotes += 1
        self.assertEqual(curly_brackets, 0, msg="unbalanced curly brackets")
        self.assertEqual(square_brackets, 0, msg="unbalanced square brackets")
        self.assertEqual(double_quotes%2, 0, msg="unbalanced double quotes")
        self.assertEqual(single_quotes%2, 0, msg="unbalanced single quotes")

        print(output_command)

if __name__ == '__main__':
    unittest.main()