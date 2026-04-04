
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
def calculate_fill(z_width:int, y_pos:int, x_width:int)-> str:
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
def calculate_position(directions_list:list[object])->str:
    total_z = 0
    total_y = 0
    total_x = 0
    for steps in directions_list:
        total_z += steps[0]
        total_y += steps[1]
        total_x += steps[2]
    final_coordinates = f"~{total_z} ~{total_y} ~{total_x}"
    return final_coordinates

def calculate_lines(points:list[tuple[int,int]]) -> list[list[tuple[int,int]]] | list[tuple[int,int]]:
    '''
    Calculates where there lines in a matrix of points
    Returns: list of lines, [starting position, ending position]
            & Points that arent connected to lines
    Example:
    sample_lines = [(0,1),(0,0),(0,2),
                    (0,5),(0,6),(0,7),
                    (14,1),(17,6)]

    common_axis_x:
    {0: [(0, 1), (0, 0), (0, 2), (0, 5), (0, 6), (0, 7)], 14: [(14, 1)], 17: [(17, 6)]}
    common_axis_z:
    {1: [(0, 1), (14, 1)], 0: [(0, 0)], 2: [(0, 2)], 5: [(0, 5)], 6: [(0, 6), (17, 6)], 7: [(0, 7)]}

    Has common x: [(0, 1), (0, 0), (0, 2), (0, 5), (0, 6), (0, 7)]

    z_list: [1, 0, 2, 5, 6, 7]

    Sorted In_a_line: [0, 1, 2, 5, 6, 7]

    Z_starts: [0, 5]

    Z_ends: [2, 7]
    lines: [[[(0, 0), (0, 2)], [(0, 5), (0, 7)]], [[(14, 1)], [(17, 6)]]]
    '''
    common_axis_x = {} #list[lines], list[points]
    common_axis_z = {}
    for pt in points: #group all points by common axis
        if not pt[0] in common_axis_x: #create a dictionary entry for each x and z that has a pos
            common_axis_x[pt[0]] = [pt]
        else:
            common_axis_x[pt[0]].append(pt)

        if not pt[1] in common_axis_z:
            common_axis_z[pt[1]] = [pt]
        else:
            common_axis_z[pt[1]].append(pt)
    
    lines_list = []
    points_only = []
    not_in_a_line_x = []
    not_in_a_line_z = []
    for key, pt_list in common_axis_x.items():
        if len(pt_list) > 1:
            in_a_line_z = []
            z_list = []
            
            for pt in pt_list: #list of all z positions
                z_list.append(pt[1])

            for pt in pt_list: #if has in front or behind/ if has neighbour -> add
                if (pt[1] + 1) in z_list:
                    in_a_line_z.append(pt[1])
                elif (pt[1] - 1) in z_list: #only checks if next one is consecutive, should be if any exists in the list
                    in_a_line_z.insert(0, pt[1])
            
            in_a_line_z = sorted(in_a_line_z)

            z_start_places = [in_a_line_z[0] if in_a_line_z else None] #make sure theres something there
            z_end_places = []
            #get the starting position of every line, is also the number of lines on that axis
            for idx, z in enumerate(in_a_line_z): 
                if idx != 0 and (z - 1) != in_a_line_z[idx-1] :
                    z_start_places.append(z)

                elif idx != (len(in_a_line_z)-1) and (z + 1) != in_a_line_z[idx+1]:
                    z_end_places.append(z)
            z_end_places.append(in_a_line_z[-1])

            #add the position of the  start and end of every line
            for i in range(len(z_start_places)): 
                lines_list.append([(key ,z_start_places[i]),(key ,z_end_places[i])])
        
            for pt in pt_list: #add solo points, 
                if not pt[1] in in_a_line_z:
                    not_in_a_line_z.append(pt)

        else: #maybe extend as we are added a full list, no other things on their axis
            not_in_a_line_z.append(pt_list[0]) 


    for key, pt_list in common_axis_z.items():
        if len(pt_list) > 1:
            in_a_line_x = []
            x_list = []
            
            for pt in pt_list: #list of all z positions
                x_list.append(pt[0])
            

            for pt in pt_list: #if has in front or behind/ if has neighbour -> add
                if (pt[0] + 1) in x_list:
                    in_a_line_x.append(pt[0])
                elif (pt[0] - 1) in x_list: #only checks if next one is consecutive, should be if any exists in the list
                    in_a_line_x.insert(0, pt[0])
            
            in_a_line_x = sorted(in_a_line_x)

            x_start_places = [in_a_line_x[0] if in_a_line_x else None] #make sure theres something there
            x_end_places = []
            #get the starting position of every line, is also the number of lines on that axis
            for idx, x in enumerate(in_a_line_x): 
                if idx != 0 and (x - 1) != in_a_line_x[idx-1] :
                    x_start_places.append(x)

                elif idx != (len(in_a_line_x)-1) and (x + 1) != in_a_line_x[idx+1]:
                    x_end_places.append(x)
            x_end_places.append(in_a_line_x[-1])
            

            #add the position of the  start and end of every line
            for i in range(len(x_start_places)): 
                lines_list.append([(x_start_places[i], key),(x_end_places[i], key)])
        
            for pt in pt_list: #add solo points, 
                if not pt[0] in in_a_line_x:
                    not_in_a_line_x.append(pt)

        else: #maybe extend as we are added a full list, no other things on their axis
            not_in_a_line_x.append(pt_list[0]) 

    #print("common_axis_x:")
    #print(common_axis_x)
    #print("common_axis_z:")
    #print(common_axis_z)
    #print(f"\nHas common x: {pt_list}")
    #print(f"\nz_list: {x_list}")
    #print(f"\nSorted In_a_line: {in_a_line_z}")
    #print(f"\nZ_starts: {z_start_places}")
    #print(f"\nZ_ends: {z_end_places}")
    #print(f"not_in_a_line_x: {not_in_a_line_x}")
    #print(f"not_in_a_line_z: {not_in_a_line_z}")
    for pt in points: #no common x or z with anything
        if (pt in not_in_a_line_x) and (pt in not_in_a_line_z):
            points_only.append(pt)

    return lines_list,points_only

