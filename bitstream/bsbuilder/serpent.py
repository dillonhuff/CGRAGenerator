#!/usr/bin/python

import sys;
import re;

# from ../decoder/lib import cgra_info
sys.path.append("../decoder")
from lib import cgra_info
from lib import connect_tiles

def main():
    # test_connect_tiles()
    # sys.exit(0)
    # notes()

    print '######################################################'
    print '# serpent.py: Read cgra info'
    cgra_filename = get_default_cgra_info_filename()
    cgra_info.read_cgra_info(cgra_filename)


    print '######################################################'
    print '# serpent.py: Initialize node and tile data structures'
    init_tile_resources(DBG=1)
    build_nodes(DBG=1)
    initialize_routes()
    initialize_node_INPUT()

    print '########################################'
    print '# serpent.py: constant folding'
    constant_folding(DBG=1)
    print "# consts should be gone now"

    print '########################################'
    print '# serpent.py: register folding'
    register_folding()

    # Happens automatically as long as we process non-regop regs LAST (right?)
    # print '######################################################'
    # print '# serpent.py: Process and optimize INPUT node'
    # process_input()

    print '######################################################'
    print '# serpent.py: Process remaining nodes, starting with INPUT'
    process_nodes('INPUT')

    # TODO/FIXME Special treatment for OUTPUT?
    # note OUTPUT wire is always wire_m1_1_BUS16_S1_T0

    sys.exit(0)


def notes():
    print "Read the dotfile input make make a list of dests for each node"
    print "Process all the constants"
    print "Process all the reg->pe pairs"
    print "Process all node->regall groups"
    print "  -> out[node] = (list of regs), combined[reg] = node"
    print "Start with INPUT node"
    print "  if pe in dests: combine pe into input tile, mark it processed"
    print "    -> pe (and optional input reg) will get assigned a tile,"
    print "       indicating that they have been processed."
    print "  elif reg-pe combo in dests:"
    print "    combine pe into input tile, mark it processed"
    print "  else no combinings"
    print "  foreach remaining dest d:"
    print "    if pe: assign a nearby tile; recurse on dests (RD)"
    print "    elif mem: assign a nearby tile; recurse on dests (RD)"
    print "    elif unprocessed reg: "
    print "      # all combinings have been done, yes? maybe not quite..."
    print "      assign a nearby tile"
    print "      if all dests are unassigned regs, assign a double reg"
    print "      recurse on dests"
    print "    elif processed reg: "
    print "      recurse on dests"


def test_connect_tiles():
    cgra_filename = get_default_cgra_info_filename()
    cgra_info.read_cgra_info(cgra_filename)
    connect_tiles.test_ctsr()
    connect_tiles.test_ctsc()



# Maybe this should be part of cgra library, yes?
def get_default_cgra_info_filename():
    '''
    Look for default cgra_info file in <decoder-directory>/examples/cgra_info.txt
    '''
    import os
    mydir = os.path.dirname(os.path.realpath(__file__))
    cgra_filename = mydir + "../decoder/examples/cgra_info.txt"

    VERBOSE=0
    # global verbose #(implied because use before def)
    if VERBOSE: print("I think I am here:\n  %s" % mydir)
    if VERBOSE: print("Default cgra_info file is\n  %s" % cgra_filename)
    return cgra_filename

# Final result:
# Tile 0: INPUT => reg1 => add 16 => reg1,reg2
# tile[0].nodes = ["add1"]
# tile[0].op1   = ["INPUT", "reg1"]
# tile[0].op2   = ["const16_16"]
# tile[0].out   = ["reg1", "reg2"]

# Tile 1: two registers
# tile[0].op1   = ["reg3"]
# tile[0].out   = ["reg4", "reg5"]

# Reverse lookup
# node["add1"] = (0,"node")
# node["reg1"] = (0, "op1")


        # Tile numbers for each node e.g.
        #  tile["mul_49119_492_PE"] = 14

