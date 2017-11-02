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

DO_TEST=1
def do_test():
    if not DO_TEST: return
    cgra_info.read_cgra_info()

    test_ctsr()
    test_ctsc()
    test_all()

def test_all():
    track = 0

    print "########################################"
    print "# End turn takes us down a mem column"
    connect_tiles(src=0,dst=17,track=0,dir='hv',DBG=1)
    print ""

    print "########################################"
    print "# Same thing except vh instead of hv"
    # BOOKMARK



    print "########################################"
    print "# End turn takes us further down a mem column"
    connect_tiles(src=0,dst=39,track=0,dir='hv',DBG=1)
    print ""

    print "########################################"
    print "# A long path straight down column zero"
    connect_tiles(src=0,dst=36,track=0,dir='hv',DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_row(0, 1, track, DBG=1); print ""
    (begin,path,end) = connect_tiles_same_col(0, 8, track, DBG=1); print ""
    (begin,path,end) =          connect_tiles(0,10, track, DBG=1); print ""

    # What happens if tile is straight across from bottom half of mem tile?
    (begin,path,end) =          connect_tiles(8,10, track, DBG=1); print ""




def verify(begin,path,end, result_list, rnum=0, test='ctsr'):
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

    (begin,path,end) = connect_tiles_same_row( 0, 1, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    (begin,path,end) = connect_tiles_same_row( 0, 2, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    (begin,path,end) = connect_tiles_same_row( 2, 0, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    (begin,path,end) = connect_tiles_same_row( 0, 5, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    (begin,path,end) = connect_tiles_same_row( 5, 0, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    print "# Connect to top half of a memory tile"
    (begin,path,end) = connect_tiles_same_row( 0, 3, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    print "# Connect to bottom half of a memory tile"
    (begin,path,end) = connect_tiles_same_row( 8, 3, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    print "# This one crosses bottom half of a memory tile"
    (begin,path,end) = connect_tiles_same_row( 8, 13, track, DBG=1)
    verify(begin,path,end, results,resno,testname); resno = resno+1


def test_ctsc():
    track = 0

    print "########################################"
    print "# Begin ctsc testing"
    print ""

    results = range(100)
    nresults = len(results)

    testname = 'ctsc'; resno = 0
    (begin,path,end) = connect_tiles_same_col(0, 8, track, DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1


    (begin,path,end) = connect_tiles_same_col(0,14, track, DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1


    (begin,path,end) = connect_tiles_same_col(14,0, track, DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1


    (begin,path,end) = connect_tiles_same_col(0,36, track, DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1


    (begin,path,end) = connect_tiles_same_col(36,0, track, DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    print "# What happens if we try to make a path through mem column?"
    (begin,path,end) = connect_tiles_same_col(3,45,track,DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    print "# What happens if we try to make a path UP through mem column?"
    (begin,path,end) = connect_tiles_same_col(45,3,track,DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1

    print "# Connect adjacent NS mem tiles"
    (begin,path,end) = connect_tiles_same_col(3, 17, track, DBG=1)
    # verify(begin,path,end)
    verify(begin,path,end, results,resno,testname); resno = resno+1

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
    (cornerconn,hpath,vpath) = ([],[],[])
    
    if rsrc==rdst:
        if DBG: print "# Both tiles are in same row\n# "
        (begin,hpath,end) = connect_tiles_same_row(src,dst,track,DBG=DBG-1)
        if DBG: prettyprint_path(dir, begin, hpath, cornerconn, vpath, end)
        return (begin,hpath,end)

    elif csrc==cdst:
        if DBG: print "# Both tiles are in same column\n# "
        (begin,vpath,end) = connect_tiles_same_col(src,dst,track,DBG=DBG-1)
        if DBG: prettyprint_path(dir, begin, hpath, cornerconn, vpath, end)
        return (begin,vpath,end)

    if dir=='hv':
        # Fist go horizontal (EW), then vertical (NS)
    
        # Find the corner tile: same row as src, same col as dst
        (rcorn,ccorn) = (rsrc,cdst)
        corn = cgra_info.rc2tileno(rcorn,ccorn)
        if DBG: print "# Found corner tile %d (r%d,c%d)"\
           % (corn, rcorn, ccorn)

        # horizontal path from src to corn
        if DBG>1: print "# hpath:",
        (hbegin,hpath,hend) = connect_tiles_same_row(src,corn,track,DBG=DBG-1)
        if DBG>1: print "# "

        # vert path from corn to dest
        if DBG>1: print "# vpath:",
        (vbegin,vpath,vend) = connect_tiles_same_col(corn,dst,track,DBG=DBG-1)
        if DBG>1: print "# "

        # In corner tile, connect hend to vbegin
        cornerconn = ["%s -> %s" % (hend,vbegin)]
        if DBG>1: print "# corner:", cornerconn
        if DBG: print "# "

        # If corner tile is mem, it needs an extra connection

        final_path = hpath + cornerconn + vpath
        if DBG: prettyprint_path(dir, hbegin, hpath, cornerconn, vpath, vend)
        return (hbegin, final_path, vend)

    # TODO WERE IS VH?? FIXME
    assert False, 'should not be here!!!'
    return (1,2,3)


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
    return (beginwire, path, endwire)


def connect_tiles_same_col(src,dst,track,DBG=0):

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
    return (beginwire, path, endwire)


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

if (DO_TEST): do_test()
