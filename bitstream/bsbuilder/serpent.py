#!/usr/bin/python

import sys
import re
import os

# Import cgra_info via relative path
mypath = os.path.realpath(__file__)
mydir  = os.path.dirname(mypath)
decoder_path = mydir+"/../decoder"
sys.path.insert(0, decoder_path)
from lib import cgra_info
from lib import connect_tiles as CT


import traceback # sys.stdout.flush(); traceback.print_stack(); sys.stderr.flush()
def show_trace(nlines=100):
    sys.stdout.flush(); traceback.print_stack(); sys.stderr.flush()

from inspect import currentframe, getframeinfo
def where(lno=0):
    # E.g. 'serpent.py/42'
    # frameinfo = getframeinfo(currentframe())
    frameinfo = getframeinfo(currentframe().f_back)
    if not lno: lno = frameinfo.lineno
    return '%s/%s' % (frameinfo.filename, lno)

def pwhere(lno=0, txt=''):
    frameinfo = getframeinfo(currentframe().f_back)
    if not lno: lno = frameinfo.lineno
    info = '%s/%s' % (frameinfo.filename, lno)
    if txt=='':
        # E.g. "serpent.py/42"
        print info
    else:
        # E.g. "serpent.py/42: hello world"
        print '%s: %s' % (info, txt)

def test_where():
    print where()
    pwhere('hello')
    print where()
    exit()
# test_where()

import packer

# FIXME/TODO globals wrapper and initializer thingy, see packer.py maybe
GRID_WIDTH  = 8
GRID_HEIGHT = GRID_WIDTH

# INPUT always comes in on bus 'T0_in_s2t0'
INPUT_TILENO = 0
INPUT_TILE   = INPUT_TILENO
INPUT_WIRE   = 'in_s2t0'
INPUT_WIRE_T = 'T0_in_s2t0'

# Set this to True if a PE has been placed in the INPUT tile
# FIXME is this the best way to do this!!?
INPUT_OCCUPIED = False

VERBOSE = False
dot_filename = False
bsb_filename = False
def process_args():
    # Get name of this script
    scriptname = sys.argv[0]
    scriptname_tail = scriptname
    parse = re.search('([/].*$)', scriptname)
    parse = re.search('([^/]+$)', scriptname)
    if (parse): scriptname_tail = parse.group(1)
    args = sys.argv[1:] # shift

    usage = '''
Place and route indicated "dot" file.  Output is in "bsb" format.
Examples:
   %s pointwise_mapped.dot
   %s -v pointwise_mapped.dot
   %s pointwise_mapped.dot -o pointwise.bsb
   %s pointwise_mapped.dot -o pointwise.bsb -cgra cgra_info.txt 
   %s --help
''' % (scriptname_tail, scriptname_tail, scriptname_tail, scriptname_tail, scriptname_tail)

    # Will need cgra_info
    global cgra_filename
    cgra_filename = get_default_cgra_info_filename()

    # if (len(args) < 1): print usage; sys.exit(-1);

    global VERBOSE
    global bsb_filename
    global dot_filename
    while (len(args) > 0):
        if   (args[0] == '--help'): print usage; sys.exit(0);
        elif (args[0] == '-v'):    VERBOSE = True
        elif (args[0] == '-cgra' or args[0] == '-cgra_info'):
            cgra_filename = args[1]
            args = args[1:];
        elif (args[0] == '-o'):
            bsb_filename = args[1]
            args = args[1:];

        else:
            dot_filename = args[0];
        args = args[1:]


def nearest_mem_tile(node='INPUT', exclude = [], DBG=1):
    '''
    Find mem tile nearest to indicated node,
    excluding tiles in exclude list
    '''

    mytileno = nodes[node].tileno
    (myrow,mycol) = rc2tileno(mytileno)
    if DBG: print \
       "# Looking for memtile nearest to node '%s' in tile %d (r%d,c%d)" \
       % (node, mytileno, myrow, mycol)

    for i in range( max(GRID_WIDTH, GRID_HEIGHT)):
        if DBG: print "# Searching distance %d" % i
        

def manhattan_distance_rc(src=[0,0], dst=[5,1], DBG=0):

    # use connect_tiles.connect_tiles_same_{row,col} to connect;
    # count ntiles in path

    # (begin,path,end) = CT.connect_tiles(src=0,dst=17,track=0,dir='hv',DBG=DBG-1)
    p = CT.connect_tiles(src=0,dst=17,track=0,dir='hv',DBG=DBG-1)
    (begin,path,end) = CT.unpack_path(p)

    dist = len(path)
    
    # E.g. extract_tile('T1_in_s2t0 -> T1_out_s0t0') = 'T1'
    def extract_tile(s): return re.search('^(T\d+)', s).group(1)

    if DBG:
        print "# Distance from %s to %s is %d:" % (src, dst, dist)
        # T0-> (T1 -> T2 -> T3) ->T17
        a = extract_tile(begin)

        tiles = []
        for i in path: tiles.append(extract_tile(i))
        b = tiles

        c = extract_tile(end)
        print '# %s-> %s ->%s' % (a,b,c)
            
def test_manhattan_distance_rc():
    cgra_info.read_cgra_info(verbose=True)
    manhattan_distance_rc(DBG=1)
    print ''

def test_fan_out():
    # S0 only connecst to four sides
    cgra_info.fan_out('in_BUS16_S0_T0', 0, DBG=1)
    
    # S2 can also connect to op1
    cgra_info.fan_out('in_BUS16_S2_T0', 0, DBG=1)
    
    cgra_info.fan_out('mem_out', 3, DBG=1)
    cgra_info.fan_out('pe_out_res', 0, DBG=1)

# # FIXME combine with other manhattan thing above maybe
# def manhattan_distance(src=[0,0], dst=[5,1]):
#     '''
#     Return manhattan distance (number of intervening tiles) from src
#     tile to each side (e,s,w,n) of dst tile.
#     E.g. path from (0,0) to (5,1) should be (7,8,5,5)
#     '''
# 
#     dist = {}
#     # Eight cases: dest is (n, ne, e, se, s, sw, w, nw) of src
#     d2s = direction(dst,src)
#     delta_row = abs( src[0] - dst[0] )
#     delta_col = abs( src[1] - dst[1] )
# 
#     short_straight_path = min(delta_row-2,delta_col-2)
# 
#     if d2s == 'n':
#         
#         dist['n'] = (delta_row-2) + 0
#         dist['w'] = (delta_row-1) + (delta_col-1)
#         dist['e'] = (delta_row-1) + (delta_col+1)
#         dist['s'] = (delta_row-0) + (delta_col-0)
#     if d2s == 's':
#         dist['s'] = (delta_row-2) + 0
#         dist['w'] = (delta_row-1) + (delta_col-1)
#         dist['e'] = (delta_row-1) + (delta_col+1)
#         dist['n'] = (delta_row-0) + (delta_col-0)
#     if d2s == 'e':
#         dist['e'] = (delta_col-2) + 0
#         dist['w'] = (delta_col-1) + (delta_row-1)
#         dist['n'] = (delta_col-0) + (delta_row-0)
#         dist['e'] = (delta_col-1) + (delta_row+1)
# 
# 
# 
# 
# def search_pattern_old(n,DBG=1):
#     '''
#     Produce a searchpattern list of (r,c) coords for all tiles at
#     distance n away from center tile (0,0).  The idea is to pack as
#     closely as possible to the NW corner of the grid and to prefer-
#     entially find tiles in a straight line form the center tile.
# 
#                     1--------> 3
#                     2          |
#                     |   +--+   |
#                     |   |  |   |
#                     |   +--+   |
#                     |          v
#                     v 4-------->
# 
#     '''
#     (top,left,right,bottom) = ([],[],[],[])
# 
#     # Top side, NW corner to NE neighbor
#     top.append([-n,0]) # Opt: straight-line tile goes first
#     for c in range(-n, n): top.append([-n,c])
#     if DBG: print top
# 
#     # Left side, NW neighbor to SW corner
#     left.append([0,-n]) # Opt: straight-line tile goes first
#     for r in range(1-n, n+1): left.append([r,-n])
#     if DBG: print left
# 
#     # Right side, NE corner to SE neighbor
#     right.append([0,n]) # Opt: straight-line tile goes first
#     for r in range(-n, n): right.append([r,n])
#     if DBG: print right
# 
#     # Bottom side, SW neighbor to SE corner
#     bottom.append([n,0]) # Opt: straight-line tile goes first
#     for c in range(1-n, n+1): bottom.append([n,c])
#     if DBG: print bottom
# 
# 
# def test_search_pattern():
#     search_pattern(1,DBG=1)
#     # [[-1, 0], [-1, -1], [-1, 0]]
#     # [[0, -1], [0, -1], [1, -1]]
#     # [[0, 1], [-1, 1], [0, 1]]
#     # [[1, 0], [1, 0], [1, 1]]
# 
#     print "----"
#     search_pattern(2,DBG=1)
#     # [[-2, 0], [-2, -2], [-2, -1], [-2, 0], [-2, 1]]
#     # [[0, -2], [-1, -2], [0, -2], [1, -2], [2, -2]]
#     # [[0, 2], [-2, 2], [-1, 2], [0, 2], [1, 2]]
#     # [[2, 0], [2, -1], [2, 0], [2, 1], [2, 2]]