class Node:
    def __init__(self, nodename):
        self.name = nodename
        self.tileno = -1 # Because 0 is a valid tile number, see?

        # FIXME are these used? are these useful?
        self.op1 = False
        self.op2 = False

        self.src = False  # E.g. T0_out_s0t0 or 'add_x_y.op1'
        self.dests = []
        self.placed = False
        self.route  = {}   # E.g. route['INPUT'] = [T0_in_s0t0, 'T0_op1']

        # self.routed = {}   # E.g. routed['INPUT'] = True
        # Use self.is_routed() instead (see below)

        self.net = []
        # self.processed = False

    def addop(self, operand):
        assert type(operand) == str
        if   not self.op1:
            self.op1 = operand; return "op1"
        elif not self.op2:
            self.op2 = operand; return "op2"
        else:
            print "ERROR my dance card she is full"
            return False

    def show(self):
        print ""
        print "node='%s'" % self.name        
        print "  tileno= %s" % self.tileno
        print "  op1='%s'"   % self.op1
        print "  op2='%s'"   % self.op2
        print "  src='%s'" % self.src
        print "  placed= %s" % self.placed
        print "  dests=%s" % self.dests
        # print "  route=%s" % self.route
        prettyprint_dict("  route ", self.route)
        print "  net= %s" % self.net

    def is_routed(dest_name): return self.route[dest_name] != []

def prettyprint_dict(dictname, dict):
    for d in sorted(dict):
        print "%s%-20s = %s" % (dictname, [d], dict[d])
    

nodes = {}
def build_nodes(DBG=0):
    # Build a global data structure from the dot file e.g.
    #
    #   "INPUT" -> "lb_p4_clamped_stencil_update_stream$mem_1$cgramem";
    #   "INPUT" -> "lb_p4_clamped_stencil_update_stream$reg_0_1";
    #   "INPUT" -> "mul_49119_492_PE";
    #
    # becomes
    #
    #   node["INPUT"].dests = ["mem_1" "reg_0_1", "mul_49119_492_PE"]

    global nodes
    for line in sys.stdin:
        line = line.strip()

        # Don't care about luts (for now)
        if re.search("wen_lut", line): continue

        line = re.sub('lb_p4_clamped_stencil_update_stream\$', "", line)
        line = re.sub("\$cgramem", "", line)
        if DBG>1: print "# ", line

        parse = re.search('["]([^"]+)["][^"]+["]([^"]+)["]', line)
        # if not parse: print "# FOO IGNORED\n"
        if not parse: continue

        lhs=parse.group(1)
        rhs=parse.group(2)

        if DBG>1: print "# FOO", lhs, rhs, "\n";

        addnode(rhs); addnode(lhs)
        nodes[lhs].dests.append(rhs)
        # print nodes[rhs].dests

    if DBG:
        print "Found dests:"
        for n in sorted(nodes): print "  %-20s %s" % (n, nodes[n].dests)
        print ""


def addnode(nodename):
    global nodes
    if not nodename in nodes: nodes[nodename] = Node(nodename)
        
def initialize_routes():
    for nodename in nodes:
        n = nodes[nodename]
        for d in n.dests:
            n.route[d] = []
            # n.routed[d] = False



# # Could also be a simple list resources[n]
# class Tile:
#     # Enumerate the tile resources
#     def __init__(self,tileno):
#         self.tileno = tileno
#         self.resources = []
#         for dir in ['in','out']:
#             for side in range(4):
#                 for track in range(5):
#                     port = "%s_s%dt%d" % (dir,side,track)
#                     self.resources.append(port)
#         # print self.resources
# 
# global tiles
# def init_tiles_old(DBG=0):
#     ntiles = cgra_info.ntiles()
# 
#     tiles = range(ntiles)
# 
#     for i in range(len(tiles)):
#         tiles[i] = Tile(i)
# 
#     if DBG: print "Initialized %d tiles" % ntiles
# 
#     # print ntiles
#     # print tiles
#     # print tiles[0]

