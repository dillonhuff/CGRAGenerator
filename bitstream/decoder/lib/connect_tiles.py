#!/usr/bin/python

import sys;
import re;

# # from ../decoder/lib import cgra_info
# sys.path.append("../decoder")
# from lib import cgra_info

# Should be in same dir as this one, yes?
import cgra_info

# INDEX
# FIXME/TODO build a index

DO_TEST=0
def do_test():
    if not DO_TEST: return
    cgra_info.read_cgra_info()

    test_ctsr()
    test_ctsc()
    test_all()

def test_all():
    track = 0

    print "########################################"
    print "# Begin any-to-any testing"
    print ""

    results = range(100)
    nresults = len(results)

    testname = 'anypath'; resno = 0

    # anypath 0
    print "########################################"
    print "# End turn takes us down a mem column"
    p = connect_tiles(src=0,dst=17,track=0,dir='hv',DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    # assert False

    print "########################################"
    print "# Same thing except vh instead of hv"
    p = connect_tiles(src=0,dst=17,track=0,dir='vh',DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    # TODO/FIXME more vh tests maybe

    print "########################################"
    print "# End turn takes us further down a mem column"
    p = connect_tiles(src=0,dst=39,track=0,dir='hv',DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "########################################"
    print "# A long path straight down column zero"
    p = connect_tiles(src=0,dst=36,track=0,dir='hv',DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    # anypath 4
    p = connect_tiles_same_row(0, 1, track, DBG=1);
    verify(p, results,resno,testname); resno = resno+1

    # anypath 5
    p = connect_tiles_same_col(0, 8, track, DBG=1);
    verify(p, results,resno,testname); resno = resno+1

    p =          connect_tiles(0,10, track, DBG=1);
    verify(p, results,resno,testname); resno = resno+1

    # What happens if tile is straight across from bottom half of mem tile?
    p  =          connect_tiles(8,10, track, DBG=1);
    verify(p, results,resno,testname); resno = resno+1


def verify(path, result_list, rnum=0, test='ctsr'):
    (begin,path,end) = (path[0],path[1:-1],path[-1])

    # Set result_list to e.g. range(100) if not doing compares.
    DO_COMPARE = (result_list[0] != 0)

    print '# '
    print "# Check %s %d" % (test, rnum),
    print (begin,path,end)
    if DO_COMPARE:
        assert (begin,path,end) == result_list[rnum], 'path looks wrong'
        print "# Result checks out!\n"
    else:
        print "# (Use above result for verification.)\n"

def test_ctsr():
    track = 0

    print "########################################"
    print "# Begin ctsr testing"
    print ""

    results = [
        ('T0_out_s0t0', [], 'T1_in_s2t0'),
        ('T0_out_s0t0', ['T1_in_s2t0 -> T1_out_s0t0'], 'T2_in_s2t0'),
        ('T2_out_s2t0', ['T1_in_s0t0 -> T1_out_s2t0'], 'T0_in_s0t0'),
        ('T0_out_s0t0', ['T1_in_s2t0 -> T1_out_s0t0', 'T2_in_s2t0 -> T2_out_s0t0', 'T3_in_s2t0 -> T3_out_s0t0', 'T4_in_s2t0 -> T4_out_s0t0'], 'T5_in_s2t0'),
        ('T5_out_s2t0', ['T4_in_s0t0 -> T4_out_s2t0', 'T3_in_s0t0 -> T3_out_s2t0', 'T2_in_s0t0 -> T2_out_s2t0', 'T1_in_s0t0 -> T1_out_s2t0'], 'T0_in_s0t0'),
        ('T0_out_s0t0', ['T1_in_s2t0 -> T1_out_s0t0', 'T2_in_s2t0 -> T2_out_s0t0'], 'T3_in_s2t0'),
        ('T8_out_s0t0', ['T9_in_s2t0 -> T9_out_s0t0', 'T10_in_s2t0 -> T10_out_s0t0'], 'T3_in_s6t0'),
        ('T8_out_s0t0', ['T9_in_s2t0 -> T9_out_s0t0', 'T10_in_s2t0 -> T10_out_s0t0', 'T3_in_s6t0 -> T3_out_s4t0', 'T11_in_s2t0 -> T11_out_s0t0', 'T12_in_s2t0 -> T12_out_s0t0'], 'T13_in_s2t0')
        ]

    testname = 'ctsr'; resno = 0

    p = connect_tiles_same_row( 0, 1, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_row( 0, 2, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_row( 2, 0, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_row( 0, 5, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_row( 5, 0, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "# Connect to top half of a memory tile"
    p = connect_tiles_same_row( 0, 3, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "# Connect to bottom half of a memory tile"
    p = connect_tiles_same_row( 8, 3, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "# This one crosses bottom half of a memory tile"
    p = connect_tiles_same_row( 8, 13, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1


def test_ctsc():
    track = 0

    print "########################################"
    print "# Begin ctsc testing"
    print ""

    results = range(100)
    nresults = len(results)

    testname = 'ctsc'; resno = 0
    p = connect_tiles_same_col(0, 8, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_col(0,14, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_col(14,0, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_col(0,36, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    p = connect_tiles_same_col(36,0, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "# What happens if we try to make a path through mem column?"
    p = connect_tiles_same_col(3,45,track,DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "# What happens if we try to make a path UP through mem column?"
    p = connect_tiles_same_col(45,3,track,DBG=1)
    verify(p, results,resno,testname); resno = resno+1

    print "# Connect adjacent NS mem tiles"
    p = connect_tiles_same_col(3, 17, track, DBG=1)
    verify(p, results,resno,testname); resno = resno+1

def connect_tiles(src=0,dst=17,track=0,dir='hv',DBG=0):
    '''tile17 should be row 2, col 3 maybe'''
    (rsrc,csrc) = cgra_info.tileno2rc(src)
    (rdst,cdst) = cgra_info.tileno2rc(dst)

    if DBG:
        print "# Connect tile %d (r%d,c%d)" % (src,rsrc,csrc),
        print "to tile %d (r%d,c%d)" % (dst,rdst,cdst),
        print "on %s path" % dir
        if is_mem_rc(rdst,cdst):
            print "# Destination is a memory tile"

    # No need for a corner if sr, dst are in same row or col
    (cornerconn,path1,path2) = ([],[],[])
    
    if rsrc==rdst:
        if DBG: print "# Both tiles are in same row\n# "
        p = connect_tiles_same_row(src,dst,track,DBG=DBG-1)
        (begin,path1,end) = unpack_path(p)
        if DBG: prettyprint_path(dir, begin, path1, cornerconn, path2, end)
        return pack_path(begin,path1,end)

    elif csrc==cdst:
        if DBG: print "# Both tiles are in same column\n# "
        p = connect_tiles_same_col(src,dst,track,DBG=DBG-1)
        (begin,path2,end) = unpack_path(p)
        if DBG: prettyprint_path(dir, begin, path1, cornerconn, path2, end)
        return pack_path(begin,path2,end)

    elif dir=='hv':
        # First go horizontal (EW), then vertical (NS)
        # Find corner tile: same row as src, same col as dst
        (rcorn,ccorn) = (rsrc,cdst)
        p = connect_through_corner(src,dst,rcorn,ccorn,track,dir,DBG)
        return p

    elif dir=='vh':
        # First go vertical (NS), then horizontal (EW)
        # Find corner tile: same row as dst, same col as src
        (rcorn,ccorn) = (rdst,csrc)
        p = connect_through_corner(src,dst,rcorn,ccorn,track,dir,DBG)
        return p

    assert False, 'unknown case in connect_tiles()'
    return [-1,-1,-1]

def unpack_path(p):
    (begin,path,end) = (p[0],p[1:-1],p[-1])
    return (begin,path,end)

def pack_path(begin,path,end):
    p = [begin]+path+[end]
    return p

def connect_through_corner(src,dst,rcorn,ccorn,track=0,dir='hv',DBG=0):

        corn = cgra_info.rc2tileno(rcorn,ccorn)
        if DBG: print "# Found corner tile %d (r%d,c%d)"\
           % (corn, rcorn, ccorn)

        # horizontal path from src to corn
        if DBG>1: print "# path1:",
        p = connect_tiles(src,corn,track,DBG=0)
        (begin1,path1,end1) = unpack_path(p)
        if DBG>1: print "# "

        # vert path from corn to dest
        if DBG>1: print "# path2:",
        # (begin2,path2,end2) = connect_tiles(corn,dst,track,DBG=DBG-1)
        p = connect_tiles(corn,dst,track,DBG=0)
        (begin2,path2,end2) = unpack_path(p)
        if DBG>1: print "# "

        # In corner tile, connect end1 to begin2
        cornerconn = ["%s -> %s" % (end1,begin2)]
        if DBG>1: print "# corner:", cornerconn
        if DBG: print "# "

        final_path = path1 + cornerconn + path2
        if DBG: prettyprint_path(dir, begin1, path1, cornerconn, path2, end2)
        return pack_path(begin1, final_path, end2)

def prettyprint_path(dir, begin, path1, cornerconn, path2, end):
    if dir == 'hv': (p1,p2) = ('hpath','vpath')
    else:           (p1,p2) = ('vpath','hpath')

    print "# Begin: %s" % [begin]
    if path1: print "# %s  %s" % (p1,path1)
    if cornerconn:  print "# corner %s" % cornerconn
    if path2: print "# %s  %s" % (p2,path2)
    if True:  print "# End:   %s" % [end]
    print "# "

    final_path = path1 + cornerconn + path2
    print "# Complete path: %s%s%s" % ([begin], final_path,[end])


def connect_tiles_same_row(src=0,dst=5,track=0,DBG=0):
    if DBG<0: DBG=0 # ugh

    (rsrc,csrc) = cgra_info.tileno2rc(src)
    (rdst,cdst) = cgra_info.tileno2rc(dst)

    # If mem tile is 2 rows high, can match rsrc to either rdst or rdst+1
    if rsrc == (rdst+1) and is_mem_rc(rdst,cdst):
        # Source row matches bottom half of mem tile
        rdst = rdst+1

    if DBG: print "# Connect tile %d (r%d,c%d) to tile %d (r%d,c%d)" %\
       (src,rsrc,csrc, dst,rdst,cdst)

    # tiles must be on same row; must be two different tiles
    assert rsrc == rdst; assert src != dst
    
    if cdst>csrc: (inside,outside) = (2,0) # left-to-right
    else:         (inside,outside) = (0,2) # right-to-left

    beginwire = build_wire_rc(rsrc,csrc,'out',outside,track)
    
    path = []

    if (cdst>=csrc): cols = range(csrc+1,cdst, 1) # left-to-right
    else:            cols = range(csrc-1,cdst,-1) # right-to-left
    # print cols

    for c in cols:
        # Note build_wire will apply mem offset on NS sides
        # depending on top/bottom half vs. up/down dir of flow

        inwire  = build_wire_rc(rsrc,c,'in' ,inside, track)
        outwire = build_wire_rc(rsrc,c,'out',outside,track)
        connection = "%s -> %s" % (inwire, outwire)
        path.append(connection)

    endwire = build_wire_rc(rdst,cdst,'in',inside,track)

    if DBG: printpath(beginwire, path, endwire)
    return pack_path(beginwire, path, endwire)


def connect_tiles_same_col(src,dst,track,DBG=0):
    if DBG<0: DBG=0 # ugh

    (rsrc,csrc) = cgra_info.tileno2rc(src)
    (rdst,cdst) = cgra_info.tileno2rc(dst)

    # Special case for mem tile DOWN => start in bottom half
    # FIXME may want to rethink this later...
    if is_mem_rc(rsrc,csrc) and (rdst>rsrc): # down
        # print "foo mem tile down"
        if (rsrc%2==0): rsrc = rsrc+1
        else          : rsrc = rsrc%2

    # Special case for mem tile UP => end in bottom half
    # FIXME may want to rethink this later...
    if is_mem_rc(rsrc,csrc) and (rdst<rsrc): # up
        # print "foo mem tile up"
        if (rdst%2==0): rdst = rdst + 1 # Stop when get to *bottom* of dest tile
        else          : rdst = dst%2

    if DBG: print "# Connect tile %d (r%d,c%d) to tile %d (r%d,c%d)" %\
       (src,rsrc,csrc,dst,rdst,cdst)

    # tiles must be on same col; must be two different tiles
    assert csrc == cdst; assert src != dst
    
    if rdst>rsrc: (inside,outside) = (3,1) # down
    else:         (inside,outside) = (1,3) # up

    beginwire = build_wire_rc(rsrc,csrc,'out',outside,track)

    path = []

    if (rdst>=rsrc): rows = range(rsrc+1,rdst)
    else:            rows = range(rsrc-1,rdst,-1)
    # print rows

    for r in rows:
        # Note build_wire will apply mem offset (mo) on EW sides if
        # row is odd and tile is mem mo=s02_mem_offset(rsrc,c)

        inwire  = build_wire_rc(r,csrc,'in' ,inside, track)
        outwire = build_wire_rc(r,csrc,'out',outside,track)
        connection = "%s -> %s" % (inwire, outwire)
        path.append(connection)

    endwire = build_wire_rc(rdst,cdst,'in',inside,track)

    if DBG: printpath(beginwire, path, endwire)
    return pack_path(beginwire, path, endwire)


def build_wire_rc(r,c,inout,side,track):
    tileno = cgra_info.rc2tileno(r,c)

    # Need mem offset if row==odd indicates mem tile bottom-half
    if is_mem_rc(r,c) and (r%2==1): mo=4
    else                          : mo=0

    return "T%d_%s_s%dt%d" % (tileno, inout, side+mo, track)

def is_mem_rc(r,c):
    tileno   = cgra_info.rc2tileno(r,c)
    tiletype = cgra_info.tiletype(tileno)

    # print "Tile %d has type '%s'" % (tileno,tiletype)

    # "return re.search()" DOES NOT WORK! (why?)
    if re.search("^mem", tiletype): return True
    else:                           return False


def allports(path):
    # Path looks like this:
    # ['T0_out_s0t0', 'T1_in_s2t0 -> T1_out_s0t0', 'T2_in_s2t0 -> T2_out_s0t0', 'T3_in_s2t0']
    # Want list of all the ports

    pstring = ' -> '.join(path)
    # "T0_out_s0t0 -> T1_in_s2t0 -> T1_out_s0t0 -> T2_in_s2t0 -> T2_out_s0t0 -> T3_in_s2t0"

    plist = pstring.split(' -> ')
    ['T0_out_s0t0', 'T1_in_s2t0', 'T1_out_s0t0', 'T2_in_s2t0', 'T2_out_s0t0', 'T3_in_s2t0']

    return plist

def printpath(begin,path,end):
    if path == []:
        print "# %s -> %s" % (begin,end)

    else:
        # print "#               %s ->" % begin
        # print "# ............. %s ->" % begin
        print "# -------------> %12s ->" % begin
        # print "path=", path
        for p in path:
            (i,o) = parse_connection(p)
            print "# %11s -> %12s ->" % (i,o)
        print "# %11s" % (end)

    return


def parse_connection(c):
    match = re.search('(\S+)\s*[-][>]\s*(\S+)', c)
    inwire = match.group(1)
    outwire = match.group(2)
    return (inwire,outwire)


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

# lifted from bsview.py
def find_neighbor(w, DBG=9):
    '''E.g. find_neighbor_wire("T4_in_s1t1") => ("T5_out_s3t1")'''

    # FIXME this can all be cleaned up...

    if (0):
        (tilefoo,wfoo) = (3, ("sb_wire_in1_s3t2", "out0_s1t2"))
        (tilefoo,wfoo) = (1, ("in_s2t4"))
        if (tileno == tilefoo) and (w in wfoo):
            DBG=1; print "\nWant match for tile %d wire '%s'" % (tileno,w)

    #     # find_neighbor_wire(4,"in_s1t1") => (5, "out_s3t1")

    # find_neighbor_wire("T4_in_s1t1") => ("T5_out_s3t1")
    # 
    # parse = re.search("(in|out)([01])*_s([0-9]+)t([0-9]+)", w)
    (tileno, dir, side, track) = parsewire(w)

    # Only works for 'out' wires (HA!)
    assert dir == 'out'

    in_or_out = dir

    # top_or_bottom = parse.group(2)  # 'None', '0' or '1'
    top_or_bottom = side/4 # '0' or '1'

    if (in_or_out=="out"): in_or_out="in"
    else:                  in_or_out="out"

    (r,c) = cgra_info.tileno2rc(tileno)

    # Adjust for wire in bottom of a memtile
    if (top_or_bottom == '1'): r = r + 1

    if   (side==0): (r,c,side) = (r,c+1,side+2)
    elif (side==1): (r,c,side) = (r+1,c,side+2)
    elif (side==2): (r,c,side) = (r,c-1,side-2)
    elif (side==3): (r,c,side) = (r-1,c,side-2)

    # Yes, yes, I know
    elif (side==4): (r,c,side) = (r,c+1,side+2)
    elif (side==5): (r,c,side) = (r+1,c,side+2)
    elif (side==6): (r,c,side) = (r,c-1,side-2)
    elif (side==7): (r,c,side) = (r-1,c,side-2)

    if (r < 0): return (False,False)
    if (c < 0): return (False,False)

    #   print (r,c,side)

    nbr_tileno = cgra_info.rc2tileno(r,c)
    # Note should return 'False' if (r,c) invalid
    if DBG: print "Found nbr tile number '%s'" % str(nbr_tileno)

    top_or_bottom = ''
    if (cgra_info.tiletype(nbr_tileno) == "memory_tile"):
        if DBG: print "HO found memory tile.  is it a top or a bottom :)"
        # '0' means top, '1' means bottom
        top_or_bottom = str(r % 2)
        if DBG:
            if (top_or_bottom): print " It's a bottom"
            else              : print " You're the top!"

    # adj_wire = "%s%s_s%dt%d" % (in_or_out, top_or_bottom, side, track)

    nbr_wire = "T%s_%s%s_s%dt%d" \
               % (nbr_tileno, in_or_out, top_or_bottom, side, track)

    # if DBG: print "%s on tile %d matches %s on tile %d\n" % (w, tileno, nbr_wire, nbr_tileno)
    if DBG: print "'%s' connects to neighbor '%s'\n" % (w, nbr_wire)

    return nbr_wire



if (DO_TEST): do_test()

# MAYBE STILL NEED THIS (or maybe not)
# def get_default_cgra_info_filename():
#     '''
#     Look for default cgra_info file in <decoder-directory>/examples/cgra_info.txt
#     '''
#     import os
#     mydir = os.path.dirname(os.path.realpath(__file__))
#     cgra_filename = mydir + "../decoder/examples/cgra_info.txt"
# 
#     VERBOSE=0
#     # global verbose #(implied because use before def)
#     if VERBOSE: print("I think I am here:\n  %s" % mydir)
#     if VERBOSE: print("Default cgra_info file is\n  %s" % cgra_filename)
#     return cgra_filename