def main(DBG=1):
    # test_connect_tiles()
    # sys.exit(0)
    # notes()

    global cgra_filename
    process_args()

    print '######################################################'
    print '# serpent.py: Read cgra info'
    cgra_info.read_cgra_info(cgra_filename, verbose=True)

    print '######################################################'
    print '# serpent.py: Initialize the packer'
    packer.USE_CGRA_INFO = True
    packer.init_globals() # this is crucial out there
    print "# here's the grid!"
    print '# '
    packer.FMT.grid()
    print ''

    print '######################################################'
    print '# serpent.py: Read input, initialize node and tile data structures'
    init_tile_resources(DBG=1)
    build_nodes(DBG=1)
    assert not nodes['INPUT'].placed
    initialize_routes()
    initialize_node_INPUT()

    # FIXME should be part of initialize_node_INPUT somehow right?
    # Allocate tile 0 for input node
    packer.allocate(0)
    if DBG>2:
        print "# order so far"
        print '# '
        packer.FMT.order()
        print ''

    print ''
    print '########################################'
    print '# serpent.py: register folding'
    register_folding(DBG=1)

    # Happens automatically as long as we process non-regop regs LAST (right?)
    # print '######################################################'
    # print '# serpent.py: Process and optimize INPUT node'
    # process_input()

    print ''
    print '######################################################'
    print '# serpent.py: Process remaining nodes, starting with INPUT'
    process_nodes('INPUT')

    print '########################################'
    print '# serpent.py: constant folding - do this LAST'
    constant_folding(DBG=1)
    print "# consts should be gone now"

    # TODO/FIXME Special treatment for OUTPUT?
    # note OUTPUT wire is always wire_m1_1_BUS16_S1_T0

    if bsb_filename: note = 'see file "%s"' % bsb_filename
    else:            note = ''

    print "########################################################"
    print "# FINAL OUTPUT", note
    final_output()

    sys.exit(0)
    

def final_output(DBG=0):

    # Redirect stdout to bsb_filename if such exists
    if bsb_filename:
        save_stdout = sys.stdout
        sys.stdout = open(bsb_filename, 'w')

    if DBG:
        print '# REGISTERS', REGISTERS
        for n in sorted(nodes):
            # print "  %-20s %s" % (n, nodes[n].dests)
            nodes[n].show()

        for nodename in sorted(nodes):
            node = nodes[nodename]
            print nodename
            prettyprint_dict("  route ", node.route)

    # First the constants
    print ''
    print '# CONSTANTS'
    for sname in sorted(nodes):
        if is_const(sname):
            dname = nodes[sname].dests[0]
            # nodes[sname].show()
            # nodes[dname].show()
            print '# %s::%s %s' % (sname,dname,nodes[sname].output)
    print ''

    # Registers and ops
    print '# REGISTERS', REGISTERS
    print ''

    print '# PE tiles'
    print_oplist()

    print '# MEM tiles'
    print_memlist()

    # Routing
    print '# ROUTING'
    print ''
    for sname in sorted(nodes):
        if is_const(sname): continue
        src = nodes[sname]
        for dname in src.dests:
            dst = nodes[dname]
            print '# %s::%s' % (sname,dname)

            if is_regop(sname):
                r = src.route[dname][0]
                print '#', mark_regs(r), '\n'
                break

            for c in src.route[dname]:
                print mark_regs(c)

            print ''

    # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
    # OUTPUT tile  0 (0,0) / in_BUS16_S1_T1 / wire_1_0_BUS16_S3_T1
    print_io_info()


def print_io_info(DBG=0):
    # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
    # OUTPUT tile  0 (0,0) / in_BUS16_S1_T1 / wire_1_0_BUS16_S3_T1
    inode = nodes['INPUT'];  
    onode = nodes['OUTPUT']; 
    if DBG:
        inode.show()
        onode.show()

    # cgra_info.test_canon2global()

    iwire = inode.input0
    owire = onode.output

    if DBG>1:
        print "# local name for input wire is '%s'" % iwire

    ig = cgra_info.canon2global(iwire)
    og = cgra_info.canon2global(owire)

    if DBG>1: print iwire, ig
    if DBG>1: print owire, og

    def p(io, t, w, wg):
        # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
        # OUTPUT tile  0 (0,0) / in_BUS16_S1_T1 / wire_1_0_BUS16_S3_T1
        (r,c) = cgra_info.tileno2rc(t)
        wc    = cgra_info.canon2cgra(w)
        print '# %-6s tile %2d (%d,%d) / %s / %s' % (io, t, r,c, wc, wg)

    p('INPUT',  inode.tileno, iwire, ig)
    p('OUTPUT', onode.tileno, owire, og)
    # assert False
    exit()


def print_oplist():
    oplist = range(cgra_info.ntiles())
    for sname in sorted(nodes):
        if is_const(sname): continue
        src = nodes[sname]
        if is_pe(sname):
            addmul = sname[0:3]
            op1 = optype(src.input0)
            op2 = optype(src.input1)
            opline = 'T%d_%s(%s,%s)' % (src.tileno, addmul, op1, op2)
            opcomm = '# %s' % sname
            oplist[src.tileno] = '%-26s %s' % (opline,opcomm)

    # Print in tile order, 0 to 'ntiles'
    for i in range(cgra_info.ntiles()):
        if oplist[i] != i: print oplist[i]

    print ''


def print_memlist():
    # E.g. prints
    #     'T3_mem_64    # mem_1 fifo_depth=64'
    #     'T17_mem_64   # mem_2 fifo_depth=64'
    memlist = range(cgra_info.ntiles())
    for sname in sorted(nodes):
        if is_const(sname): continue
        src = nodes[sname]
        if is_mem(sname):
            opline = 'T%d_mem_%d' % (src.tileno, src.fifo_depth)
            opcomm = '# %s fifo_depth=%d' % (sname, src.fifo_depth)
            memlist[src.tileno] = '%-12s %s' % (opline,opcomm)

    # Print in tile order, 0 to 'ntiles'
    for i in range(cgra_info.ntiles()):
        if memlist[i] != i: print memlist[i]

    print ''


def optype(input):
    '''
    Where input is one of e.g. 'T32_op1', 'const32_32'
    and where 'T32_op1' may or may not be in REGISTERS list.
    Return 'reg', 'wire' or name of const e.g. 'const0_0'
    '''
    if is_const(input):                return input
    elif re.search('op.\(r\)', input): return 'reg'
    elif input in REGISTERS:           return 'reg'
    else:                              return 'wire'

def mark_regs(c):
    '''
    if e.g. c=="T0_in_s2t0 -> T0_out_s0t0" and "T0_out_s0t0" is a register,
    mark it with an r e.g. return "T0_in_s2t0 -> T0_out_s0t0_R"
    '''
    rhs = re.search('(\S+)$', c).group(1)
    # print c,rhs
    # if rhs in REGISTERS: c = c+ '_R'
    if rhs in REGISTERS: c = c+ ' (r)'
    return c



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
    return cgra_info.get_default_cgra_info_filename()


