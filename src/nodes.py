from enum import Enum

class Node:
    def __init__(self):
        self.parent: Node = None
        self.left: Node | str = None #left child
        self.right: Node | str = None #right child

        self.type: Operation = None
        self.var: str | None = None #var types have str data
        self.position: tuple | None = None

        self.depth = 0 #number of parents to root
        self.level = 0 #testing maybe delete
        self.offset = 0 #set by SetOffset in level.py after a graph is made into list
        #what is offset

    def __repr__(self):
        return f"Node(type={self.type}, var={self.var})"


class Operation(Enum):
    VAR = 0
    NOT = 1
    AND = 2
    OR = 3