def init_tile_resources(DBG=0):
    '''E.g. resources[0] = ['in_s0t0', 'in_s0t1', ... 'out_s3t3', 'out_s3t4']'''
    global resources

    ntiles = cgra_info.ntiles()
    resources = range(ntiles)
    for i in range(ntiles):
        resources[i] = []
        for dir in ['in','out']:
            for side in range(4):
                for track in range(5):
                    port = "%s_s%dt%d" % (dir,side,track)
                    resources[i].append(port)

        # Tile-specific resources
        if  is_mem_tile(i): resources[i].extend(['mem_in','mem_out'])
        elif is_pe_tile(i): resources[i].extend(['op1','op2','pe_out'])

    # TODO/FIXME add memtile, pe-specific resources etc.

    if DBG: print "Initialized %d tiles" % ntiles
    print resources[0]

def is_pe_tile(tileno):  return re.search("^pe",  cgra_info.tiletype(tileno))
def is_mem_tile(tileno): return re.search("^mem", cgra_info.tiletype(tileno))


def initialize_node_INPUT():
    src = 'in_s1t0'
    tileno=0

    # Place 'name' in tile 'tileno' at location 'src'
    place('INPUT', tileno, src)

    # Really?
    # assert INPUT.name == 'INPUT'
    # assert INPUT.op1 == False
    # assert INPUT.op2 == False
    # assert INPUT.routed == False

def is_const(node):  return re.search("^const", node)
def is_reg(node): return re.search("^(reg)", node)
def is_mem(node): return re.search("^(mem)", node)
def is_pe(node): return (node and re.search("^(add|mul)", node))
def is_io(node): return (node and re.search("INPUT|OUTPUT", node))

def constant_folding(DBG=0):
    # Combine "const" nodes with their associated PEs

    # Process the constants
    # dests['const16_16'] = ['mul_48716_488_PE']
    global nodes
    for n in nodes:
        
        if not is_const(n): continue
        k = nodes[n]

        # Constant has only one destination (the PE)
        dest = k.dests
        assert len(dest) == 1

        pe = nodes[k.dests[0]]
        assert is_pe(pe.name)

        pe.addop(k.name)
        if DBG: pe.show()

        # k.processed = True
        # del nodes[n]
        
def register_folding(DBG=9):
    '''
    Process all the reg->pe pairs
    Mark by setting reg src to e.g. 'add_x_y.op1'
    '''
    
    global nodes
    if DBG: print "Process all the reg->pe pairs"
    for reg_name in nodes:

        # Only look at nodes that are regs
        # if nodes[n_name].processed: continue
        if not is_reg(reg_name):      continue
        reg = nodes[reg_name]

        # Reg must have ONE dest and dest must be a PE
        if len(reg.dests) != 1: continue
        pe_name = reg.dests[0]
        if not is_pe(pe_name):   continue
        pe = nodes[pe_name]

        # Fold it! By setting src to e.g. "add_x_y.op1"
        # route [pe, "op1"] means duh obvious right?
        op = pe.addop(reg_name) # "op1" or "op2"
        reg.src  = "%s.%s" % (pe_name, op) # E.g. "add_x_y.op1"

        # if DBG: print "Found foldable reg '%s'" % reg_name
        if DBG: print "Will fold reg '%s' into pe '%s' as '%s'" % \
           (reg_name,pe_name,op)

        if DBG:
            reg.show()
            pe.show()
            print '-----'



