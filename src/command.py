
from nodes import *
import arranger
from enum import Enum

class Direction(tuple, Enum):
    '''
    Directions for positioning redstone components
          |                     ^ Y
          |                     |
    -------------> X      -------------> X & Z
          |                     |
          |                     |
         \/ Z
    '''
    UP = (0,0,-1)
    DOWN = (0,0,1)
    LEFT = (-1,0,0)
    RIGHT = (1,0,0)
    Y_UP = (0,1,0)
    Y_DOWN = (0,-1,0)

'''
    Calculates the coordinates for a box with dimensions, z_width, x_width at position y_pos

    calculate_fill(3,0,3) -> ~1 ~0 ~1 ~-1 ~0 ~-1
    calculate_fill(5,-1,5) -> ~2 ~-1 ~2 ~-2 ~-1 ~-2
''' #create proper calculate fill
def calculate_fill(z_width, y_pos, x_width):
        return f"~{z_width//2} ~{y_pos} ~{x_width//2} ~-{z_width//2} ~{y_pos} ~-{x_width//2}"
    
'''
    Calculates the coordinates of a position, depending on the steps listed
    [Directions.UP] -> ~0 ~0 ~-1
    [Directions.UP, Directions.LEFT] -> ~-1 ~0 ~-1

          |                     ^ Y
          |                     |
    -------------> X      -------------> X & Z
          |                     |
          |                     |
         \/ Z

    ---------------------------------
    |  UP+LEFT  |  UP   |  UP+RIGHT |
    |--------------------------------
    |    LEFT   | center|   RIGHT   |
    ---------------------------------
    | DOWN+LEFT |  DOWN | DOWN+RIGHT|
    ---------------------------------
'''    
def calculate_position(directions_list):
    total_z = 0
    total_y = 0
    total_x = 0
    for steps in directions_list:
        total_z += steps[0]
        total_y += steps[1]
        total_x += steps[2]
    final_coordinates = f"~{total_z} ~{total_y} ~{total_x}"
    return final_coordinates

class Component: #each redstone block
    '''
    Defines the Position and type of Block on the circuit

    Component([Direction.UP], "redstone_repeater")
    Component([], "wool")
    Component([Direction.DOWN, Direction], "redstone_repeater")
    --------------------------------
    |         | repeater |         |
    |-------------------------------
    |         |    wool  |         |
    --------------------------------
    |         |          | redstone|
    --------------------------------
    '''
    
    def __init__(self, directions_list, block):
        self.position = calculate_position(directions_list)
        self.code =  f"setblock {self.position} {block}"

class Logic_Gate:
    '''
    Parent class and constructor for any logic gate

    Params:
    color = color scheme of the circuit
    baselength = wedith of the square base
    name = name of circuit
    '''
    def __init__(self, color=None, base_length=3, name=None):
        self.name = name
        self.color = color
        self.base_length = base_length
        self.base = f"fill {calculate_fill(base_length, -1, base_length)} {color}_wool"        
        
class Not_Gate(Logic_Gate):
    def __init__(self):
        super().__init__("red", 3, "NOT")
        self.parts = [Component([],"red_wool"), Component([Direction.DOWN],"redstone_wire"), 
                      Component([Direction.UP],"redstone_wall_torch[facing=north]")]

class AND_Gate(Logic_Gate):
    def __init__(self):
        super().__init__("orange",3, "AND")
        self.parts = [Component([Direction.UP], "redstone_wall_torch[facing=north]"),
                      Component([],"orange_wool"), Component([Direction.LEFT],"orange_wool"),Component([Direction.RIGHT],"orange_wool"),
                      Component([Direction.Y_UP],"redstone_wire"), Component([Direction.LEFT,Direction.Y_UP],"redstone_torch"),Component([Direction.RIGHT,Direction.Y_UP],"redstone_torch"),
                      Component([Direction.DOWN,Direction.LEFT],"redstone_wire"), Component([Direction.DOWN,Direction.RIGHT],"redstone_wire")]