class Component: #each redstone block
    '''
    Defines the Position and type of Block each logicgate

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
    
    def __init__(self, directions_list:list[object], block:str):
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
    def __init__(self, color:str=None, base_length:int=3, name:str=None):
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
    '''
    Denotes a full build/circuit. Redstone lines are determined 
    by the position of logic gates.
    '''
    def __init__(self, list_nodes:list[object], lamp_position: tuple[int,int]):
        self.list_nodes = list_nodes
        self.lamp_position = lamp_position
        self.color_dict = {'A':'red', 'B':'blue', 'C':'green', 'D':'orange', 'E':'yellow', 
                           'F':'lightblue', 'G':'cyan', 'H':'lime', 'I':'pink', 
                           'J':'magenta', 'K':'purple', 'L':'brown','M':'light_gray',
                           'N':'gray','O':'white','P':'black'}
        #hard coded the colors of the variables
        self.base_start = '''summon falling_block ~ ~1 ~ {BlockState:{Name:"redstone_block"},Time:1,Passengers:[{id:"falling_block",BlockState:{Name:"activator_rail"}}'''
        self.base_end = '''{id:command_block_minecart,Command:"setblock ~ ~ ~1 command_block{Command:\\"fill ~ ~-1 ~-1 ~ ~ ~ air\\"}"},{id:command_block_minecart,Command:"setblock ~ ~-1 ~1 redstone_block"},{id:command_block_minecart,Command:"kill @e[type=command_block_minecart,distance=0..2]"}]}'''
        #choosing box materials
        self.barrier_material = 'smooth_stone'
        self.base_material = 'smooth_sandstone'

    def spawn_nodes(self, command_line:str)->str:
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

    def bounding_box(self, node_list:list[object]):
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
    
    def add_title_equation(self, command:str, expr:str, position:tuple[int,int]):
        '''
        Adds the equation of the expression on top of the circuit
        '''
        y_position = 2
        title = f"summon text_display ~{position[0]} ~{y_position} ~{position[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[5f,5f,5f]}},billboard:\'center\',text:{{bold:true,color:white,text:\'{expr.strip()}\'}}}}"
        self.add_command(command, title)

    def add_circuit_base(self, command:str, left_most:int, right_most:int, 
                         up_most:int, down_most:int, base_material:str, border_material:str) -> str:
        '''
        Adds the base of the circuit and its border
        '''
        border = f"fill ~{left_most-1} ~-3 ~{up_most-5} ~{right_most+1} ~-3 ~{down_most-3} {border_material}"
        self.add_command(command, border)

        base = f"fill ~{left_most} ~-3 ~{up_most-4} ~{right_most} ~-3 ~{down_most-4} {base_material}"
        self.add_command(command, base)
        return command

    def add_markers(self, command:str, node_list:list[object]) -> str:
        '''
        Goes through the node list and places their corresponding markers 
        at their listed position

        Possible nodes: AND, OR, NOT, variables
        '''
        offset_down = -4

        for nodes in node_list:
            match nodes.type:
                case Operation.NOT:
                    name = 'NOT'
                case Operation.AND:
                    name = 'AND'
                case Operation.OR:
                    name = 'OR'
                case Operation.VAR: #position of levers
                    #compartmentalise levers too?
                    lever_code = f"setblock ~{nodes.position[0]} ~-2 ~{nodes.position[1]+offset_down} lever[face=floor,powered=false]"
                    self.add_command(command, lever_code)

                    #placing variable colour
                    lever_color_code = f"setblock ~{nodes.position[0]} ~-3 ~{nodes.position[1]+offset_down} {self.color_dict[nodes.var]}_concrete"
                    self.add_command(command, lever_color_code)
                    

                    #placing lever names
                    if self.color_dict[nodes.var] == 'orange': #no orange text so we use gold, edge case
                        orange_lever_label = f"summon text_display ~{nodes.position[0]} ~-1.3 ~{nodes.position[1]+offset_down} {{transformation:{{left_rotation:[0f,0f,0f,1f], right_rotation:[0f,0f,0f,1f], translation:[0f,0f,0f], scale:[1.7f,1.7f,1.7f]}},billboard:'center', text:{{bold:true, color:gold, text:'{nodes.var}'}}}}"
                        self.add_command(command, orange_lever_label)
                    else: 
                        lever_label = f"summon text_display ~{nodes.position[0]} ~-1.3 ~{nodes.position[1]+offset_down} {{transformation:{{left_rotation:[0f,0f,0f,1f], right_rotation:[0f,0f,0f,1f], translation:[0f,0f,0f], scale:[1.7f,1.7f,1.7f]}},billboard: 'center', text:{{bold:true, color:{self.color_dict[nodes.var]}, text:'{nodes.var}'}}}}"
                        self.add_command(command, lever_label)
                    continue

                case _: #default case
                    name = 'UNKNOWN' 
            
            #actually placing the nodes, using placement markers to reduce code and computation load
            #offset down by 4, shoudl probably this at an earlier state FIXME
            code = f'''/summon armor_stand ~{nodes.position[0]} ~-2 ~{nodes.position[1]+offset_down} {{Marker:1b,CustomName:\\"{name}\\",Tags:[placer]}}'''
            self.add_command(command, code)
        return command
    
    def set_redstone_wires(self, command:str, redstone_locations:list[tuple[int,int]]) -> str:
        '''
        Sets the positions of the redstone wires and repeater between circuits.
        '''
        # Given that the redstone wires are straight lines by design, it would
            # be optimal to replace the setblocks with fills, however, we do not
            # have time.
        offset = -4
        
        lines, points = calculate_lines(redstone_locations[0])
        print(f"lines: {lines}, \npoints: {points}")

        for pos in points:
            command = self.add_command(command, f"setblock ~{pos[0]} ~-2 ~{pos[1]+offset} redstone_wire")
        for ln in lines: #[line[position1(x,z),position2(x,z]]
            command = self.add_command(command, f"fill ~{ln[0][0]} ~-2 ~{ln[0][1]+offset} ~{ln[1][0]} ~-2 ~{ln[1][1]+offset} redstone_wire")


        # Place up facing repeaters
        for pos in redstone_locations[1]:
            self.add_command(command, f"setblock ~{pos[0]} ~-2 ~{pos[1]+offset} repeater[facing=south]")
        # Place left facing repeaters
        for pos in redstone_locations[2]:
            self.add_command(command, f"setblock ~{pos[0]} ~-2 ~{pos[1]+offset} repeater[facing=east]")
        return command

    def get_command(self, truth_table: bool = False, expr: str = ""):
        command = [self.base_start] #apply the starting of the command

        #Bounding box coordinates
        left_most, right_most, up_most, down_most, center= self.bounding_box(self.list_nodes)

        #Displaying expression above
        self.add_title_equation(command, expr, center)

        #hardcoded barriers around circuits
        self.add_circuit_base(command, left_most, right_most, 
                              up_most, down_most, self.base_material, self.barrier_material)
    
        #get locations of maps and redstone wiring
        #Conflicts with initial injection to the Circuit object FIXME
        self.redstone_locations = arranger.Arranger.ArrangeRedstone(self.list_nodes)
        self.lamp_position = (self.lamp_position[0], self.lamp_position[1])

        #sets markers for the gates and variables
        self.add_markers(command,self.list_nodes)
        
        #placing lantern TODO
        lantern_position = f'''setblock ~{self.lamp_position[0]} ~-2 ~{self.lamp_position[1]-5} redstone_lamp'''
        redstone_to_lantern =f"setblock ~{self.lamp_position[0]} ~-2 ~{self.lamp_position[1]-4} redstone_wire"
        self.add_command(command, lantern_position)
        self.add_command(command, redstone_to_lantern)

        #set wiring needed
        self.set_redstone_wires(command, self.redstone_locations)
        
        #trigger construction of all components at their markers
        self.spawn_nodes(command) 
        
        #spacing for the truth table, in x direction only, 
        # works weirdly because we use clone for truth tables TODO
        rightmost_x = 0
        for node in self.list_nodes:
            if node.position[0] > rightmost_x:
                rightmost_x = node.position[0]
        offset_x = rightmost_x + 3

        #finding the levers which are on and off for the truth table, 
        # cloning step out of order FIXME
        vars = {}
        for node in self.list_nodes:
            if node.var:
                vars[node.var] = False
        
        vars = dict(sorted(vars.items()))

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
    sample_lines = [(1,0),(2,0),(3,0),
                    (7,1),(7,2),(7,0),
                    (7,12)]
    print(f"lines: {calculate_lines(sample_lines)}")