# Happens automatically as long as we process non-regop regs LAST (right?)
# def process_input(DBG=1):
#     # INPUT tile is always tile 0
#     # INPUT wire is always wire_m1_1_BUS16_S1_T0 i.e. T0_in_s1t0
# 
#     INPUT = nodes['INPUT']
#     INPUT_dests  = sorted(INPUT.dests)
# 
#     # Look for a reg-pe pair that we can fold into the INPUT tile
#     print "Searching for regop (reg/pe pair) in INPUT dests %s" % INPUT_dests
#     for dname in INPUT_dests:
#         # print dname
#         if is_regop(dname):
#             print "Found a reg pair starting at '%s'" % dname
#             fold_regop_to_input(nodes[INPUT_tileno], d)
#             return
# 
#     if DBG: print "No regpe candidates found for input folding\n"
# 
#     # That failed.
#     # Now, look for a pe that we can foldinto the INPUT tile
# 
#     print "Searching for foldable pe in INPUT dests %s" % INPUT_dests
#     for dname in nodes['INPUT'].dests:
#         if is_pe(dname):
#             print "# Found INPUT-connected pe '%s'" % dname
#             fold_input_connected_pe(dname)
#             return
# 
#     if DBG: print "No pe candidates found for input folding\n"
# 
# def fold_regop_to_input(n,d): print 'its not plugged in yet'

def place(name, tileno, src, DBG=0):
    '''
    Place "name" in tile "tileno" at location "src"
    where e.g. local name 'src' = 'pe_out' or 'out_s1t1'
    '''

    if   is_pe(name):  assert src ==  'pe_out'
    elif is_mem(name): assert src == 'mem_out'

    n = nodes[name]
    if n.placed:
        print "ERROR %s already placed at %s" % (name, n.src)
        sys.exit(1)

    n.tileno = tileno
    n.src = src
    n.placed = True

    if not (src in resources[tileno]):
        print "ERROR tile %d has no available resource '%s'" % (tileno,src)
    assert src in resources[tileno]

    resources[tileno].remove(src)
    assert src not in resources[tileno]
    
    if DBG: print "# Placed '%s' in tile %d at location '%s'" % (name, tileno, src)
    return (0, src)

def add_route(sname, dname, tileno, src_port, dst_port, DBG=1):
    '''
    Within tile 'tileno' build connection "src_port -> dst_port"
    Add connection to src node as part of route[dst]
    Add ports to netlist for 'src'
    Port names have the form 'T0_in_s1t1'
    '''

    if dst_port == 'choose_op':
        assert is_pe(dname)
        op       = nodes[dname].addop(sname)
        dst_port = "T%d_%s" % (nodes[dname].tileno, op)
        if DBG: print "# I chose to connect '%s' to '%s'/'%s'" \
                  % (sname,dname,op)

    # Can't route unplaced nodes, right?
    assert nodes[sname].placed == True
    assert nodes[dname].placed == True

    # Build the port-to-port connection
    connection = "%s -> %s" % (src_port, dst_port)
    if DBG: print "#   Routed ports '%s'" % connection

    # Add the connection to src->dst route list
    nodes[sname].route[dname].append(connection)
    if DBG: print "#   Added connection '%s' to route from '%s' to '%s'" % \
       (connection, sname, dname)
    # nodes[sname].routed[dname] = True
    if DBG: print "#   Now node['%s'].route['%s'] = %s" % \
       (sname,dname,nodes[sname].route[dname])

    # Add the ports to netlist of src node
    nodes[sname].net.extend([src_port, dst_port])
    if DBG: print "#   Added ['%s','%s'] to netlist" % (src_port, dst_port)
    if DBG: print "#   Now node['%s'].net = %s" % (sname,nodes[sname].net)

    if DBG: nodes[sname].show()

def finish_route(sname,dname, DBG=0):
    '''Mark *route completed* by adding dname to sname netlist'''
    nodes[sname].net.append(dname)

    if DBG: print "# Route '%s -> %s' is now complete" % (sname,dname)
    if DBG: print "# Add '%s' to nodes['%s'].net"      % (sname,dname)
    if DBG: print "#   Now node['%s'].net = %s" % (sname,nodes[sname].net)
    



def is_regop(regname):
    '''
    "regname" is a reg-pair if:
    - regname is the name of a reg node
    - regname.src is assigned and is a pe
    '''
    assert type(regname) == str
    if not is_reg(regname):         return False

    reg_src = nodes[regname].src # E.g. "add_2_3.op1"
    # print reg_src;
                
    if is_pe(reg_src): return True
    else:              return False



