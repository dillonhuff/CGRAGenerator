#!/usr/bin/python

import sys;
import re;

# from ../decoder/lib import cgra_info
sys.path.append("../decoder")
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

def pwhere(lno, txt=''):
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
    cgra_info.read_cgra_info()
    manhattan_distance_rc(DBG=1)
    print ''

def test_reachable():
    # S0 only connecst to four sides
    cgra_info.reachable('in_BUS16_S0_T0', 0, DBG=1)
    
    # S2 can also connect to op1
    cgra_info.reachable('in_BUS16_S2_T0', 0, DBG=1)
    
    cgra_info.reachable('mem_out', 3, DBG=1)
    cgra_info.reachable('pe_out_res', 0, DBG=1)

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

    print '######################################################'
    print '# serpent.py: Read cgra info'
    cgra_filename = get_default_cgra_info_filename()
    cgra_info.read_cgra_info(cgra_filename)

    print '######################################################'
    print '# serpent.py: Initialize the packer'
    packer.USE_CGRA_INFO = True
    packer.init_globals() # this is crucial out there
    print "# here's the grid!"
    print '# '
    packer.FMT.grid()
    print ''

    print '######################################################'
    print '# serpent.py: Initialize node and tile data structures'
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

    print '########################################'
    print '# serpent.py: constant folding - do this LAST'
    constant_folding(DBG=1)
    print "# consts should be gone now"

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

        self.input  = False  # E.g. T0_out_s0t0 or 'add_x_y.op1'
        self.output = False
        # EXAMPLES   input           output
        # regpe      op1             'alu_3_2' (unplaced)
        # regpe      T0_ops          'alu_3_2' (placed)

        # regreg     T0_out_s0t0     'reg_2_4'
        # mem        T3_mem_in       T3_mem_out
        # pe         T0_ops          T0_pe_out
        # regsolo    T0_out_s0t0     T1_in_s2t0

        self.dests = []
        self.placed = False
        self.route  = {}   # E.g. route['INPUT'] = [T0_in_s0t0, 'T0_op1']

        # self.routed = {}   # E.g. routed['INPUT'] = True
        # Use self.is_routed() instead (see below)

        self.net = []
        # self.processed = False

    # NOBODY should alter net except via these functions: BOOKMARK


    def type(self):
        if self.name[0] == 'm': return 'mem'
        else: return 'pe'

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
        print "node='%s'" % self.name        
        print "  tileno= %s" % self.tileno
        print "  op1='%s'"   % self.op1
        print "  op2='%s'"   % self.op2

        print "  in= '%s'" % self.input
        print "  out='%s'" % self.output

        print "  placed= %s" % self.placed
        print "  dests=%s" % self.dests
        # print "  route=%s" % self.route
        prettyprint_dict("  route ", self.route)
        print "  net= %s" % self.net

    def is_routed(dest_name): return self.route[dest_name] != []

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
            print "       %-11s available in '%s' nodenet" \
                  % (rname, self.name)
            return True

        if DBG>2: print "is_avail: looking for '%s' in tile %d resources %s" \
              % (rname, tileno, resources[tileno])
        if rname in resources[tileno]:
            print "       %-11s available in free list for tile %d"\
                  % (rname, tileno)
            return True

        else:
            print "  %-11s is not available to node '%s'" % (r, self.name)
            return False

    def place(self,tileno,input,output,DBG=0):
        '''
        Place node "name" in tile "tileno"
        with input 'input' and output 'output'
        where e.g. 'input'  = 'T2_ops'    or 'T1_out_s0t1'
        where e.g. 'output' = 'T2_pe_out' or 'T2_in_s2t1'
        '''
        name = self.name

        if   is_pe(name):
            assert re.search('ops$',     input)
            assert re.search('pe_out$',  output)
        elif is_mem(name):
            assert re.search('mem_in$',  input)
            assert re.search('mem_out$', output)
        # elif is_reg(name)...
        # assert input = .*_out_.*, output = .*_in_.* etc.

        if self.placed:
            print "ERROR %s already placed at %s" % (name, self.input)
            assert False, "ERROR %s already placed at %s" % (name, self.input)

        self.tileno = tileno
        self.input  = input
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
#     print 'foo'
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

        if DBG: print "       Looks like both are available to '%s' (%s)" \
           % (self.name, where(451))
        if DBG: print ''

        # If can reach a->b directly, return a->b'

        (aprime,bprime) = (to_cgra(a),to_cgra(b))
        print "       Ask cgra: can '%s' connect to '%s'? (%s)"\
              % (aprime,bprime,where(457))

        # rlist = all ports that a can reach in tile T
        rlist = cgra_info.reachable(to_cgra(a), T, DBG=0)
        print "         %s can connect to %s" % (aprime,rlist)

        bprime = to_cgra(b)
        print "         Is '%s' in the list?" % bprime
        if bprime in rlist:
            if DBG: print '         YES'
            return ['%s -> %s' % (a,b)]

        if DBG: print "           NO"
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
        print "maybe can connect intermediary"
        for r in rlist:
            rprime = from_cgra(r, T)
            print "maybe can connect intermediary '%s' -> '%s' -> '%s'"\
                  % (a,rprime,b)
            p1 = self.connect(a,rprime,T,DBG)
            if not p1: continue
            p2 = self.connect(rprime,b,T,DBG)
            if not p2: continue

            print "Found double connection.  What a day!"
            return p1+p2

        print "no good"
        return False
            
