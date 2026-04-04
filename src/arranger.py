from parser import *
import level
import command

class Arranger:
    def ArrangeGates(root: Node) -> list[Node]:
        """
        Return a list of nodes with all their position values populated
        for use with Circuit class.
        """
        nodes = level.PostT(root)

        max_level = 0

        # Populate all level values
        for i in range(len(nodes)):
            nodes[i].level = level.GetLevel(nodes[i])
            if nodes[i].level > max_level:
                max_level = nodes[i].level

        # Set positions for level 0 (variables)
        node_indices = [i for i in range(len(nodes)) if nodes[i].level == 0]
        for i in range(len(node_indices)):
            nodes[node_indices[i]].position = (4*i + 1, 0)

        # Set positions for level i in [1, max_level]
        for i in range(1, max_level+1):
            node_indices = [j for j in range(len(nodes)) if nodes[j].level == i]
            for j in range(len(node_indices)):
                isNot = nodes[node_indices[j]].type == Operation.NOT
                nodes[node_indices[j]].position = (nodes[node_indices[j]].left.position[0] + (0 if isNot else 1), -(3 + 4*(i-1)))

        return nodes
    
    def ArrangeRedstone(nodes: list[Node]) -> list[list[tuple[int, int]]]:
        """
        Return a list of lists of redstone locations.

        Parameters:
            nodes -- A list of nodes with position values populated as
                     per ArrangeGates()
        Return format:
            list:
                1. list[tuple] -- redstone wire locations
                2. list[tuple] -- up facing redstone repeater locations
                3. list[tuple] -- left facing redstone repeater locations
        """
        # TODO: Add repeaters here

        wire_locations = []
        up_repeaters = []
        left_repeaters = []

        for node in nodes:
            # Wire locations for left inputs
            if node.left:
                ChildIsVar = node.left.type == Operation.VAR
                for i in range(node.left.position[1]-(1 if ChildIsVar else 2) - (node.position[1]+2) + 1):
                    wire_locations.append((node.left.position[0], node.position[1]+2 + i))
                    if not (i+2) % 15:
                        up_repeaters.append((node.left.position[0], node.position[1]+2 + i))
                # wire_locations.extend([(node.left.position[0], i) for i in range(node.left.position[1]-(1 if ChildIsVar else 2), node.position[1]+1, -1)])
                # print(f"{node.level}: ({node.left.position[0]}, {node.position[1]+2}), ({node.left.position[0]}, {node.left.position[1]-(1 if ChildIsVar else 2)})")
            
            # Wire locations for right inputs
            if node.right:
                ChildIsVar = node.right.type == Operation.VAR

                # Horizontal wires
                for i in range((node.right.position[0]+1) - (node.position[0]+1)):
                    wire_locations.append((node.position[0]+1 + i, node.position[1]+2))
                    if not (i+2) % 13 and i != (node.right.position[0]+1) - (node.position[0]+1) - 1:
                        left_repeaters.append((node.position[0]+1 + i, node.position[1]+2))
                
                # Vertical wires
                for i in range(node.right.position[1]-(1 if ChildIsVar else 2) - (node.position[1]+2) + 1):
                    if (node.right.position[0], node.position[1]+2 + i) not in wire_locations:
                        wire_locations.append((node.right.position[0], node.position[1]+2 + i))
                    if not (i+2) % 15 and i != node.right.position[1]-(1 if ChildIsVar else 2):
                        up_repeaters.append((node.right.position[0], node.position[1]+2 + i))
                    # Blanket fix for edge case - (((((a^b)^c)^d)^e)^f)vg
                    if (node.right.position[0], node.position[1]+3) in wire_locations and (node.right.position[0], node.position[1]+3) not in up_repeaters:
                        up_repeaters.append((node.right.position[0], node.position[1]+3))


                # wire_locations.extend([(i, node.position[1]+2) for i in range(node.position[0]+1, node.right.position[0]+1)])
        
        return [wire_locations, up_repeaters, left_repeaters]

def do_shit(expr, truth_table=False):
    root = FOLe.CreateGraph(expr)
    
    nodes = Arranger.ArrangeGates(root)
    
    circuit = command.Circuit(nodes, (root.position[0], root.position[1]-2))
    print(circuit.get_command(truth_table))

if __name__ == "__main__" and False:
    print(f"test2: {test2}")
    do_shit(test2)
    # for pos in Arranger.ArrangeRedstone(nodes):
    #     print(pos)