def process_nodes(sname, indent='# ', DBG=1):
    '''Place and route each unprocessed destination for nodename'''

    # print indent+"Processing node '%s'" % sname
    src = nodes[sname]

    schildren = sorted(src.dests)
    if schildren == []:
        print indent+"  '%s' has no children\n" % sname
        return

    # Build an ordered list of what to process; pe and mem first, then regs
    # With any luck, regs get a free ride somewhere along the path.
    
    regchilds = []; otherchilds = []
    for dname in sorted(schildren):
        if   is_pe(dname):  otherchilds.append(dname)
        elif is_io(dname):  otherchilds.append(dname)
        elif is_mem(dname): otherchilds.append(dname)
        elif is_regop(dname): otherchilds.append(dname)
        elif is_reg(dname):   regchilds.append(dname)
        else: print "ERROR What is '%s'?" % dname

    sorted_schildren = otherchilds + regchilds
    #print 'FOO', sorted_schildren

    # Place and route all dests

    already_done = []
    if DBG: print indent+"Processing '%s' dests %s" % (sname,sorted_schildren)
    for dname in sorted_schildren:
        was_placed = is_placed(dname)
        was_routed = is_routed(sname,dname)

        # Skip nodes that have already been placed and routed
        # EXCEPT INPUT NODE destinations
        if was_placed and was_routed:
            print indent+"  (already processed '%s')\n" % dname

            # INPUT is a weird special case
            if sname != 'INPUT': already_done.append(dname)
            continue

        print indent+"  Processing '%s' dest '%s'" % (sname,dname)

        place_and_route(sname,dname,indent+'  ')

        if not DBG: continue

        # Not sure about these...!
        if was_placed:
            print indent+"  ('%s' was already placed)" % dname
        else:
            (t,loc) = (nodes[dname].tileno,nodes[dname].src)
            print indent+"  Placed '%s' in tile %d at location '%s'" % (dname, t, loc)

        if was_routed:
            print indent+"  ('%s' was already routed)" % dname
        else:
            # (tileno,resource) = (nodes[dname].tileno, nodes[dname].src)
            # print indent+"  Placed '%s' at tile %d port '%s'" % (dname,tileno,resource)
            # print indent+"  Routed '%s -> %s'" % (sname,dname)
            print indent+"  Routed %s" % nodes[sname].route[dname]
            print indent+"  Now node['%s'].net = %s" % (sname,nodes[sname].net)
                                               
        print ""
        
        # dchildren = sorted(nodes[dname].dests)
        # if dchildren == []:
        #     print indent+"  Dest '%s' has no children" % dname
        # else:
        #     print indent+"  Processed dest '%s'; now process children %s" % \
        #           (dname, dchildren)

        # Do this as a separate pass for breadth-first...
        # process_nodes(dname, indent+'    ')

    # Recursively process each dest

    for dname in sorted_schildren:
        if dname in already_done: continue
        process_nodes(dname, indent+'    ')


def place_and_route(sname,dname,indent='# ',DBG=0):

    if DBG: print indent+"PNR '%s' -> '%s'" % (sname,dname)

    # Source should alreay be placed, yes?
    if not is_placed(sname):
        print "ERROR '%s' has not been placed yet?" % sname
    assert is_placed(sname)

    # FIXME this is not optimal
    # place(pe_name, INPUT_tileno, 'pe_out')
    if sname=='INPUT' \
       and is_pe(dname) \
       and ('pe_out' in resources[0]):

        print "FOO whhop ther ti tis - avail pe slot in input tile"

        # TODO global INPUTWIRE = 'T0_in_s1t0', INPUTTILE=0

        DBG=1
        if DBG: print "Connecting '%s' to '%s'" % (sname,dname)

        itile = 0; assert nodes['INPUT'].tileno == itile

        place(dname, itile, 'pe_out')
        add_route(sname, dname, itile, 'T0_in_s1t0', 'choose_op')
        finish_route(sname, dname)       
        return