class Node:
    def __init__(self, nodename):
        self.name       = nodename
        self.tileno     = -1 # Because 0 is a valid tile number, see?
        self.fifo_depth = -1

        # input/output EXAMPLES (FIXME needs update)
        #            input0/1         output
        # regpe      op1             'alu_3_2' (unplaced)
        # regpe      T0_op1          'alu_3_2' (placed)

        # regreg     T0_out_s0t0     'reg_2_4'
        # mem        T3_mem_in       T3_mem_out
        # pe         T0_op[12]       T0_pe_out
        # regsolo    T0_out_s0t0     T1_in_s2t0
        self.input0 = False  # E.g. T0_out_s0t0 or 'add_x_y'
        self.input1 = False
        self.output = False

        self.dests = []
        self.placed = False
        self.route  = {}   # E.g. route['INPUT'] = [T0_in_s0t0, 'T0_op1']

        # self.routed = {}   # E.g. routed['INPUT'] = True
        # Use self.is_routed() instead (see below)

        self.net = []
        # self.processed = False

    def tiletype(self):
        if self.name[0:3] == 'mem': return 'mem'
        else:                       return 'pe'

    def addop(self, operand):
        assert type(operand) == str
        if not self.input0:
            self.input0 = operand; return "op1"
        elif not self.input1:
            self.input1 = operand; return "op2"
        else:
            print "ERROR my dance card she is full"
            return False

    def show(self):
        print "node='%s'" % self.name        

        type = 'idunno'
        if is_regsolo(self.name): type='regsolo'
        elif is_regop(self.name): type = 'regop'
        elif is_regreg(self.name): type = 'regreg'
        # also: is_{const,mem,reg,pe,io}
        # FIXME add the other types, make it a separate func
        print "  type='%s'" % type

        print "  tileno= %s" % self.tileno
        print "  input0='%s'" % self.input0
        print "  input1='%s'" % self.input1
        print "  output='%s'" % self.output

        print "  placed= %s" % self.placed # FIXME needed/used?
        print "  dests=%s" % self.dests
        # print "  route=%s" % self.route
        prettyprint_dict("  route ", self.route)
        print "  net= %s" % self.net

        if self.fifo_depth != -1:
            print "  fifo_depth= %d" % self.fifo_depth

        print ''

    def is_placed(self): return self.tileno != -1
    def is_routed(self,dest_name): return self.route[dest_name] != []

    def is_avail(self, rname, DBG=0):
        '''
        Resource rname in tile T is avail
        if it is free and/or if it is already in mynet.
        rname should be of the form 'T%d_something'
        '''
        # rname must have embedded tileno, e.g. 'T1_in_s3t2' or 'T5_mem_out'
        (tileno,r) = parse_resource(rname)

        if DBG>2: pwhere(386)
        if DBG>2: print "Looking for '%s' in %s" % (r, self.net)

        # E.g. resources[T] = ['in_s0t0', 'in_s0t1', ...
        # Can't use a register unless we're specifically looking for a register
        if rname in REGISTERS:
            assert rname not in resources[tileno],\
                   "'%s' is a register: should not be in resources list!"
            # But it CAN be in the net list maybe...?
            print "'%s' not avail to '%s' b/c its a register" % (r, self.name)
            return False
            # assert r not in self.net, "'%s' is a register: should not be part of net list!"

        if DBG>2: print "Looking for '%s' in %s" % (rname, self.net)
        if DBG>2: print "is_avail: looking for '%s' in '%s' nodenet" \
              % (rname, self.name)
        if rname in self.net:
            # print "       %-11s available in '%s' nodenet" \'] % (rname, self.name)
            return True

        if DBG>2: print "is_avail: looking for '%s' in tile %d resources %s" \
              % (rname, tileno, resources[tileno])
        if rname in resources[tileno]:
            # print "       %-11s is in free list for tile %d" % (rname, tileno)
            return True

        else:
            print "  %-11s is not available to node '%s'" % (rname, self.name)
            return False

    def place(self,tileno,input,output,DBG=0):
        '''
        Place node "name" in tile "tileno"
        with input 'input' and output 'output'
        where e.g. 'input'  = 'T2_op1'    or 'T1_out_s0t1'
        where e.g. 'output' = 'T2_pe_out' or 'T2_in_s2t1'
        '''
        name = self.name
        if   is_pe(name):
            if input==False and tileno==INPUT_TILE:
                if DBG: print "# Placing PE in input tile"
                if DBG: print "# well that's okay then"
            else:
                assert re.search('op[12]',     input),\
                  '\n\n\ninput should be "op1/2", is actually '+input
            assert re.search('pe_out$',  output)
        elif is_mem(name):
            assert re.search('mem_in$',  input)
            assert re.search('mem_out$', output)
        # elif is_reg(name)...
        # assert input = .*_out_.*, output = .*_in_.* etc.

        if self.placed:
            print "#   WARNING %s already placed at %s" % (name, self.input0)
            # assert False, "ERROR %s already placed at %s" % (name, self.input0)
            print "#   It's okay, probably an alu with two inputs"

        self.tileno = tileno

        # self.input0  = input
        # FIXME this is maybe not great...
        if input:
            if   re.search('op1', input): self.input0 = input
            elif re.search('op2', input): self.input1 = input
            else:
                assert not is_pe(self.name), input
                self.input0 = input
        
        self.output = output
        self.placed = True

        # output is in our net, but input is not.  right?
        self.net.append(output) # right?  RIGHT???

        if DBG: print "# Placed '%s' in tile %d at location '%s'" \
           % (name, tileno, input)
        return

    # Placing the node does not remove its resources from the tile;
    # that's a job for the router, yes?

#     (itile,dummy) = parse_resource( input)
#     (otile,dummy) = parse_resource(output)
#     assert itile == tileno
#     if DBG and (otile != itile): print \
#        "# node's output is in a different tile; must be a register."
# 
#     print otile,tileno,output,input
# 
#     # Placing the node does not remove its resources from the tile;
#     # that's a job for the router, yes?
#     print itile, resources[itile]
#     assert input in resources[itile],\
#            "ERROR tile %d has no available resource '%s'" % (tileno,input)
#     resources[itile].remove(input)
# 
# 
#     assert output in resources[otile],\
#            "ERROR tile %d has no available resource '%s'" % (tileno,output)
# 
#     print otile,tileno,output
# 
#     # note input==output for INPUT node only (bug?  feature?)
#     if input == output:
#         assert tileno == INPUT_TILENO, 'input should not equal outpu!?'
#     else:
#         resources[otile].remove(output)

    def connect(self,a,b,T=-1,DBG=88):
        '''
        In tile T, connect a to b if possible.
        a and b may or may not have embedded tile info.
        Both must be resources available to self.
        If can connect, return connection(s) necessary.
        Else return FALSE i guess.
        '''
        DBG = max(0,DBG)
        if DBG==88: pwhere(1544, 'WARNING did you mean to not set DBG?')

        if a[0] == 'T': T = int(re.search('^T(\d+)', a).group(1))
        if b[0] == 'T': T = int(re.search('^T(\d+)', b).group(1))

        # Canonicalize a,b to have embedded tile info e.g. 'T<t>_resource'
        if a[0] != 'T': a = "T%d_%s" % (T,a)
        if b[0] != 'T': b = "T%d_%s" % (T,b)

        if DBG>1: print ''
        if DBG>1: print "looking to connect '%s' and '%s'" % (a,b)

        if not self.is_avail(a):
            if DBG>1: print "'%s' not avail to tile %d" % (a,T)
            return False
        if not self.is_avail(b):
            if DBG>1: print "'%s' not avail to tile %d" % (b,T)
            return False

        # Valid combinations:       a               b
        #                     pe_out|mem_out      out_.*
        #                          in.*           out_.*
        #                          in.*      {mem_in,op1,op2}   

        if DBG>1: print "       Looks like both are available to '%s' (%s)\n" % (self.name, where(451))

        # print "       Ask cgra: can '%s' connect to '%s'? (%s)" % (a,b,where(457))

        if cgra_info.connect_within_tile(T, a, b, DBG-1):
            if DBG: print '     YES'
            return ['%s -> %s' % (a,b)]
        else:
            if DBG: print "     NO"
        
        print "Cannot connect '%s' to '%s' directly.  BUT" % (a,b)
        print "maybe can connect through intermediary?"
        # sys.stdout.flush(); traceback.print_stack(); sys.stderr.flush()
        # FIXME too many intermediaries?
        pwhere(469)
    
        # Try to salvage it; e.g. if dest is 'op1' then
        # 'reachable' list can contain 'out' wires; if
        # one of the reachable wires can connect to 'op1'
        # then return both paths
        #
        # To test:
        # - data0 (op1) can only connect to side 2;
        # - try and connect (in_s3t0) to op1 in tile 0

        # It only works when dest is op1 or op2 or mem_in, i think

        # FIXME too many intermediaries?
        if not re.search('(op1|op2|mem_in)', b):
            print "Nope wrong kind of tile for intermediary..."
            return False

        print "maybe can connect '%s' to '%s' through an intermediary"\
              % (a,b)
        
        # a_cgra = to_cgra(a, DBG-1)
        # aprime = a_cgra
        (aprime,bprime) = (cgra_info.canon2cgra(a),cgra_info.canon2cgra(b))

        # areach = FO # from just up there
        # areach = cgra_info.fan_out(to_cgra(a), T, DBG=9)
        areach = cgra_info.fan_out(aprime, T, DBG-1)
        print "'%s'/'%s' can areach %s" % (a,aprime,areach)

        b_cgra = to_cgra(b, DBG-1)
        # breach = cgra_info.reachable(bprime, T, DBG=1)
        breach = cgra_info.fan_in(to_cgra(b), T, DBG-1)
        print "'%s'/'%s' can breached by %s" % (b,bprime,breach)


        middle = False
        for p in areach:
            print p, breach
            if p in breach:
                print "WHOOP! There it is:", p
                middle = p
                break

            #         if not middle: assert False
        if middle:
            print "Found double connection QUICKLY."
            p1 = '%s -> %s' % (a, from_cgra(middle, T))
            p2 = '%s -> %s' % (from_cgra(middle, T), b)
            pmiddle = [p1,p2]

            print "Found double connection.  What a day!"
            print "Remember quickfind was", middle, pmiddle
            return pmiddle

        else:
            print "NO MIDDLE"
            print "no good"
            return False
            

def addT(tileno, r):
    '''Embed tileno in resource 'r' e.g. "mem_out" => "T3_mem_out"'''
    return 'T' + str(tileno) + '_' + r

