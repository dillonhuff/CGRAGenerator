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
    print "foo"


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
        self.op1 = False
        self.op2 = False
#         self.src1 = False # E.g. T0_in_s0t0
#         self.src2 = False
        self.src = False  # E.g. T0_out_s0t0 or 'add_x_y.op1'
        self.dests = []
        self.placed = False
        self.route  = {}   # E.g. route['INPUT'] = [T0_in_s0t0, 'T0_op1']

        # Use self.is_routed() instead (see below)
        # self.routed = {}   # E.g. routed['INPUT'] = True

        self.net = []
        #         self.processed = False

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
        print ""
        print "  dests=%s" % self.dests
        showdict("  route ", self.route)
#         print "  route=%s" % self.route
        print ""


        # Use self.is_routed() instead (see below)
        #         showdict("  routed", self.routed)
        #         print ""
        #         print "  routed= %s" % self.routed

        print "  net= %s" % self.net


    def is_routed(dest_name): return self.route[dest_name] != []

def showdict(dictname, dict):
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

#         k.processed = True
        # del nodes[n]
        
def register_folding(DBG=9):
    '''Process all the reg->pe pairs'''
    
    global nodes
    if DBG: print "Process all the reg->pe pairs"
    for reg_name in nodes:
        # if nodes[n_name].processed: continue
        if not is_reg(reg_name):      continue
        reg = nodes[reg_name]

        # Reg must have ONE dest and dest must be a PE
        if len(reg.dests) != 1: continue
        pe_name = reg.dests[0]
        if not is_pe(pe_name):   continue
        pe = nodes[pe_name]

        # Fold it!
        # route [pe, "op1"] means duh obvious right?
        op = pe.addop(reg_name) # "op1" or "op2"
        reg.src  = "%s.%s" % (pe_name, op) # E.g. "add_x_y.op1"

        if DBG:
            reg.show()
            pe.show()
            print '-----'

def process_input(DBG=1):
    # INPUT tile is always tile 0
    # INPUT wire is always wire_m1_1_BUS16_S1_T0 i.e. T0_in_s1t0

    INPUT = nodes['INPUT']
    INPUT_dests  = INPUT.dests

    # Look for a reg-pe pair that we can foldinto the INPUT tile
    print "Searching for regpe pair  in INPUT dests %s" % INPUT_dests
    for dname in INPUT_dests:
        # print dname
        if is_regpe_pair(dname):
            print "Found a reg pair starting at '%s'" % dname
            fold_regpe_pair_to_input(nodes[INPUT_tileno], d)
            return

    if DBG: print "No regpe candidates found for input folding\n"

    # That failed.
    # Now, look for a pe that we can foldinto the INPUT tile

    print "Searching for foldable pe in INPUT dests %s" % INPUT_dests
    for dname in nodes['INPUT'].dests:
        if is_pe(dname):
            print "# Found INPUT-connected pe '%s'" % dname
            fold_input_connected_pe(dname)
            return

    if DBG: print "No pe candidates found for input folding\n"

def place(name, tileno, src,DBG=1):
    '''Place "name" in tile "tileno" at location "src"'''

    n = nodes[name]
    if n.placed:
        print "ERROR %s already placed at %s" % (name, n.src)
        sys.exit(1)

    n.tileno = tileno
    n.src = src
    n.placed = True
    assert src in resources[tileno]
    resources[tileno].remove(src)
    assert src not in resources[tileno]
    
    if DBG: print "# Placed '%s' in tile %d at location '%s'" % (name, tileno, src)


def fold_input_connected_pe(pe_name, DBG=1):
    '''assign pe to input tile'''

    INPUT = nodes['INPUT']
    INPUT_tileno = INPUT.tileno
    INPUT_src   = 'in_s1t0'
    assert INPUT_tileno == 0

    # Place foldable PE in tile 0 with INPUT
    place(pe_name, INPUT_tileno, 'pe_out')

    # BOOKMARK
    # NEXT: need a cleanup and checkin for this file, maybe lib/conn* too?
    # Build a 'route' routine maybe
    # PNR remaining INPUT dests
    # And/or maybe encapsulate some of above code into function(s)

    # Route INPUT to folded PE

# BOOKMARK
# Continue with routing
# PNR remaining INPUT dests
# And/or maybe encapsulate some of above code into function(s)



    assert INPUT.name   == 'INPUT'
    assert INPUT.tileno == 0
    assert INPUT.op1 == False
    assert INPUT.op2 == False
    assert INPUT.src == INPUT_src

    # Route src (INPUT) to dst (folded pe)

    src = "T%d_%s" % (INPUT.tileno, INPUT.src)

    op = nodes[pe_name].addop('INPUT')
    dst = "T%d_%s" % (INPUT.tileno, op)

    addroute('INPUT', pe_name, INPUT.tileno, src, dst)




def addroute(src_nodename, dst_nodename, tileno, src_wire, dst_wire, DBG=1):
    ''' Add tileno:"src_port -> dst_port" for route from src do dst'''

    (sn,dn) = (src_nodename,dst_nodename)

    node = nodes[sn]

    # Can't route an unplaced node, right?
    assert node.placed == True

    connection = "%s -> %s" % (src_wire, dst_wire)
    node.route[dn].append(connection)
#     node.routed[dn] = True
    node.net.extend([src_wire, dst_wire])


    if DBG: print "Added connection '%s' to route from '%s' to '%s'" \
       % (connection, sn, dn)


    if DBG: print "#   Routed node '%s' to '%s'" % (src_wire, dst_wire)
    if DBG: print "#   node.route['%s'] = %s" % (dn,node.route[dn])
    if DBG: print "#   node.net = %s" % node.net

    if DBG: node.show()



def fold_regpe_pair_to_input(n,d): print 'its not plugged in yet'

def is_regpe_pair(regname):
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



# note OUTPUT wire is always wire_m1_1_BUS16_S1_T0



cgra_filename = get_default_cgra_info_filename()
cgra_info.read_cgra_info(cgra_filename)

init_tile_resources(DBG=1)

build_nodes(DBG=1)
initialize_routes()
initialize_node_INPUT()
print '------------------------------------------------------------------------'
constant_folding(DBG=1)
print '------------------------------------------------------------------------'
print "# consts should be gone now"
print '------------------------------------------------------------------------'
register_folding()
print '------------------------------------------------------------------------'
process_input()




sys.exit(0)



main()