class OR_Gate(Logic_Gate):
    def __init__(self):
        super().__init__("light_blue", 3, "OR")
        self.parts = [Component([Direction.UP], "redstone_wire"),
                      Component([],"redstone_wire"), Component([Direction.LEFT],"light_blue_wool"),Component([Direction.RIGHT],"light_blue_wool"),
                      Component([Direction.DOWN,Direction.LEFT],"repeater[facing=south]"), Component([Direction.DOWN,Direction.RIGHT],"repeater[facing=south]")]
        

'''
Holds all the logic gates and components, 
denotes a full circuit with all its parts
'''
class Circuit:  
    def __init__(self, list_nodes:list[object], lamp_position: tuple[int,int], 
                 redstone_locations: list[list[tuple[int, int]]] = [[], [], []]):
        self.list_nodes = list_nodes
        self.lamp_position = lamp_position
        self.redstone_locations = redstone_locations
        self.color_dict = {'A':'red', 'B':'blue', 'C':'green', 'D':'orange', 'E':'yellow', 
                           'F':'lightblue', 'G':'cyan', 'H':'lime', 'I':'pink', 
                           'J':'magenta', 'K':'purple', 'L':'brown','M':'light_gray',
                           'N':'gray','O':'white','P':'black'}
        self.color_assignment = {}
        #hard coded the colors of the variables
        self.base_start = '''summon falling_block ~ ~1 ~ {BlockState:{Name:"redstone_block"},Time:1,Passengers:[{id:"falling_block",BlockState:{Name:"activator_rail"}}'''
        self.base_end = '''{id:command_block_minecart,Command:"setblock ~ ~ ~1 command_block{Command:\\"fill ~ ~-1 ~-1 ~ ~ ~ air\\"}"},{id:command_block_minecart,Command:"setblock ~ ~-1 ~1 redstone_block"},{id:command_block_minecart,Command:"kill @e[type=command_block_minecart,distance=0..2]"}]}'''
        #choosing box materials
        self.barrier_material = 'smooth_stone'
        self.base_material = 'smooth_sandstone'

    def spawn_nodes(self, command_line):
        '''
        Spawns the actual circuits at the markers

        Ex. Spawn the Not circuit at every NOT_armour_stand marker
        '''
        gate_list = [Not_Gate(), AND_Gate(), OR_Gate()]
        for gates in gate_list: #For every type of circuit
            base_code = f'''execute at @e[type=armor_stand,name='{gates.name}'] run {gates.base}''' #adding the base
            self.add_command(command_line, base_code)
            for components in gates.parts: #adding components
                node_code = f'''execute at @e[type=armor_stand,name='{gates.name}'] run {components.code}'''
                self.add_command(command_line, node_code)
        return command_line

    def add_command(self, original_command, new_command):
        '''
        Appends a new command to the command block line

        Since every individual command must be wrapped and executed 
        using a falling command block minecart.
        To reduce redundant code and reduce errors
        '''
        #unsecured quotations
        added_command = f'''{{id:command_block_minecart,Command:"{new_command}"}}'''
        original_command.append(added_command)
        return original_command

    def bounding_box(self, node_list):
        '''
        Gives the ranges of the bounding box of the circuit and 
        the center coordinate as a tuple
        left_most, right_most, up_most, down_most :int
        center: tuple[int,int]
        '''
        xs = []
        zs = []
        for nodes in node_list:
            xs.append(nodes.position[0])
            zs.append(nodes.position[1]) 
            left_most = min(xs) - 1
            right_most = max(xs) + 1
            up_most = self.lamp_position[1] - 2
            down_most = max(zs) + 1
        center = ((right_most/2),(up_most/2))
        return left_most, right_most, up_most, down_most, center
        #stupid hardcoded way of finding the bounding box
        #FIXME
    
    def add_title_equation(self, command, expr, position):
        '''
        Adds the equation of the expression on top of the circuit
        '''
        y_position = 2
        title = f"summon text_display ~{position[0]} ~{y_position} ~{position[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[5f,5f,5f]}},billboard:\'center\',text:{{bold:true,color:white,text:\'{expr.strip()}\'}}}}"
        self.add_command(command, title)

    def add_circuit_base(self, command, left_most, right_most, up_most, down_most, base_material, border_material):
        '''
        Adds the base of the circuit and its border
        '''
        border = f"fill ~{left_most-1} ~-3 ~{up_most-5} ~{right_most+1} ~-3 ~{down_most-3} {border_material}"
        self.add_command(command, border)

        base = f"fill ~{left_most} ~-3 ~{up_most-4} ~{right_most} ~-3 ~{down_most-4} {base_material}"
        self.add_command(command, base)
        return command


    def get_command(self, truth_table: bool = False, expr: str = ""):
        command = [self.base_start] #apply the starting of the command

        #Bounding box coordinates
        left_most, right_most, up_most, down_most, center= self.bounding_box(self.list_nodes)

        #Displaying expression above
        self.add_title_equation(command, expr, center)

        #find the rightmost node and add a gap since we are too stupid to arrage them largest to smallest
        #why only along the x direction?
        rightmost_x = 0
        for node in self.list_nodes:
            if node.position[0] > rightmost_x:
                rightmost_x = node.position[0]
        offset_x = rightmost_x + 3

        #finding the levers which are on and off for the truth table
        vars = {}
        for node in self.list_nodes:
            if node.var:
                vars[node.var] = False
        
        vars = dict(sorted(vars.items()))

        #hardcoded barriers around circuits
        self.add_circuit_base(command, left_most, right_most, 
                              up_most, down_most, self.barrier_material, self.base_material)
        

        #get locations of maps and redstone wiring
        self.redstone_locations = arranger.Arranger.ArrangeRedstone(self.list_nodes)
        self.lamp_position = (self.lamp_position[0], self.lamp_position[1])


        #placing the circuits and levers
        for nodes in self.list_nodes:
            match nodes.type:
                case Operation.NOT:
                    name = 'NOT'
                case Operation.AND:
                    name = 'AND'
                case Operation.OR:
                    name = 'OR'
                case Operation.VAR: #position of levers
                    #compartmentalise levers too?
                    lever_code = f"setblock ~{nodes.position[0]} ~-2 ~{nodes.position[1]-4} lever[face=floor,powered=false]"
                    self.add_command(command, lever_code)

                    #placing variable colour
                    lever_color_code = f"setblock ~{nodes.position[0]} ~-3 ~{nodes.position[1]-4} {self.color_assignment[nodes.var]}_concrete"
                    self.add_command(command, lever_color_code)

                    #placing lever names
                    if self.color_assignment[nodes.var] == 'orange': #no orange text so we use gold, edge case
                        orange_lever_label = f"summon text_display ~{nodes.position[0]} ~-1.3 ~{nodes.position[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f], right_rotation:[0f,0f,0f,1f], translation:[0f,0f,0f], scale:[1.7f,1.7f,1.7f]}},billboard:'center', text:{{bold:true, color:gold, text:'{nodes.var}'}}}}"
                        self.add_command(command, orange_lever_label)
                    else:
                        lever_label = f"summon text_display ~{nodes.position[0]} ~-1.3 ~{nodes.position[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f], right_rotation:[0f,0f,0f,1f], translation:[0f,0f,0f], scale:[1.7f,1.7f,1.7f]}},billboard: 'center', text:{{bold:true, color:{self.color_assignment[nodes.var]}, text:'{nodes.var}'}}}}"
                        self.add_command(command, lever_label)
                    continue

                case _: #default case
                    name = 'UNKNOWN' 
            
            #actually placing the nodes, using placement markers to reduce code and computation load
            code = f'''/summon armor_stand ~{nodes.position[0]} ~-2 ~{nodes.position[1]-4} {{Marker:1b,CustomName:\\"{name}\\",Tags:[placer]}}'''
            self.add_command(command, code)

        #placing lantern
        lantern_position = f'''setblock ~{self.lamp_position[0]} ~-2 ~{self.lamp_position[1]-5} redstone_lamp'''
        redstone_to_lantern =f"setblock ~{self.lamp_position[0]} ~-2 ~{self.lamp_position[1]-4} redstone_wire"
        self.add_command(command, lantern_position)
        self.add_command(command, redstone_to_lantern)

        # Given that the redstone wires are straight lines by design, it would
            # be optimal to replace the setblocks with fills, however, we do not
            # have time.
        for pos in self.redstone_locations[0]:
            command.append(f'''{{id:command_block_minecart,Command:"setblock ~{pos[0]} ~-2 ~{pos[1]-4} redstone_wire"}}''')
            
        # Place up facing repeaters
        for pos in self.redstone_locations[1]:
            command.append(f'''{{id:command_block_minecart,Command:"setblock ~{pos[0]} ~-2 ~{pos[1]-4} repeater[facing=south]"}}''')
            
        # Place left facing repeaters
        for pos in self.redstone_locations[2]:
            command.append(f'''{{id:command_block_minecart,Command:"setblock ~{pos[0]} ~-2 ~{pos[1]-4} repeater[facing=east]"}}''')
        
        command = self.spawn_nodes(command) #trigger construction of all components at markers


        if truth_table:
            structure_x = abs(right_most-left_most)+3
            structure_y = abs(up_most - down_most)+3
            structure_block_save = f'''{{id:command_block_minecart,Command:"setblock ~{left_most-1} ~3 ~{up_most-5} structure_block[mode=save]{{name:'module',posX:0,posY:-6,posZ:0,sizeX:{structure_x},sizeY:5,sizeZ:{structure_y},rotation:'NONE',mirror:'NONE',mode:'SAVE',ignoreEntities:0b,showboundingbox:1b}} replace"}},{{id:command_block_minecart,Command:"setblock ~{left_most-1} ~4 ~{up_most-5} redstone_block"}}'''
            structure_block_break = f'''{{id:command_block_minecart,Command:"fill ~{left_most-1} ~3 ~{up_most-5} ~{left_most-1} ~4 ~{up_most-5} air"}}'''
            command.extend([structure_block_save,structure_block_break])
        
        for i in range(1 if not truth_table else (2 ** len(vars))):

            #Deciding truth table lever on or off
            keys = list(vars.keys())
            for j in range(len(keys)):
                vars[keys[j]] = ((i >> (len(keys)-1-j)) & 1) == 1

            if i != 0:
                left_most += offset_x
                right_most += offset_x
                structure_x = abs(right_most-left_most)+3
                structure_y = abs(up_most - down_most)+3
                structure_block_load = f'''{{id:command_block_minecart,Command:"setblock ~{left_most-1} ~-2 ~{up_most-5} structure_block[mode=load]{{name:'module',posX:0,posY:-1,posZ:0,sizeX:{structure_x},sizeY:5,sizeZ:{structure_y},rotation:'NONE',mirror:'NONE',mode:'LOAD',ignoreEntities:0b,showboundingbox:1b}} replace"}},{{id:command_block_minecart,Command:"setblock ~{left_most-1} ~-1 ~{up_most-5} redstone_block"}}'''
                command.extend([structure_block_load])

                #placing truth tables levers
                for nodes in self.list_nodes:
                    if nodes.type == Operation.VAR: 
                        lever_powered = vars[nodes.var]
                        lever_powered_string = "true" if lever_powered else "false"
                        lever_code_table = f'''{{id:command_block_minecart,Command:"setblock ~{nodes.position[0]} ~-2 ~{nodes.position[1]-4} lever[face=floor,powered={lever_powered_string}]"}}'''
                        command.append(lever_code_table)
            
        command.append(self.base_end) #close command
        command = ",".join(command)
        return(command)

if __name__ == "__main__" and False:
    start_string = ["start"]
    end_string = spawn_nodes(start_string)
    print(end_string)