# FIXME/TODO use CT.parse_resource(r) instead
def parse_resource(r):
    '''
    resource must be of the form "T0_in_s0t0" or "T3_mem_out"
    returns tileno+remains e.g. parse_resource("T0_in_s0t0") = (0, 'in_s0t0')
    '''
    return CT.parse_resource(r)



def prettyprint_dict(dictname, dict):
    # So dumb.  But pretty maybe?
    maxlen = 0
    for d in sorted(dict):
        maxlen = max(maxlen, len(str([d])))
    fmt = "%%s%%-%ds = %%s" % maxlen
    for d in sorted(dict):
        # print "%s%-20s = %s" % (dictname, [d], dict[d])
        print fmt % (dictname, [d], dict[d])
    

# def reachable(a,b):
#     # Will use cgra_info.reachable(), but first have to rewrite some things
#     # E.g. 'T0_in_s1t2' => 'in_BUS16_S1_T2'
    

def to_cgra(name, DBG=0):
    # Valid names include "T0_in_s0t0","T3_mem_out"
    return cgra_info.canon2cgra(name, DBG)

def from_cgra(name, tileno, DBG=0):
    return cgra_info.cgra2canon(name, tileno, DBG)

def parse_cgra_wirename(w, DBG=0):
    return cgra_info.parse_cgra_wirename(w, DBG)

# List of output ports being used as registers
REGISTERS = []

# FIXME do the thing with the globals and the init-globals...
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
    nodes = {}

    # filename = 'examples/build.171027/conv_bw_mapped.dot'
    # filename = 'examples/build.171027/pointwise_mapped.dot'
    filename = dot_filename

    if DBG: print filename
    inputstream = open(filename);
    input_lines = [] # for line in sys.stdin: input_lines.append(line)
    for line in inputstream: input_lines.append(line)
    inputstream.close()



    # for line in sys.stdin:
    for line in input_lines:
        line = line.strip()

        # Don't care about luts (for now)
        if re.search("wen_lut", line): continue


        # E.g.     '"INPUT" -> "lb_p4_clamped_stencil_update_stream$mem_1$cgramem"; # fifo_depth 64'
        # Becomes: '"INPUT" -> "mem_1"; # fifo_depth 64'

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

        # Uhhhh...if rhs node is a mem, there should be a fifo_depth comment
        process_fifo_depth(rhs,line)

    if DBG:
        print ''
        print "Found nodes and destinations:"
        for n in sorted(nodes): print "  %-20s %s" % (n, nodes[n].dests)
        print ""


# Uhhhh...if rhs node is a mem, there should be a fifo_depth comment, e.g.
def process_fifo_depth(nodename, line):
    '''
    Look for something like
        "INPUT" -> "mem_1"; # fifo_depth 64
    and add fifo_depth to "mem_1" node info
    '''
    if nodename[0:3] != 'mem': return

    fd = re.search('fifo_depth\s+(\d+)$', line).group(1)
    nodes[nodename].fifo_depth = int(fd)

    # print ''
    # print "666foo", nodename, line
    # nodes[nodename].show()


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
            # for side in range(4):
            nsides = 4
            if  is_mem_tile(i): nsides = 8
            for side in range(nsides):
                for track in range(5):
                    port = "T%d_%s_s%dt%d" % (i, dir,side,track)
                    resources[i].append(port)

        # Tile-specific resources
        pfx = 'T' + str(i) + '_'
        if  is_mem_tile(i):
            resources[i].extend([pfx+'mem_in',pfx+'mem_out'])
        elif is_pe_tile(i):
            resources[i].extend([pfx+'op1',pfx+'op2',pfx+'pe_out'])

    # TODO/FIXME add memtile, pe-specific resources etc.

    if DBG: print "Initialized %d tiles" % ntiles
    print 'PE: ', resources[0]
    print 'MEM:', resources[3]

# def is_pe_tile(tileno):  return re.search("^pe",  cgra_info.tiletype(tileno))
# def is_mem_tile(tileno): return re.search("^mem", cgra_info.tiletype(tileno))

def is_pe_tile(tileno):  return cgra_info.mem_or_pe(tileno) == 'pe'
def is_mem_tile(tileno): return cgra_info.mem_or_pe(tileno) == 'mem'

def initialize_node_INPUT():
    input  = INPUT_WIRE_T
    output = INPUT_WIRE_T
    tileno=0

    # Place 'name' in tile 'tileno' at location 'src'
    nodes['INPUT'].place(tileno, input, output)


    # Really?
    # assert INPUT.name == 'INPUT'
    # assert INPUT.input0 == False
    # assert INPUT.input1 == False
    # assert INPUT.routed == False

def is_const(nodename):  return nodename.find('const') == 0
def is_reg(nodename):    return nodename.find('reg') == 0
def is_mem(nodename):    return nodename.find('mem') == 0
def is_pe(nodename):
    return (nodename) and (\
        (nodename.find('add') == 0) or\
        (nodename.find('mul') == 0)\
         )
def is_io(nodename):
    return (nodename and re.search("INPUT|OUTPUT", nodename)) == True
    return (nodename) and (\
        (nodename == 'INPUT') or (nodename == 'OUTPUT')
        )


def dstports(name,tile):
    # 'dstports' is what you need to connect to to get the indicated node, yes?
    # E.g. for pe it's op1 AND op2; for mem it's 'mem_in'
    # for regsolo it's every outport in the tile
    # for regpe it's op1 or op2
    def T(port): return 'T%d_%s' % (tile,port)

    if is_mem(name):  p = [T('mem_in')]
    elif is_pe(name): p = [T('op1'),T('op2')]
    elif is_folded_reg(name): p = [T(nodes[name].input0)]
    else:
        # 'name' is a register, I guess;
        # so return names of all outports in the tile
        # as possible dest ports
        p = []
        if is_mem_tile(tile): nsides = 8
        else:                 nsides = 4
        for side in range(nsides):
            outport = "T%d_out_s%dt0" % (tile,side)
            p.append(outport)

    # if DBG: print 'found destination ports', p
    return sorted(p)
# Return pe input that contains the register
# e.g. regpe_input('reg_2_3') = 'op1' (unplaced regpe) or
# or   regpe_input('reg_2_3') = 'T6_op1' (placed regpe)
def regpe_input(name): return nodes[name].input0



def test_dstports():
    dstports('mem_1', 8)
    dstports('add_1', 1)
    dstports('mul_1', 1)
    dstports('reg_1', 1)
# test_dstports()


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

        op = pe.addop(k.name)

        # 'input0' is the integer value of theconstant
        kval = re.search('const(\d+)', k.name).group(1)
        k.input0 = int(kval)

        k.placed = True
        k.tileno = pe.tileno
        o = 'T%d_%s' % (pe.tileno,op)
        k.output = o
        kroute = '%s -> %s' % (k.name, o)
        k.route[pe.name] = [kroute]

        if DBG:
            kstr = '%-14s' % ("'" + k.name + "'")
            pstr = '%-20s' % ("'" + pe.name + "'")
            print "#   Folded %s into %s as %s" % (kstr,pstr,op)
        if DBG>1: pe.show(); print ""

# UNPLACED REGOP REG
# node='reg_2_2'
#   type='regsolo' ***
#   tileno= -1
#   input0='False' ***
#   input1='False'
#   output='False'
#   placed= False
#   dests=['mul_45911_460_PE']
#   route ['mul_45911_460_PE'] = []
#   net= []
# 
# PLACED REGOP REG
# node='reg_2_2'
#   type='regop' ***
#   tileno= -1
#   input0='op1' ***
#   input1='False'
#   output='mul_45911_460_PE'
#   placed= False
#   dests=['mul_45911_460_PE']
#   route ['mul_45911_460_PE'] = ['op1']
#   net= []
# 
# UNPLACED REGOP OP
# node='mul_45911_460_PE'
#   type='idunno'
#   tileno= -1
#   input0='False' ***
#   input1='False'
#   output='False'
#   placed= False
#   dests=['add_457_460_461_PE']
#   route ['add_457_460_461_PE'] = []
#   net= []
# 
# PLACED REGOP OP
# node='mul_45911_460_PE'
#   type='idunno'
#   tileno= -1
#   input0='reg_2_2' ***
#   input1='False'
#   output='False'
#   placed= False
#   dests=['add_457_460_461_PE']
#   route ['add_457_460_461_PE'] = []
#   net= []
# 
def register_folding(DBG=9):
    '''
    Process all the reg->pe pairs
    Mark by setting reg ouput to pe node e.g. 'add_x_y'
    And set input to operand e.g. 'op1'
    Also: set nodes['add_x_y'].op1 = regname FIXME do we do this?
    Also: sname->dname route must be non-None !!
    '''

    global nodes
    if DBG: print "# Process all the reg->pe pairs"
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

        # Fold it! By setting output to e.g. "add_x_y"
        # Also set nodes['add_x_y'].op1 = regname FIXME do we do this?
        # route [pe, "op1"] means duh obvious right?
        # Also: sname->dname route must be non-None !!
        op = pe.addop(reg_name) # "op1" or "op2"
        reg.input0  = op       # E.g. "op1"
        reg.output = pe_name  # E.g. "add_x_y"
        reg.route[pe_name] = [op]  

        # if DBG: print "Found foldable reg '%s'" % reg_name
        if DBG: print "#   Folded '%s' into pe '%s' as '%s'" % \
           (reg_name,pe_name,op)

        if DBG>1:
            reg.show()
            pe.show()
            print '-----'



