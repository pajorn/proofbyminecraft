
from nodes import *
from position import *
import arranger

'''
Holds all the logic gates and components, 
denoting a full circuit with all its parts
'''
class Circuit:  
    def __init__(self, list_nodes:list[object], lamp_position: tuple[int,int], redstone_locations: list[list[tuple[int, int]]] = [[], [], []]):
        self.list_nodes = list_nodes
        self.lamp_position = lamp_position
        self.redstone_locations = redstone_locations
        self.different_colours = ['red', 'blue', 'green', 'orange', 'yellow', 'lightblue', 'cyan', 'lime', 'pink', 'magenta','purple', 'brown','light_gray','gray','white','black']
        self.color_assignment = {}
        #hard coded the colors of the variables
        self.base_start = '''summon falling_block ~ ~1 ~ {BlockState:{Name:"redstone_block"},Time:1,Passengers:[{id:"falling_block",BlockState:{Name:"activator_rail"}}'''
        self.spawn_nodes = '''{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='NOT'] run fill ~1 ~-1 ~1 ~-1 ~-1 ~-1 red_wool"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run fill ~1 ~-1 ~1 ~-1 ~-1 ~-1 light_blue_wool"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run fill ~1 ~-1 ~1 ~-1 ~-1 ~-1 orange_wool"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='NOT'] run setblock ~ ~-1 ~-1 minecraft:redstone_lamp"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='NOT'] run setblock ~ ~ ~ red_wool"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='NOT'] run setblock ~ ~ ~-1 redstone_wall_torch[facing=north]"}, {id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='NOT'] run setblock ~ ~ ~1 redstone_wire"}, {id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run setblock ~-1 ~ ~1  repeater[facing=south]"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run setblock ~ ~-1 ~-1 minecraft:redstone_lamp"},
{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run setblock ~1 ~ ~1 repeater[facing=south]"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run setblock ~-1 ~ ~1 repeater[facing=south]"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run fill ~1 ~ ~ ~-1 ~ ~ light_blue_wool"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='OR'] run fill ~ ~ ~ ~ ~ ~-1 redstone_wire"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run setblock ~ ~-1 ~-1 minecraft:redstone_lamp"},
{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run fill ~1 ~ ~ ~-1 ~ ~ orange_wool"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run setblock ~-1 ~ ~1 redstone_wire"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run setblock ~1 ~ ~1 redstone_wire"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run fill ~-1 ~1 ~ ~1 ~1 ~ redstone_torch"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run setblock ~ ~1 ~ redstone_wire"},{id:command_block_minecart,Command:"execute at @e[type=armor_stand,name='AND'] run setblock ~ ~ ~-1 redstone_wall_torch[facing=north]"}, {id:command_block_minecart,Command:"kill @e[type=armor_stand,tag=placer]"}'''
        self.base_end = '''{id:command_block_minecart,Command:"setblock ~ ~ ~1 command_block{Command:\\"fill ~ ~-1 ~-1 ~ ~ ~ air\\"}"},{id:command_block_minecart,Command:"setblock ~ ~-1 ~1 redstone_block"},{id:command_block_minecart,Command:"kill @e[type=command_block_minecart,distance=0..2]"}]}'''
        #choosing box materials
        self.barrier_material = 'smooth_stone'
        self.base_material = 'smooth_sandstone'
        
        #apply colors to the levers
        indexer = 0 
        for modules in self.list_nodes: #assigns colors to levers
            if modules.type == Operation.VAR:
                if modules.var not in self.color_assignment and indexer < len(self.different_colours):
                    self.color_assignment[modules.var] = self.different_colours[indexer]
                    indexer += 1
                #If we have more variables than colors we stop printing the levers with colors
        

    def add_command(self, original_command, new_command):
        added_command = f'id:command_block_minecart,Command:"{new_command}"'
        original_command.append(added_command)
        return original_command

    def get_command(self, truth_table: bool = False, expr: str = ""):
        command = [self.base_start] #apply the starting of the command

        #Bounding box coordinates
        xs = []
        zs = []
        for nodes in self.list_nodes:
            xs.append(nodes.position[0])
            zs.append(nodes.position[1]) 
            left_most = min(xs) - 1
            right_most = max(xs) + 1
            up_most = self.lamp_position[1] - 2
            down_most = max(zs) + 1
        #stupid hardcoded way of finding the bounding box
        #FIXME

        #Displaying expression above
        center = ((right_most/2),(up_most/2))
        title = f"summon text_display ~{center[0]} ~2 ~{center[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[5f,5f,5f]}},billboard:\'center\',text:{{bold:true,color:white,text:\'{expr.strip()}\'}}}}"
        self.add_command(command, title)

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
        barrier = f"fill ~{left_most-1} ~-3 ~{up_most-5} ~{right_most+1} ~-3 ~{down_most-3} {self.barrier_material}"
        self.add_command(command, barrier)
        base = f"fill ~{left_most} ~-3 ~{up_most-4} ~{right_most} ~-3 ~{down_most-4} {self.base_material}"
        self.add_command(command, base)

        #get locations of maps and redstone wiring
        self.redstone_locations = arranger.Arranger.ArrangeRedstone(self.list_nodes)
        self.lamp_position = (self.lamp_position[0], self.lamp_position[1])


        #placing the modules and levers
        for modules in self.list_nodes:
            if modules.type == Operation.NOT:
                name = 'NOT'
            elif modules.type == Operation.AND:
                name = 'AND'
            elif modules.type == Operation.OR:
                name = 'OR'
            elif modules.type == Operation.VAR: #position of levers
                lever_code = f'''{{id:command_block_minecart,Command:"setblock ~{modules.position[0]} ~-2 ~{modules.position[1]-4} lever[face=floor,powered=false]"}}'''
                command.append(lever_code)

                #placing variable colour
                lever_color_code = f'''{{id:command_block_minecart,Command:"setblock ~{modules.position[0]} ~-3 ~{modules.position[1]-4} {self.color_assignment[modules.var]}_concrete"}}'''
                command.append(lever_color_code)

                #placing lever names
                if self.color_assignment[modules.var] == 'orange':
                    lever_label = f'''{{id:command_block_minecart,Command:"summon text_display ~{modules.position[0]} ~-1.3 ~{modules.position[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f], right_rotation:[0f,0f,0f,1f], translation:[0f,0f,0f], scale:[1.7f,1.7f,1.7f]}},billboard:'center', text:{{bold:true, color:gold, text:'{modules.var}'}}}}"}}'''
                    command.append(lever_label)
                else:
                    lever_label = f'''{{id:command_block_minecart,Command:"summon text_display ~{modules.position[0]} ~-1.3 ~{modules.position[1]-4} {{transformation:{{left_rotation:[0f,0f,0f,1f], right_rotation:[0f,0f,0f,1f], translation:[0f,0f,0f], scale:[1.7f,1.7f,1.7f]}},billboard: 'center', text:{{bold:true, color:{self.color_assignment[modules.var]}, text:'{modules.var}'}}}}"}}'''
                    command.append(lever_label)
                continue
            else:
                continue
            
            #actually placing the modules
            code = f'''{{id:command_block_minecart,Command:"/summon armor_stand ~{modules.position[0]} ~-2 ~{modules.position[1]-4} {{Marker:1b,CustomName:\\"{name}\\",Tags:[placer]}}"}}'''
            command.append(code)



        #placing lantern
        lantern_code = f'''{{id:command_block_minecart,Command:"setblock ~{self.lamp_position[0]} ~-2 ~{self.lamp_position[1]-5} redstone_lamp"}},{{id:command_block_minecart,Command:"setblock ~{self.lamp_position[0]} ~-2 ~{self.lamp_position[1]-4} redstone_wire"}}'''
        command.append(lantern_code)

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
        


        command.append(self.spawn_nodes)


        



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
                for modules in self.list_nodes:
                    if modules.type == Operation.VAR: 
                        lever_powered = vars[modules.var]
                        lever_powered_string = "true" if lever_powered else "false"
                        lever_code_table = f'''{{id:command_block_minecart,Command:"setblock ~{modules.position[0]} ~-2 ~{modules.position[1]-4} lever[face=floor,powered={lever_powered_string}]"}}'''
                        command.append(lever_code_table)
            
                
        command.append(self.base_end) #close command
        command = ",".join(command)
        
        return(command)