#         print "# Placing pe in INPUT tile..."
#         place(dname, itile, 'pe_out')
# 
#         print "# Routing INPUT to pe..."
#         add_route(sname, dname, itile, 'T0_in_s1t0', 'choose_op')
# 
#         print '# Mark route COMPLETED'
#         finish_route(sname, dname)       
# 
#         # Check that pe_out got removed from INPUT (tile0) resources
#         assert not ('pe_out' in resources[0])

    # Does destination have a home?
    if not is_placed(dname):

        # BOOKMARK
        # do DBG=1
        # Figure how to do the first placement INPUT -> mem_1 maybe
        # Use new connection thingies maybe

        # print indent+"No home for '%s'"
        if DBG: print indent+"No home for '%s'" % dname
        if DBG: print indent+"For now just place it randomly"
        (tileno,resource) = randomly_place(dname)
    else:
        (tileno,resource) = (-1, "already_placed")

    if not is_routed(sname,dname):
        if DBG: print indent+"No route '%s -> %s'" % (sname,dname)
        if DBG: print indent+"For now just mark it finished"
        bogus_route = "%s -> %s BOGOSITY" % (sname,dname)
        nodes[sname].route[dname].append(bogus_route)
        finish_route(sname,dname)

    return (tileno,resource)

def place_and_route_test(sname,dname,indent='# ',DBG=1):
    if DBG: print indent+"  PNR '%s' -> '%s'" % (sname,dname)

    # Test
    nodes[dname].tileno = 999
    nodes[dname].src    = dname
    nodes[sname].net.append(nodes[dname].src)
    return


def randomly_place(dname, DBG=0):
    '''
    Assign dname to any random available resource
    Well maybe not completely random.
    Assign mem to mem tiles ONLY using resource 'mem_out'
    '''
    if is_mem(dname): dtype='mem'
    else:             dtype='pe'

    ntiles = len(resources) # len(list) = length (number of items in) list
    for tileno in range(ntiles):

        if is_mem_tile(tileno): ttype='mem'
        else:                   ttype='pe'
        if dtype != ttype: continue

        if is_regop(dname):
            # regops come from register-folding optimization pass
            # They look like this:
            # 
            # node='reg_2_2'
            #   tileno= -1
            #   op1='False'
            #   op2='False'
            #   src='mul_45911_460_PE.op2'
            #   placed= False
            #   dests=['mul_45911_460_PE']
            #   route ['mul_45911_460_PE'] = []
            #   net= []

            # Before placing regop, must first place target pe
            pe = nodes[dname].dests[0]
            if not is_placed(pe): randomly_place(pe)

            # regop goes in same tile as target pe as op1 or op2
            tileno = nodes[pe].tileno
            if   (re.search('op1$', nodes[dname].src)): op = 'op1'
            elif (re.search('op2$', nodes[dname].src)): op = 'op2'
            else: assert(0)
                  
            place(dname,tileno,op)
            return (tileno,op)

        elif  is_pe(dname): r='pe_out'
        elif is_mem(dname): r='mem_out'
        else:
            # It's an unassigned register, yes?
            # Although maybe could be double-register pair someday.
            # Randomly choose the first outport you find
            # (technically should be out-port but oh well

            regex = re.compile('^out')
            outs = filter(regex.match, resources[tileno])
            if outs == []: continue
            else:          r = outs[0]
        
        if r not in resources[tileno]: continue
        else:
            if DBG:
                print "# Randomly assigning '%s' to tile %d resource '%s'" \
                      % (dname,tileno,r)
            place(dname, tileno, r)
            return (tileno,r)

def is_placed(dname):
    return (nodes[dname].tileno != -1)

def is_routed(sname,dname):
    return (dname in nodes[sname].net)


main()