# Happens automatically as long as we process non-regop regs LAST (right?)
# def process_input(DBG=1):
#     # INPUT tile is always tile 0
#     # INPUT wire is always wire_m1_1_BUS16_S1_T0 i.e. T0_in_s2t0
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

def parseT(wirename):
    '''E.g. parseT("T4_in_s2t4") = (4, "in_s2t4")'''
    return cgra_info.parse_resource(wirename)

def getboth(tileno, wirename):
    parse = re.search('^T\d+_(.*)',wirename)
    if parse: wirename = parse.group(1)
    tname = 'T%d_%s' % (tileno,wirename)
    return (wirename,tname)

def stripT(wirename):
    print wirename
    return re.search('^T\d+_(.*)',wirename).group(1)


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

# FIXME OH NOOOOOO too many names for the same thing?
# ALSO; shouldn't this be a func in class Node???
def is_regpe(node_name):      return is_regop(node_name)
def is_folded_reg(node_name): return is_regop(node_name)


def is_regop(regname):
    '''
    "regname" is a reg-pair if:
    - regname is the name of a reg node AND
    - regname.input0 is one of 'op1','op2' OR
    - regname.output is a PE node
    '''
    assert type(regname) == str
    if not is_reg(regname): return False

    reg_out = nodes[regname].output # E.g. "op1" or "T2_op1"
    # print reg_src;
                
    if is_pe(reg_out): return True
    else:              return False

def is_regreg(regname):
    '''These dont exist yet (right?)'''
    return False

def is_regsolo(regname):
    assert type(regname) == str
    if not is_reg(regname):  return False
    if is_regop(regname):    return False
    if is_regreg(regname): return False
    return True



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
        elif dname=='OUTPUT': otherchilds.append(dname)
        else:
            print "ERROR What is '%s'?" % dname

    sorted_schildren = otherchilds + regchilds
    # Place and route all dests

    already_done = []
    if DBG: print indent+"Processing '%s' dests %s" % (sname,sorted_schildren)
    for dname in sorted_schildren:
        was_placed = is_placed(dname)
        was_routed = is_routed(sname,dname)

        # Skip nodes that have already been placed and routed
        # EXCEPT INPUT NODE destinations

        if was_placed and was_routed:

            if sname == 'INPUT':
                # INPUT is a weird special case
                if DBG: print 'INPUT still needs processing'

            # if sname is regop and dname is its dest,
            # - keep processing
            # - use special case in place_and_route to shortcut it
            elif is_regop(sname) and nodes[sname].output == dname:
                if DBG: print indent+'REGOP still needs processing'

            else:
                print indent+"  (already processed '%s')" % dname
                already_done.append(dname)
                continue

        print indent+"  Processing '%s' dest '%s'" % (sname,dname)

        rval = place_and_route(sname,dname,indent+'  ')
        assert rval

        if DBG: pnr_debug_info(was_placed,was_routed,indent,sname,dname)

        # Do this as a separate pass for breadth-first...
        # process_nodes(dname, indent+'    ')

    # Recursively process each dest

    for dname in sorted_schildren:
        if dname in already_done: continue
        process_nodes(dname, indent+'    ')


def pnr_debug_info(was_placed,was_routed,indent,sname,dname):

        if was_placed:
            print indent+"  ('%s' was already placed in tile %d)" \
                  % (dname, nodes[dname].tileno)
        else:
            # was not placed before but is placed now
            assert is_placed(dname)
            (t,loc) = (nodes[dname].tileno,nodes[dname].input0)
            print indent+"  Placed '%s' in tile %d at location '%s'" \
                  % (dname, t, loc)

        if was_routed:
            # was not placed before but is placed now
            assert is_routed(sname,dname)
            print indent+"  ('%s' was already routed)" % dname
        else:
            # (tileno,resource) = (nodes[dname].tileno, nodes[dname].input0)
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

def place_and_route(sname,dname,indent='# ',DBG=0):

    global REGISTERS

    if is_routed(sname,dname):
        DBG=1
        if DBG: print indent+"huh already been done"
        return True

    if DBG: print indent+"PNR '%s' -> '%s'" % (sname,dname)

    # Source should alreay be placed, yes?
    if not is_placed(sname):
        print "ERROR '%s' has not been placed yet?" % sname
    assert is_placed(sname)

    # Apparently...if src is INPUT node and dest is an unallocated PE,
    # we'll put the PE in same tile with INPUT.
    # Note what if it's a reg-folded PE?

    global INPUT_OCCUPIED
    if sname=='INPUT' \
       and is_pe(dname) \
       and ('T0_pe_out' in resources[INPUT_TILENO])\
       and not INPUT_OCCUPIED:
        place_pe_in_input_tile(dname)
        INPUT_OCCUPIED = True
        return True

    if sname=='INPUT' \
       and is_folded_reg(dname) \
       and ('T0_pe_out' in resources[INPUT_TILENO])\
       and not INPUT_OCCUPIED:
        place_folded_reg_in_input_tile(dname)
        # assert False, "TODO put reg-pe folded pair in INPUT tile :("
        INPUT_OCCUPIED = True
        return True

    # Does destination have a home?
    # if not is_placed(dname):
    if True:
        #FIXME wtf with the 'if true' jazz

        DBG=1
        # print indent+"No home for '%s'"
        if DBG: print indent+"No home for '%s'" % dname

        if dname=='OUTPUT':
            process_output(sname,dname)
            return True

        # Get nearest tile compatible with target node 'dname'
        # "Nearest" means closest to input tile (NW corner)
        # dtileno = get_nearest_tile(sname, dname)
        if not is_placed(dname):
            dtileno = get_nearest_tile(sname, dname)
        else:
            dtileno = nodes[dname].tileno
            print "Acutally it does have a home already, in tile %d" % dtileno

        # FIXME will need an 'undo' for order[] list if dtileno ends up not used

        # print 'dtileno/nearest is %d' % dtileno
        if DBG: pwhere(1114, 'Nearest available tile is %d\n' % dtileno)

        # If node is pe or mem, can try multiple tracks

        if is_mem(sname): trackrange = range(5)
        elif is_pe(sname): trackrange = range(5)
        else: trackrange = [0]

        for track in trackrange:
            path = find_best_path(sname, dname, dtileno, track, DBG=1)
            if path: break
            if track != trackrange[-1]:
                print "could not find path on track %d, try next track" % track

        if not path:
            if DBG:
                pwhere(1489,
                       'Tile %d no good; undo and try again:' % dtileno)
            packer.unallocate(dtileno, DBG=0)
            packer.EXCEPTIONS.append(dtileno)
            rval = place_and_route(sname,dname,indent='# ',DBG=0)

            # Restore EXCEPTIONS, return final result.
            packer.EXCEPTIONS = []
            return rval

        print "# Having found the final path,"
        print "# 1. place dname in dtileno"
        print '# 1a. If regsolo, add name to REGISTERS for later'
        print "# 1b. If regop, place (but don't route) assoc. pe"
        print "# 2. Add the connection to src->dst route list"
        print "# 3. add all the path ports to the src net"
        print "# 4. Remove path resources from the free list"
        print ""

        print 999999999, dtileno
        # if dtileno == 15: print 666
        print "# 1. place dname in dtileno"
        d_in = CT.allports(path)[-1]

        if   is_pe(dname):  d_out = addT(dtileno,'pe_out')
        elif is_mem(dname): d_out = addT(dtileno, 'mem_out')
        elif is_regsolo(dname):
            print '# 1a. If regsolo, add name to REGISTERS for later'
            d_out = CT.find_neighbor(d_in, DBG=9)
            # assert False

            print "# Add reg's input wire to list of registers"


            # REGISTERS.append(path[-1])
            REGISTERS.append(d_in)


            print 'added reg to REGISTERS'
            print 'now registers is', REGISTERS

        elif is_regop(dname):
            d_out = place_regop_op(dname, dtileno, d_in, DBG)

        elif is_regreg(dname):
            assert False, 'what do we do with regreg??'
        else:
            assert False, 'what do we do with regs?? (see below)'
            # ANSWER: make sure reg dest is registered in REGISTERS etc.
        
        nodes[dname].place(dtileno, d_in, d_out, DBG)
        print ""
        
        # DONE see above
