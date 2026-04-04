from parser import FOLe
from nodes import Node, Operation
from worldgen import*
from arranger import Arranger
from command import *
import traceback

def ValidInput(expr) -> bool:
    if len(expr) < 3: #must have at least 2 variables and an operand to be a valid boolean equation
        return False
    
    var_count = 0   #variable count
    op_count = 0    #operation count
    bk_count = 0    #bracket count

    for character in expr:
        if character in ['(',')']:
            bk_count += 1
        elif character.isalpha():
            var_count += 1
        elif character in ['^','v']:
            op_count += 1
    
    if op_count == var_count - 1 and bk_count%2 == 0:
        return True #checking integrity of the expression
    else: 
        return False

def process_input(expr, truth_table: bool = False) -> str:
    """This function processes the text passed to it and returns command
    for gui shit."""
    #TODO better error handling with more informative error messages
    # Unequal brackets, foreign objects, double operands vv, empty expr
    try:
        root = FOLe.CreateGraph(expr.strip())
        nodes = Arranger.ArrangeGates(root) 
        circuit = Circuit(nodes, (root.position[0], root.position[1]-2))
        out = circuit.get_command(truth_table, expr)
    except Exception as e:
        traceback.print_exc()
        return f'processing error: {e}'
    return out