def addT(tileno, r):
    '''Embed tileno in resource 'r' e.g. "mem_out" => "T3_mem_out"'''
    return 'T' + str(tileno) + '_' + r

def parse_resource(r):
    '''
    resource must be of the form "T0_in_s0t0" or "T3_mem_out"
    returns tileno+remains e.g. parse_resource("T0_in_s0t0") = (0, 'in_s0t0')
    '''
    parse = re.search('^T(\d+)_(.*)', r)
    if not parse: assert False
    (tileno,resource) = (int(parse.group(1)), parse.group(2))
    return (tileno,resource)

def parsewire(w):
    '''wire MUST have embedded tileno e.g. "T0_in_s0t0"'''
    # Examples
    # "T0_in_s0t0" returns (0, 'in', 0, 0)
    # "T3_mem_out" returns (3, 'mem_out', -1, -1)
    (tileno,w) = parse_resource(w)

    parse = re.search('(in|out)_s(\d+)t(\d+)', w)
    if not parse: return (tileno,w,-1,-1)

    (dir,side,track) = (
        parse.group(1), parse.group(2), parse.group(3))
    return (int(tileno),dir,int(side),int(track))



def prettyprint_dict(dictname, dict):
    for d in sorted(dict):
        print "%s%-20s = %s" % (dictname, [d], dict[d])
    

# def reachable(a,b):
#     # Will use cgra_info.reachable(), but first have to rewrite some things
#     # E.g. 'T0_in_s1t2' => 'in_BUS16_S1_T2'
    

def to_cgra(name, DBG=0):
    # Valid names include "T0_in_s0t0","T3_mem_out"
    # Valid combinations:       a               b
    #                     pe_out|mem_out      out_.*
    #                          in.*           out_.*
    #                          in.*      {mem_in,op1,op2}   

    if DBG>1: print "converting", name

    # E.g. 'T0_in_s1t2' => 'in_BUS16_S1_T2'
    (T,d,s,t) = parsewire(name)
    # assert T != -1
    if DBG>1: print (T,d,s,t)
    if s == -1:
        # not a wire; name is returned as 'd'
        if d == 'op1'   :  newname = 'data0'
        if d == 'op2'   :  newname = 'data1'
        if d == 'pe_out':  newname = 'pe_out_res'

        if d == 'mem_in':  newname = 'wdata'
        if d == 'mem_out': newname = 'rdata'

    else:
        assert s < 4, 'oops need more rewrites'
        newname = '%s_BUS16_S%d_T%d' % (d,s,t)
        if is_mem_tile(T):
            newname = '%s_%d_BUS16_S%d_T%d' % (d,s/4,s%4,t)


    if DBG: print "to_cgra: cgra name for '%s' is '%s'" % (name, newname)
    if DBG: print ''

    return newname


def from_cgra(name, tileno):
    print "converting", name
    (dir,side,track) = parse_cgra_wirename(name)
    print (dir,side,track)

    if dir == -1:
        # not a wire
        if name == 'data0':      newname = 'op1'
        elif name == 'data1':      newname = 'op2'
        elif name == 'pe_out_res': newname = 'pe_out'
        
        elif name == 'wdata': newname = 'mem_in'
        elif name == 'rdata': newname = 'mem_out'
        else: assert False, 'sb_wire or something?'
    else:
        newname = '%s_s%st%s' % (dir,side,track)

    print 'from_cgra: new name is', newname
    print ''
    newname = 'T%d_%s' % (tileno, newname)
    return newname