#         print '# 1a. If regsolo, add name to REGISTERS for later'
#         if is_regsolo(dname):
#             nodes[dname].show()
#             print 'now what?'
#             print 'add reg to REGISTERS'

        print "# 2. Add the connection to src node's src->dst route list"
        nodes[sname].route[dname] = path
        if DBG: print "#   Added connection '%s' to route from '%s' to '%s'" % \
           (path, sname, dname)
        # nodes[sname].routed[dname] = True
        if DBG: print "#   Now node['%s'].route['%s'] = %s" % \
           (sname,dname,nodes[sname].route[dname])
        pwhere(1186)
        print ""

        print "# 3. add all the path ports to the src net"
        snode = nodes[sname]
        print "BEFORE: '%s' net is %s" % (sname, snode.net)
        for p in CT.allports(path):
            snode.net.append(p)
        print "AFTER: '%s' net is %s" % (sname, snode.net)
        print ''
        
        print "# 4. Remove path resources from the free list"
        unfree_resources(path,DBG=9)
        #         assert False, 'hey hows that'
        #         print resources[1]

        print ''
        pwhere(1198)
        print "HOORAY connected '%s' to '%s'" % (sname,dname)
        if DBG:
            print ''
            nodes[sname].show()
            print ''
            nodes[dname].show()
            print ''

        if DBG: print "# Route '%s -> %s' is now complete" % (sname,dname)

        if dname == 'reg_0_1':
            print 'GOT TWO ROUTES!  WOO AND HOO!'
            # assert False,\
            #        '\n\n\nGOT TWO ROUTES!  WOO AND HOO!  What now.\n\n\n'

        # something like:
        # - change packer to use cgra_info for rc2tileno/tileno2rc DONE maybe
        # - set packer.order[] such that only mem tiles are valid (!= -1); 
        # - call the appropriate thingy mcboo

        # if DBG: print indent+"For now just place it randomly"
        # (tileno,resource) = randomly_place(dname)
        (tileno,resource) = (dtileno, d_out)

    else:
        (tileno,resource) = (-1, "already_placed")

    if not is_routed(sname,dname):
        assert False, 'huh, this has still never happened i guess...'

        # assert False, 'cannot be placed without being routed...right??'
        # print 666
        print 'Cannot be placed without being routed...right??'
        print 'Wrong, sure it can! alu with op1 routed but not yet op2, yes?'
        print 'Off to new territory...'


#         if DBG: print indent+"No route '%s -> %s'" % (sname,dname)
#         if DBG: print indent+"For now just mark it finished"
#         bogus_route = "%s -> %s BOGOSITY" % (sname,dname)
#         nodes[sname].route[dname].append(bogus_route)
#         finish_route(sname,dname)

    # return (tileno,resource)
    return True

# END def place_and_route()
########################################################################

def process_output(sname,dname, DBG=1):
    snode = nodes[sname]
    dnode = nodes[dname]
    src = snode.output

    if DBG>1:
        snode.show()
        dnode.show()

    if DBG:
        print ''
        print "1. Route from '%s' output '%s' to any avail outport in tile %d"\
              % (sname, src, snode.tileno)

    t = snode.tileno
    if DBG>1: print "\n# Tile %d free list: %s" % (t, resources[t])

    # if 'src' is an outport, just use that
    if re.search('T\d+_out_', src): outwire = src

    # else choose first avail outwire
    else:
        for w in resources[t]:
            if re.search('T\d+_out_', w):
                if DBG: print "#  - Found candidate '%s'.  Will it connect?" % w
                if cgra_info.connect_within_tile(t, src, w, DBG=0):
                    if DBG: print '#  - YES'
                    outwire = w
                    break
                else:
                    if DBG: print "#  - NO, keep looking."

    if DBG: print ''

    snode.route['OUTPUT'] = ['%s -> %s' % (src,outwire)]
    snode.net.append(outwire)
    if DBG: snode.show()

    dnode.type = 'OUTPUT'
    dnode.tileno = snode.tileno
    dnode.input0 = outwire
    dnode.input1 = False
    dnode.output = outwire
    dnode.placed = True
    dnode.net = [src,outwire]
    if DBG: dnode.show()

    return
    

def squote(txt, f=''):
    fmt = '%'+str(f)+'s'  # E.g. '%-13s' when f=-13
    return fmt % ("'" + txt + "'")


# '%-13s' % ("'" + w + "'")
def sqw(w): return squote(w, -13)

def unfree_resources(path,DBG=0):
    '''Remove all path resources from free list(s)'''
    for r in CT.allports(path):
        (tileno,x) = CT.parse_resource(r)
        if (r in resources[tileno]):
            resources[tileno].remove(r)
            if DBG: print "     %s removed from tile %d free list" \
               % (sqw(r), tileno)
            # print "  Before: %s" % resources[tileno]
            # print "  After:  %s" % resources[tileno]
        else:
            if DBG: print "     %s not in tile %d free list" \
               % (sqw(r), tileno)


def place_and_route_test(sname,dname,indent='# ',DBG=1):
    if DBG: print indent+"  PNR '%s' -> '%s'" % (sname,dname)

    # Test
    nodes[dname].tileno = 999
    nodes[dname].input0    = dname
    nodes[sname].net.append(nodes[dname].input0)
    return


def place_pe_in_input_tile(dname):
    '''INPUT connects to pe 'dname'; place it in same node as INPUT'''
    DBG=1
    sname = 'INPUT'
    if DBG:
        print "# Place input-connected PE '%s' in INPUT tile" % dname
        print "Connecting '%s' to '%s'" % (sname,dname)

    assert nodes['INPUT'].tileno == INPUT_TILE
    nodes[dname].place(INPUT_TILE, input=False, output='T0_pe_out')

    # INPUT_WIRE_T = 'T0_in_s2t0'
    # add_route(sname, dname, INPUT_TILE, 'T0_in_s2t0', 'choose_op')
    add_route(sname, dname, INPUT_TILE, INPUT_WIRE_T, 'choose_op')
    if DBG: print "# Route '%s -> %s' is now complete" % (sname,dname)
    return

    # Long form:
    # TODO global INPUTWIRE = 'T0_in_s2t0', INPUTTILE=0
    # print "# Placing pe in INPUT tile..."
    # place(dname, itile, 'pe_out')
    # 
    # print "# Routing INPUT to pe..."
    # add_route(sname, dname, itile, 'T0_in_s2t0', 'choose_op')
    # 
    # print '# Mark route COMPLETED'
    # finish_route(sname, dname)       
    # 
    # # Check that pe_out got removed from INPUT (tile0) resources
    # assert not ('pe_out' in resources[INPUT_TILENO])


def place_folded_reg_in_input_tile(dname):
    assert False, 'Note this routine has never been tried in combat and will probably fail...'

    DBG=1
    sname = 'INPUT'
    if DBG:
        print "# Put reg-pe folded pair '%s' in INPUT tile " % dname
        print "Connecting '%s' to '%s'" % (sname,dname)
        nodes[sname].show()
        nodes[dname].show()
        pname = nodes[dname].output
        nodes[pname].show()
        # print "TODO put reg-pe folded pair in INPUT tile :("
        # assert False, "TODO put reg-pe folded pair in INPUT tile :("

    assert nodes['INPUT'].tileno == INPUT_TILE

    dnode = nodes[dname] # The register, e.g. 'reg_op_1'
    
    dtileno = INPUT_TILENO
    d_in = 'T%d_%s' % (dtileno,dnode.input0) # E.g. 'T0_op1'
    d_out = place_regop_op(dname, dtileno, d_in, DBG=9)
    nodes[dname].place(dtileno, d_in, d_out, DBG)

    # A lot of this is duplicated from place() :(

    print "# 2. Add the connection to src node's src->dst route list"
    path = '%s -> %s' % (INPUT_WIRE_T, d_in)
    path = [path]
    nodes[sname].route[dname] = path
    if DBG: print "#   Added connection '%s' to route from '%s' to '%s'" % \
       (path, sname, dname)
    # nodes[sname].routed[dname] = True
    if DBG: print "#   Now node['%s'].route['%s'] = %s" % \
       (sname,dname,nodes[sname].route[dname])
    pwhere(1186)
    print ""

    # Note input goes to reg-mul_307 AND mul_312 !

    print "# 3. add all the path ports to the src net"
    snode = nodes[sname]
    print "BEFORE: '%s' net is %s" % (sname, snode.net)
    for p in CT.allports(path):
        snode.net.append(p)
    print "AFTER: '%s' net is %s" % (sname, snode.net)
    print ''

    print "# 4. Remove path resources from the free list"
    unfree_resources(path,DBG=9)
    #         assert False, 'hey hows that'
    #         print resources[1]

    print ''
    pwhere(1198)
    print "HOORAY connected '%s' to '%s'" % (sname,dname)
    if DBG:
        print ''
        nodes[sname].show()
        print ''
        nodes[dname].show()
        print ''

    if DBG: print "# Route '%s -> %s' is now complete" % (sname,dname)

    if dname == 'reg_0_1':
        print 'GOT TWO ROUTES!  WOO AND HOO!'
        # assert False,\
        #        '\n\n\nGOT TWO ROUTES!  WOO AND HOO!  What now.\n\n\n'

    return

