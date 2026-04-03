from parser import *
from nodes import *

#assigns every gate level number

# class Node:
#     def __init__(self):
#         self.parent: Node = None
#         # str types refer to variables
#         self.left: Node | str = None
#         self.right: Node | str = None
#         self.type: Operation = None
#         self.var: str | None = None
#         self.depth = 0 #number of parents to root

#         self.level = 0 #testing maybe delete

# def GetVars(nodes):
#     vars = []
#     for node in nodes:

#     return


def GetLctn(node): #not used
    """return the an (x,y) coordinate tuple of a node
        TODO
    """
    out = (node.offset, node.level) #tuple of (x, y) coords kinda
    return out

#TODO the setting stuff better
def SetLevels(nodes: list[Node]): #the offset of each node is it's position in the list
    for i in range(len(nodes)):
        nodes[i].offset = i
    pass 

def SetOffset(nodes: list[Node]):
    """
    takes list of nodes and then sets their offsets from left to right
    """
    for node in nodes:
        node.offset = nodes.index(node) #offset of each node is the first place the node appears in the list
    pass

def PostT(node):
    """returns post ordered list of Nodes
   
   PostT(FOLe.CreateGraph(test1))
   ['a', 'b', <Operation.AND: 2>, 'a', 'c', <Operation.AND: 2>, <Operation.OR: 3>] 
    """

    out = []
    if node == None:
        return out #If no nodes, just return the empty list

    out.extend(PostT(node.left)) #add the children to out
    out.extend(PostT(node.right))

    # if hasattr(node, 'var') and node.var is not None:
    #     out.append(node.var)
    # elif hasattr(node, 'type'):
    #     out.append(node.type)
    if node:
        out.append(node) #finally append the actual node to 'out'
    else:
        out.append(None) #redundant check since it can't be empty

    return out

def GetLevel(node):

    """should returns the level of the node

        0 level is furthest left and then higher level means more right

        Level
        -------------------->
        _______________
        0 | 1 | 2 | ...
        a | ^ | v |
        b | ^ |   |
        a |   |   |
        c |   |   |
        ---------------


        level(node) = 1 + max(level(childs))

         (a^b)v(a^c)
         L=2    OR
              /   |
         L=1 AND   AND
            / |   / |
      L=0  a  b  a   c

    """

    child_level = [] #levels of the children
    if node is None: #base case? Because the default is none? Error protection?
        return 0
    
    if node.type == Operation.VAR: #if it variable then return 0, must be the bottom level
        return 0
    
    if node.left: #recursive
        child_level.append(GetLevel(node.left)) # get level left child
    if node.right:
        child_level.append(GetLevel(node.right)) # get level right child

    node.level = 1 + max(child_level)
    return node.level

test1 = "(a^b)v(a^c)"
test2 = "(av(bvc))^~(a^(bvc))"
edge1 = "a v b"