def parse_cgra_wirename(w):
    parse = re.search('(in|out)_BUS16_S(\d+)_T(\d+)', w)
    print "in", w
    rval = (-1,-1,-1)
    if (parse):
        print 'parsed'
        (dir,side,track) = (parse.group(1), parse.group(2), parse.group(3))
        rval = (dir,side,track)
    print 'out', rval
    return rval

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
        print ''
        print "Found nodes and destinations:"
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
    print resources[0]

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
    # assert INPUT.op1 == False
    # assert INPUT.op2 == False
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
    elif is_folded_reg(name): p = [T(nodes[regname].input)]
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
def regpe_input(name): return nodes[name].input



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

        if DBG:
            kstr = '%-14s' % ("'" + k.name + "'")
            pstr = '%-20s' % ("'" + pe.name + "'")
            print "#   Folded %s into %s as %s" % (kstr,pstr,op)
        if DBG>1: pe.show(); print ""


def register_folding(DBG=9):
    '''
    Process all the reg->pe pairs
    Mark by setting reg ouput to pe node e.g. 'add_x_y'
    And set input to operand e.g. 'op1'
    Also: set nodes['add_x_y'].op1 = regname
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

        # Fold it! By setting src to e.g. "add_x_y.op1"
        # Also set nodes['add_x_y'].op1 = regname
        # route [pe, "op1"] means duh obvious right?
        op = pe.addop(reg_name) # "op1" or "op2"
        # reg.input  = "%s.%s" % (pe_name, op) # E.g. "add_x_y.op1"
        reg.input  = op       # E.g. "op1"
        reg.output = pe_name  # E.g. "add_x_y"

#         # Fold it!
#         reg.input  = 'REGPE'
#         reg.output = pe_name       # E.g. "add_x_y"



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

def finish_route(sname,dname, DBG=0):
    '''Mark *route completed* by adding dname to sname netlist'''
    nodes[sname].net.append(dname)

    if DBG: print "# Route '%s -> %s' is now complete" % (sname,dname)
    if DBG: print "# Add '%s' to nodes['%s'].net"      % (sname,dname)
    if DBG: print "#   Now node['%s'].net = %s" % (sname,nodes[sname].net)
    



def is_regop(regname):
    '''
    "regname" is a reg-pair if:
    - regname is the name of a reg node AND
    - regname.input is one of 'op1','op2' OR
    - regname.output is a PE node
    '''
    assert type(regname) == str
    if not is_reg(regname):         return False

    reg_out = nodes[regname].output # E.g. "op1" or "T2_op1"
    # print reg_src;
                
    if is_pe(reg_out): return True
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

        # Everything from here down is just debug info right?
        # Not sure about these...!
        if was_placed:
            print indent+"  ('%s' was already placed)" % dname
        else:
            # was not placed before but is placed now
            assert is_placed(dname)
            (t,loc) = (nodes[dname].tileno,nodes[dname].input)
            print indent+"  Placed '%s' in tile %d at location '%s'" % (dname, t, loc)

        if was_routed:
            # was not placed before but is placed now
            assert is_routed(dname)
            print indent+"  ('%s' was already routed)" % dname
        else:
            # (tileno,resource) = (nodes[dname].tileno, nodes[dname].input)
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

    # Apparently...if src is INPUT node and dest is an unallocated PE,
    # we'll put the PE in same tile with INPUT.
    # Note what if it's a reg-folded PE?

    if sname=='INPUT' \
       and is_pe(dname) \
       and ('T0_pe_out' in resources[INPUT_TILENO]):

        place_pe_in_input_tile(dname)
        return

    if sname=='INPUT' \
       and is_folded_reg(dname) \
       and ('T0_pe_out' in resources[INPUT_TILENO]):

        place_folded_reg_in_input_tile(dname)
        assert False, "TODO put reg-pe folded pair in INPUT tile :("
        return

    # Does destination have a home?
    if not is_placed(dname):

        DBG=1
        # print indent+"No home for '%s'"
        if DBG: print indent+"No home for '%s'" % dname

        # Get nearest tile compatible with target node 'dname'
        # "Nearest" means closest to input tile (NW corner)
        dtileno = get_nearest_tile(dname)
        
        # FIXME will need an 'undo' for order[] list if dtileno ends up not used

        # if dtileno==8: print 666

        # print 'dtileno/nearest is %d' % dtileno
        if DBG: pwhere(1114, 'Nearest available tile is %d\n' % dtileno)

        path = find_best_path(sname, dname, dtileno)
        
        print "# Having found the final path,"
        print "# 1. place dname in dtileno"
        print "# 2. Add the connection to src->dst route list"
        print "# 3. add all the path ports to the src net"
        print "# 4. what else?"
        print ""

        print "# 1. place dname in dtileno"
        print 999999999, dtileno
        # d_in = path[-1] # right?  RIGHT???  Wrong :(
        d_in = CT.allports(path)[-1]

        if   is_pe(dname):  d_out = addT(dtileno,'pe_out')
        elif is_mem(dname): d_out = addT(dtileno, 'mem_out')
        else:
            assert False, 'what do we do with regs?? (see below)'
            # ANSWER: make sure reg dest is registered in REGISTERS etc.

        
        nodes[dname].place(dtileno, d_in, d_out, DBG=1)
        print ""
        
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
        
        print "#4. Remove resources from the free list"
#         assert False, 'hey time to do this thing'
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

        print 666
        if DBG: print "# Routefoo '%s -> %s' is now complete" % (sname,dname)

        # No.  Why?  No.
        # Yes.  B/c 'is_routed' depends on finding name in net.
        if DBG: print "# Add '%s' to '%s' net, to show that it's been routed"\
           % (sname,dname)
        # uhhhh...is this a good idea?
        # aka finish_route(sname,dname)
        # '''Mark *route completed* by adding dname to sname netlist'''
        nodes[sname].net.append(dname)
        if DBG: print "#   Now node['%s'].net = %s" % (sname,nodes[sname].net)
        if DBG: print ''

#         # BOOKMARK
#         assert False, '\nBOOKMARK: routing it'
#         assert False, '\nBOOKMARK: route it!'

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
        assert False, 'cannot be placed without being routed...right??'
#         if DBG: print indent+"No route '%s -> %s'" % (sname,dname)
#         if DBG: print indent+"For now just mark it finished"
#         bogus_route = "%s -> %s BOGOSITY" % (sname,dname)
#         nodes[sname].route[dname].append(bogus_route)
#         finish_route(sname,dname)

    return (tileno,resource)

def place_pe_in_input_tile(dname):
    '''INPUT connects to pe 'dname'; place it in same node as INPUT'''
    sname = 'INPUT'

    DBG=1
    if DBG: print "# Place input-connected PE '%s' in INPUT tile" % dname
    if DBG: print "Connecting '%s' to '%s'" % (sname,dname)

    INPUT_TILE = 0; assert nodes['INPUT'].tileno == INPUT_TILE

    nodes[dname].place(INPUT_TILE, 'T0_ops', 'T0_pe_out')
    
    # add_route(sname, dname, INPUT_TILE, 'T0_in_s2t0', 'choose_op')
    add_route(sname, dname, INPUT_TILE, INPUT_WIRE_T, 'choose_op')
    finish_route(sname, dname)       
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
        print "TODO put reg-pe folded pair in INPUT tile :("
        assert False, "TODO put reg-pe folded pair in INPUT tile :("


def get_nearest_tile(dname, DBG=0):

    DBG=1
    # Figure how to do the first placement INPUT -> mem_1 maybe
    # Use new connection thingies maybe

    if DBG:
        print ''
        print "# order before get_nearest():"
        packer.FMT.order()
        print ''

    dtype = nodes[dname].type()

    # print "# i'm in tile %s" % packer.FMT.tileT(sname)
    nearest = packer.find_nearest(0, dtype, DBG=0)

    # print 'foudn nearest tile', nearest
    assert nearest != -1

    # stile = nodes[sname].tileno
    # dtile = nodes[dname].tileno

    # print 'dname is type %s and...' % dtype,
    # print '"nearest" is type %s' % cgra_info.mem_or_pe(nearest)
    assert nodes[dname].type() == cgra_info.mem_or_pe(nearest)

    if DBG:
        print "# order after get_nearest():"
        packer.FMT.order()
        print ''

    return nearest


########################################################################
########################################################################
########################################################################
# BOOKMARK: scrub scrub scrub!  from here down

def find_best_path(sname,dname,dtileno):
        DBG=1

        # next:
        # trying to route sname/stileno to dname/dtileno
        # foreach path in connect_{hv,vh}connect(ptile,dtile)
        #   foreach port in snode.input,snode.net
        #     (begin,end) = (path[0],path[-1])
        #     if src.canconnect(sname.input,begin) and src.canconnect(end,dname)
        #        paths.append (begin,path,end)
        # choose a path in paths

        # trying to route sname/stileno to dname/dtileno
        snode = nodes[sname]
        dnode = nodes[dname]
        stileno = snode.tileno
        pwhere(1289,\
            "Want to route from src tile %d ('%s') to dest tile %d ('%s')" \
            % (stileno, sname, dtileno, dname))

        # foreach path p in connect_{hv,vh}connect(ptile,dtile)
        # FIXME for now only looking at track 0(!)
        phv = CT.connect_tiles(stileno,dtileno,track=0,dir='hv',DBG=DBG-1)
        if DBG>2: print '  Found path phv', phv

        pvh = CT.connect_tiles(stileno,dtileno,track=0,dir='vh',DBG=DBG-1)
        if DBG>2: print '  Found path pvh', pvh

        # FIXME need a better way to determine if path is straight-line
        if pvh==phv:
            if DBG>2: print "  NOTE path is a straight line"

        for path in [pvh,phv]:

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



def eval_path(path, snode, dname, dtileno, DBG=0):
    # Given 'path' from src node 'snode' in stileno
    # to dst node 'dname' in possible dest tile 'dtileno',
    # see if path is valid
    if DBG: pwhere(1325, "Evaluating path %s" % path)
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

    # canon_src = 'T%d_%s' % (stileno, snode.input)
    # plist = [canon_src] + snode.net

    assert snode.input in snode.net
    plist = sorted(snode.net)
    # print plist
    # FIXME should only look at ports in same tile as beginpoint...RIGHT?
    # FIXME verify no redundancies in plist
    if DBG:
        print "   Ports avail to source node '%s': %s" % (sname,plist)
        print "   Take each one in turn"

    for p in plist:
        print "     Can '%s' connect to beginpoint '%s'?" % (p, beginpoint)

        cbegin = can_connect_begin(snode, snode.input, beginpoint, DBG)
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
        print "   Want to route endpoint to a dest port %s" % dplist

    if DBG:
        print "   In-ports avail to dest node '%s': %s" % (dname,dplist)
        print "   Take each one in turn"

    for dstport in dplist:
        print "     Can path endpoint '%s' connect to dest port '%s'?" \
              % (endpoint, dstport)

        cend = can_connect_end(snode, endpoint, dstport,DBG)
        if cend: return cend
        else:
            print "  Cannot connect path endpoint '%s' to dest port '%s'" \
                  % (endpoint, dstport)
            print "  Try next port in the list?"

    return False

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




# FIXME OH NOOOOOO
def is_regpe(node_name):      is_regop(node_name)
def is_folded_reg(node_name): is_regop(node_name)
#     if not is_reg(node_name): return False
#     reg = nodes[node_name]
#     return is_pe(reg.input)


def place_and_route_test(sname,dname,indent='# ',DBG=1):
    if DBG: print indent+"  PNR '%s' -> '%s'" % (sname,dname)

    # Test
    nodes[dname].tileno = 999
    nodes[dname].input    = dname
    nodes[sname].net.append(nodes[dname].input)
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
            if   (re.search('op1$', nodes[dname].input)): op = 'op1'
            elif (re.search('op2$', nodes[dname].input)): op = 'op2'
            else: assert(0)
                  
            nodes[dname].place(tileno,'XXX',op)
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
            nodes[dname].place(tileno,'XXX',op)
            return (tileno,r)

def is_placed(dname):
    return (nodes[dname].tileno != -1)

def is_routed(sname,dname):
    return (dname in nodes[sname].net)


def test_connect():

    print '######################################################'
    print '# serpent.py: Read cgra info'
    cgra_info.read_cgra_info()


    print '######################################################'
    print '# serpent.py: Initialize node and tile data structures'
    init_tile_resources(DBG=0)
    build_nodes(DBG=0)
    initialize_routes()
    initialize_node_INPUT()

    print 'TEST: who can reach pe_out_res?'
    rlist = cgra_info.reachable('pe_out_res', 0, DBG=1)
    print rlist


    print 'TEST: who can reach to_cgra(pe_out)?'
    rlist = cgra_info.reachable(to_cgra('pe_out'), 0)
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
    test_reachable()

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
#             (Ta,da,sa,ta) = parsewire(a)
#             (Tb,db,sb,tb) = parsewire(b)
#             return not (sa == sb)
# 
#         # b is one of ['mem_in','op1','op2'] (mem_in == wdata maybe)
#         # who can connect to mem_in (wdata)? anything on side 2
# 
# 
# 
# 
#         (Ta,da,sa,ta) = parsewire(a)
#         (Tb,db,sb,tb) = parsewire(b)
#         assert Ta == Tb
# 

        