def place_regop_op(dname, dtileno, d_in, DBG):
    DBG=9

    # d_in is last port in path leading up to dtileno;
    # Should be something like 'T25_op1'
    if DBG>2: print 7771, dname, d_in
    
    print "# 1b. If regop, place (but don't route) assoc. pe"
    d_out = nodes[dname].output
    if DBG>2: nodes[dname].show(); print ''
    
    pname = nodes[dname].output
    if DBG>2: nodes[pname].show(); print ''
    
    nodes[pname].place(dtileno, d_in, addT(dtileno,'pe_out'), DBG)
    nodes[pname].place(dtileno, d_in+'(r)', addT(dtileno,'pe_out'), DBG)
    if DBG>2: nodes[pname].show(); print ''

    REGISTERS.append(d_in)

    # dnode.route[pname] is going to be e.g. ['op1']
    # we'll need to change that to e.g. 'T10_op1' i.e. 'd_in'
    dnode = nodes[dname]
    if DBG>2: dnode.show()
    if DBG>2: print dnode.route[pname]
    assert \
           (dnode.route[pname] == ['op1']) or \
           (dnode.route[pname] == ['op2'])
    print "# 1b. Set route to op"
    dnode.route[pname] = [d_in]
    if DBG>2: dnode.show()
    return d_out


def get_nearest_tile(sname, dname, DBG=0):
    DBG=1

    # Figure how to do the first placement INPUT -> mem_1 maybe
    # Use new connection thingies maybe

    if DBG:
        print ''
        print "# order before get_nearest():"
        packer.FMT.order()
        print ''

    dtype = nodes[dname].tiletype()
    stileno = nodes[sname].tileno

    # If dname is a reg node, maybe it can go in the same tile with sname?
    # regsolo => not part of a regpe or regreg pair
    if is_regsolo(dname) and not is_regop(sname):
        print "okay we will try to put it in the same tile with", sname
        return stileno

    # print "# i'm in tile %s" % packer.FMT.tileT(sname)
    nearest = packer.find_nearest(stileno, dtype, DBG=0)
    assert nodes[dname].tiletype() == cgra_info.mem_or_pe(nearest)

    # print 'foudn nearest tile', nearest
    assert nearest != -1

    # stile = nodes[sname].tileno
    # dtile = nodes[dname].tileno

    # print 'dname is type %s and...' % dtype,
    # print '"nearest" is type %s' % cgra_info.mem_or_pe(nearest)
    assert nodes[dname].tiletype() == cgra_info.mem_or_pe(nearest)

    if DBG:
        print "# order after get_nearest():"
        packer.FMT.order()
        print ''

    return nearest


########################################################################
########################################################################
########################################################################
# scrub scrub scrub!  from here down

# FIXME this is bad.  very very...bad
global ENDPOINT_MUST_BE_FREE
ENDPOINT_MUST_BE_FREE = False

def find_best_path(sname,dname,dtileno,track,DBG=1):
    # DBG=1

    # next:
    # trying to route sname/stileno to dname/dtileno
    # foreach path in connect_{hv,vh}connect(ptile,dtile)
    #   foreach port in snode.input0,snode.net
    #     (begin,end) = (path[0],path[-1])
    #     if src.canconnect(sname.input0,begin) and src.canconnect(end,dname)
    #        paths.append (begin,path,end)
    # choose a path in paths

    # trying to route sname/stileno to dname/dtileno
    snode = nodes[sname]
    dnode = nodes[dname]
    stileno = snode.tileno
    pwhere(1289,\
        "Want to route from src tile %d ('%s') to dest tile %d ('%s')" \
        % (stileno, sname, dtileno, dname))

    nodes[sname].show()

    # Want tileno associated with output;
    # note for e.g. regsolo, input and output ports are in different tiles;
    # want tileno associated with output...right?  Right!
    stileno = int(re.search('^T(\d+)', snode.output).group(1))

    if dtileno == stileno:
        # This can happen when e.g. we're trying to connect an ALU
        # to a register, both in the same tile
        # assert dest==reg if you wanta...

        print 'src and dst in same tile; thats okay'
        print 'BUT must make sure we choose a free port'
        # FIXME this is bad
        global ENDPOINT_MUST_BE_FREE
        ENDPOINT_MUST_BE_FREE = True
        p = connect_endpoint(snode, snode.output, dname, dtileno, DBG=DBG)
        ENDPOINT_MUST_BE_FREE = False
        return p

    # foreach path p in connect_{hv,vh}connect(ptile,dtile)
    # FIXME for now only looking at track 0(!)
    phv = CT.connect_tiles(stileno,dtileno,track,dir='hv',DBG=DBG-1)
    if DBG>2: print '  Found path phv', phv

    pvh = CT.connect_tiles(stileno,dtileno,track,dir='vh',DBG=DBG-1)
    if DBG>2: print '  Found path pvh', pvh

    # FIXME need a better way to determine if path is straight-line
    if pvh==phv:
        if DBG>2: print "  NOTE path is a straight line"

    which = 'pvh'
    for path in [pvh,phv]:
        if DBG: pwhere(1325,
                       "Evaluating %s path %s" % (which,path)); which = 'phv'
        
        final_path = eval_path(path, snode, dname, dtileno, DBG)
        if final_path:
            # FIXME For now, use first path found
            # FIXME for future, keep findin paths and return them all
            return final_path

        if pvh==phv:
            # duh.  straight-line path
            # don't do it twicet
            break 

        # choose a path in paths


# FIXME WHAY ISN'T ALL THIS CONNECT STUFF IN THE
# CONNECT_TILES LIBRARY WHERE IT BELONGS!!?
def eval_path(path, snode, dname, dtileno, DBG=0):
    # Given 'path' from src node 'snode' in stileno
    # to dst node 'dname' in possible dest tile 'dtileno',
    # see if path is valid
    stileno = snode.tileno
    sname   = snode.name

    # part 1 verify the tile-to-tile path
    # Check every port on the path for availability to snode
    if not ports_available(snode, path, DBG): return False
    if DBG:
        print "YES path from T%d to T%d is available\n" % (stileno,dtileno)

    # part 2 verify begin and end points
    final_path = can_connect_ends(path, snode, dname, dtileno, DBG)
    if not final_path:
        print "  Cannot connect '%s' to endpoint blah '%s'?" % (p, path[0])
        assert False, 'disaster could not find a path (and/or could try again with a different tile?'
        return False

    return final_path

def can_connect_ends(path, snode, dname, dtileno, DBG=0):
    stileno = snode.tileno
    sname   = snode.name

    if DBG: print "Can we attach nodes to path endpoints '%s' and '%s'?"\
       % (path[0],path[-1])

    if DBG:
        print "1. Attach source node '%s' to path beginpoint '%s'"\
              % (sname, path[0])

    assert snode.output in snode.net,\
           "'%s' output '%s' is not in '%s' net!!?" % (sname, snode.input0,sname)

    cbegin = connect_beginpoint(snode, path[0],DBG)
    if not cbegin:
        print "  Cannot connect '%s' to endpoint blah '%s'?" % (p, path[0])
        assert False, 'disaster could not find a path'
        return False

    #######################################
    if DBG: print "2. Attach path endpoint '%s' to dest node '%s' (%s)"\
       % (path[-1], dname, where(1413))

    cend = connect_endpoint(snode, path[-1], dname, dtileno, DBG)
    if not cend:
        print "  Cannot connect '%s' to endpoint blah '%s'?" % (p, path[0])
        assert False, 'disaster could not find a path'
        return False

    # print 'ready to connect endpoint! %s' % cend

    # For now, return first path found
    # FIXME for future, keep findin paths and return them all
    final_path = cbegin + path[1:-1] + cend
    print "SUCCESS! Final path from '%s' to '%s' is: %s\n" \
          % (sname,dname,final_path)

    # middle part was verified previously.
    # looks like we're good to go!

    # For now, return first valid path.
    # FIXME/TODO later will want to construct all paths
    # (or at least hv vs.vh) and compare thetwo
    return final_path
            

def ports_available(snode, path, DBG=0):
    stileno = snode.tileno
    sname   = snode.name

    if DBG>2: print "# is entire path available to src net?"
    path_ports = CT.allports(path)
    if DBG>2: print "#   entire path: ", path_ports

    for p in path_ports:
        if not snode.is_avail(p,DBG):
            if DBG: print "NO path not available"
            return False

    return True


def connect_beginpoint(snode, beginpoint, DBG=0):
    stileno = snode.tileno
    sname   = snode.name

    # canon_src = 'T%d_%s' % (stileno, snode.input0)
    # plist = [canon_src] + snode.net

    plist = sorted(snode.net)
    # print plist
    # FIXME should only look at ports in same tile as beginpoint...RIGHT?
    # FIXME verify no redundancies in plist
    if DBG:
        print "   Ports avail to source node '%s': %s" % (sname,plist)
        print "   Take each one in turn"

    for p in plist:
        print "     Can '%s' connect to beginpoint '%s'?" % (p, beginpoint)

        # Who's the diiot?  I'm the diiot.
        # cbegin = can_connect_begin(snode, snode.input0, beginpoint, DBG)
        cbegin = can_connect_begin(snode, snode.output, beginpoint, DBG)

        if cbegin: return cbegin
        else:
            print "  Cannot connect '%s' to beginpoint '%s'?" % (p, beginpoint)
            print "  Try next port in the list?"

    return False

def connect_endpoint(snode, endpoint, dname, dtileno,DBG):

    # 'dstports' is what you need to connect to to get the indicated node, yes?
    # E.g. for pe it's op1 AND op2; for mem it's 'mem_in'
    # for regsolo it's every outport in the tile
    # for regpe it's op1 or op2
    dplist = dstports(dname,dtileno)
    if DBG:
        print "   In-ports avail to dest node '%s': %s" % (dname,dplist)
        print "   Take each one in turn"

        #     # NOPE this does not help at all :(
        #     # If endpoint is on side 0 or 3, choose op2 preferentially over op1 and vice versa
        #     dplist = sort_dplist(endpoint,dplist)

    for dstport in dplist:

        print "     Can path endpoint '%s' connect to dest port '%s'?" \
              % (endpoint, dstport)

        global ENDPOINT_MUST_BE_FREE
        if ENDPOINT_MUST_BE_FREE and (dstport not in resources[dtileno]):
            print "     - OOP its being used by someone else, try another one\n"
            continue

        cend = can_connect_end(snode, endpoint, dstport,DBG)
        if cend: return cend
        else:
            print "  Cannot connect path endpoint '%s' to dest port '%s'" \
                  % (endpoint, dstport)
            print "  Try next port in the list?"

    return False

# NOPE
# def sort_dplist(endpoint, dplist, DBG=9):
#     # E.g. endpoint='T2_in_20t0' and dplist = ['T2_op1', 'T2_op2']
#     # If endpoint is on side 0 or 2, choose op2 preferentially over op1 and vice versa
# 
#     (T,d,side,t) = cgra_info.parse_canon(endpoint)
#     if DBG:
#         print '666 Sorting dplist %s' % dplist
#         print '  I think endpoint is on side %d' % side
#         print '  That means we preferentially choose op%d' % (2-side%2)
# 
#     op1 = 'T%d_op1' % T
#     op2 = 'T%d_op2' % T
# 
#     newlist = []
#     if   (side%2==0) and (op2 in dplist): newlist = [op2]
#     elif (side%2==1) and (op1 in dplist): newlist = [op1]
#         
#     for dp in dplist:
#         if dp not in newlist: newlist.append(dp)
# 
#     if DBG:
#         print 'Sorted list is %s\n' % newlist
# 
#     return newlist


def can_connect_begin(snode,src,begin,DBG=0):
    cbegin = can_connect(snode,src,begin,DBG)
    if cbegin:
        print '   Ready to connect beginpoint %s (%s)' % (cbegin, where(1509))
        print ''
    return cbegin

def can_connect_end(snode, end,dstport,DBG=0):
    cend = can_connect(snode, end,dstport,DBG)
    if cend:
        print '   Ready to connect endpoint %s (%s)' % (cend, where(1516))
        print ''
    return cend

def can_connect(snode, p1, p2, DBG=0):
    # Can we connect ports p1 to p2 as part of 'snode' net?
    if DBG>1: print "Can we connect '%s' to '%s' as part of '%s' net? (%s)"\
       % (p1,p2,snode,where(1536))
    c = snode.connect(p1,p2,DBG=DBG)
    if not c:
        if DBG>1: print 'oops no route from p1 to p2'
        return False
    return c




# def randomly_place(dname, DBG=0):
#     '''
#     Assign dname to any random available resource
#     Well maybe not completely random.
#     Assign mem to mem tiles ONLY using resource 'mem_out'
#     '''
#     if is_mem(dname): dtype='mem'
#     else:             dtype='pe'
# 
#     ntiles = len(resources) # len(list) = length (number of items in) list
#     for tileno in range(ntiles):
# 
#         if is_mem_tile(tileno): ttype='mem'
#         else:                   ttype='pe'
#         if dtype != ttype: continue
# 
#         if is_regop(dname):
#             # regops come from register-folding optimization pass
#             # They look like this:
#             # 
#             # node='reg_2_2'
#             #   type='regop' ***
#             #   tileno= -1
#             #   input0='op1' ***
#             #   input1='False'
#             #   output='mul_45911_460_PE'
#             #   placed= False
#             #   dests=['mul_45911_460_PE']
#             #   route ['mul_45911_460_PE'] = ['op1']
#             #   net= []
#             # 
#             # Before placing regop, must first place target pe
#             pe = nodes[dname].dests[0]
#             if not is_placed(pe): randomly_place(pe)
# 
#             # regop goes in same tile as target pe as op1 or op2
#             tileno = nodes[pe].tileno
#             if   (re.search('op1$', nodes[dname].input0)): op = 'op1'
#             elif (re.search('op2$', nodes[dname].input0)): op = 'op2'
#             else: assert(0)
#                   
#             nodes[dname].place(tileno,'XXX',op)
#             return (tileno,op)
# 
#         elif  is_pe(dname): r='pe_out'
#         elif is_mem(dname): r='mem_out'
#         else:
#             # It's an unassigned register, yes?
#             # Although maybe could be double-register pair someday.
#             # Randomly choose the first outport you find
#             # (technically should be out-port but oh well
# 
#             regex = re.compile('^out')
#             outs = filter(regex.match, resources[tileno])
#             if outs == []: continue
#             else:          r = outs[0]
#         
#         if r not in resources[tileno]: continue
#         else:
#             if DBG:
#                 print "# Randomly assigning '%s' to tile %d resource '%s'" \
#                       % (dname,tileno,r)
#             nodes[dname].place(tileno,'XXX',op)
#             return (tileno,r)

def is_placed(nodename):
    # return (nodes[dname].tileno != -1)
    return nodes[nodename].is_placed()

def is_routed(sname,dname):
    return nodes[sname].is_routed(dname)


def test_connect():

    print '######################################################'
    print '# serpent.py: Read cgra info'
    cgra_info.read_cgra_info(verbose=True)


    print '######################################################'
    print '# serpent.py: Initialize node and tile data structures'
    init_tile_resources(DBG=0)
    build_nodes(DBG=0)
    initialize_routes()
    initialize_node_INPUT()

    print 'TEST: who can reach pe_out_res?'
    rlist = cgra_info.fan_out('pe_out_res', 0, DBG=1)
    print rlist


    print 'TEST: who can reach to_cgra(pe_out)?'
    rlist = cgra_info.fan_out(to_cgra('pe_out'), 0)
    print 'boo'
    print rlist


    print 'TEST: can connect pe_out to out_s1t1 in INPUT tile?'
    rval = nodes['INPUT'].connect('pe_out', 'out_s1t1', T=0, DBG=9)
    print rval

    print 'TEST: can find double-connection from  in_s1t1 to op1 in tile 4?'
    print resources[0]
    rval = nodes['INPUT'].connect('in_s1t1', 'op1', T=0, DBG=9)
    print rval

DO_TEST=0
if DO_TEST:
    test_manhattan_distance_rc()
    test_fan_out()

    print 'test the new stuff'
    test_connect()
    exit()


main()







# BOOKMARK
# NEXT: implement and test cgra_info.reachable (see below)

#         rlist = cgra_info.reachable(T,a)
#         if is_avail(b) and b in rlist: return a->b
#         else for r in rlist: if canconnect(r,b) return ['a->r','r->b']

# reachable(tileno,src)
# given tileno and src::src in {pe_out, mem_out, in_s1t1}
# return a list of everything that src can connect to in the tile

# #         else if b is out_s<S> and is_avail in_s<S> and in_s<S> in reachable:
# #             return ['a->in

#         # 'a' wires pe_out, mem_out (rdata) can connect to any outwire
#         if re.search('out$', a):
#             # If 'a' is an '_out' then b should be an outwire
#             assert re.search('^T\d+_out', b)
#             return '%s -> %s' % (a,b)
# 
#         # a should be inwire now
#         assert re.search('^T\d+_in', a)
# 
#         # 'a' inwire can connect to any wire not on same side
#         if re.search('^T\d+_out', b):
#             (Ta,da,sa,ta) = CT.parsewire(a)
#             (Tb,db,sb,tb) = CT.parsewire(b)
#             return not (sa == sb)
# 
#         # b is one of ['mem_in','op1','op2'] (mem_in == wdata maybe)
#         # who can connect to mem_in (wdata)? anything on side 2
# 
# 
# 
# 
#         (Ta,da,sa,ta) = CT.parsewire(a)
#         (Tb,db,sb,tb) = CT.parsewire(b)
#         assert Ta == Tb
# 

        
