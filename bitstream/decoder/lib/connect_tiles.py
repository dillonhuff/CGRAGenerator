#!/usr/bin/python

import sys;
import re;

# # from ../decoder/lib import cgra_info
# sys.path.append("../decoder")
# from lib import cgra_info

# Should be in same dir as this one, yes?
import cgra_info



# def main():
#     print '''
# Plan: move this to the library I guess.
#     '''
#     test_ctsr()
#     test_ctsc()

def test_ctsr():
#     cgra_filename = get_default_cgra_info_filename()
#     cgra_info.read_cgra_info(cgra_filename)

    track = 0

    (begin,path,end) = connect_tiles_same_row(0,1,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_row(0,2,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_row(2,0,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_row(0,5,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_row(5,0,track,DBG=1)
    print ""

    # This one crosses a memory tile in a funny way
    (begin,path,end) = connect_tiles_same_row(8,13,track,DBG=1)
    print ""

def test_ctsc():
#     cgra_filename = get_default_cgra_info_filename()
#     cgra_info.read_cgra_info(cgra_filename)

    track = 0

    (begin,path,end) = connect_tiles_same_col(0,8,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_col(0,14,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_col(14,0,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_col(0,36,track,DBG=1)
    print ""

    (begin,path,end) = connect_tiles_same_col(36,0,track,DBG=1)
    print ""

    # What happens if we try to make a path through mem column?
    (begin,path,end) = connect_tiles_same_col(3,45,track,DBG=1)
    print ""


def connect_tiles_same_row(src,dst,track,DBG=0):

    (rsrc,csrc) = cgra_info.tileno2rc(src)
    (rdst,cdst) = cgra_info.tileno2rc(dst)
    if DBG: print "# Connect tile %d (r%d,c%d) to tile %d (r%d,c%d)" %\
       (src,rsrc,csrc,dst,rdst,cdst)
    # print rdst,cdst

    # tiles must be on same row; must be two different tiles
    assert src != dst; assert rsrc == rdst
    
    if cdst>csrc: (inside,outside) = (2,0)
    else:         (inside,outside) = (0,2)

    beginwire = build_wire_rc(rsrc,csrc,'out',outside,track)
    # print "beginwire=", beginwire
    
    path = []
    if abs(csrc-cdst)==1:
        # No need for a path; just show connection to neighbring tile
        endwire = build_wire_rc(rdst,cdst,'in',inside,track)
        # print "endwire=", endwire
        if DBG: printpath(beginwire, path, endwire)
        return (beginwire, path, endwire)

    if (cdst>csrc): cols = range(csrc+1,cdst)
    else:           cols = range(csrc-1,cdst,-1)

    # print cols
    for c in cols:
        inwire  = build_wire_rc(rsrc,c,'in' ,inside, track)
        outwire = build_wire_rc(rsrc,c,'out',outside,track)
        connection = "%11s -> %12s" % (inwire, outwire)
        # print "#   ", connection
        path.append(connection)

    endwire = build_wire_rc(rdst,cdst,'in',inside,track)
    # print path
    # print "endwire=", endwire
    if DBG: printpath(beginwire, path, endwire)
    return (beginwire, path, endwire)

def connect_tiles_same_col(src,dst,track,DBG=0):

    (rsrc,csrc) = cgra_info.tileno2rc(src)
    (rdst,cdst) = cgra_info.tileno2rc(dst)
    if DBG: print "# Connect tile %d (r%d,c%d) to tile %d (r%d,c%d)" %\
       (src,rsrc,csrc,dst,rdst,cdst)

    # tiles must be on same col; must be two different tiles
    assert src != dst; assert csrc == cdst
    
    if rdst>rsrc: (inside,outside) = (3,1)
    else:         (inside,outside) = (1,3)

    beginwire = build_wire_rc(rsrc,csrc,'out',outside,track)
    # print "beginwire=", beginwire
    
    path = []

    # Could be get_beginwire(rdst,cdst,s=rsrc,d=rdst,side=inside) (vs. (csrc,cdst))
    if abs(rsrc-rdst)==1:
        # No need for a path; just show connection to neighbring tile
        endwire = build_wire_rc(rdst,cdst,'in',inside,track)
        # print "endwire=", endwire
        if DBG: printpath(beginwire, path, endwire)
        return (beginwire, path, endwire)

    # Could be rows = get_tile_range(src=rsrc,dst=rdst) (vs. (csrc,cdst))
    if (rdst>rsrc): rows = range(rsrc+1,rdst)
    else:           rows = range(rsrc-1,rdst,-1)

    # print cols
    for r in rows:

        # Need mem offset (mo) on EW sides if row is odd and tile is mem
        # mo=s02_mem_offset(rsrc,c)

        inwire  = build_wire_rc(r,csrc,'in' ,inside, track)
        outwire = build_wire_rc(r,csrc,'out',outside,track)
        connection = "%11s -> %12s" % (inwire, outwire)
        # print "#   ", connection
        path.append(connection)

    # BOOKMARK
    endwire = build_wire_rc(rdst,cdst,'in',inside,track)
    # print path
    # print "endwire=", endwire
    if DBG: printpath(beginwire, path, endwire)
    return (beginwire, path, endwire)




def build_wire_rc(r,c,inout,side,track):
    tileno = cgra_info.rc2tileno(r,c)

    # Need mem offset (mo) on EW sides if row is odd and tile is mem
    # mo = 0
    # if side==0 or side==2:
    mo = mem_offset(r,c,side)
    # print "# mo=", mo
    return "T%d_%s_s%dt%d" % (tileno, inout, side+mo, track)

def mem_offset(r,c,side):
    DBG=0

    # Never need offset for side 3
    if side==3: return 0

    # Only need offset on mem tiles
    tileno   = cgra_info.rc2tileno(r,c)
    tiletype = cgra_info.tiletype(tileno)
    if DBG: print "Tile %d has type '%s'" % (tileno,tiletype)
    if not re.search("^mem", tiletype): return 0

    # Mem sides (0,2) need offset 4 if row is odd
    if r%2==1 and side%2==0: return 4

    # Mem side 1 needs offset 4 always 
    elif side==1: return 4
    else:         return 0

# def rctype(r,c):
#     tileno   = cgra_info.rc2tileno(r,c)
#     tiletype = cgra_info.tiletype(tileno)
#     if   re.search("^pe",  tiletype): tiletype = "pe"
#     elif re.search("^mem", tiletype): tiletype = "mem"
#     print "Tile %d has type '%s'" % (tileno,tiletype)

    

    
def printpath(begin,path,end):
    if path == []:
        print "# %s -> %s" % (begin,end)

    else:
        # print "#               %s ->" % begin
        # print "# ............. %s ->" % begin
        print "# -------------> %12s ->" % begin
        # print "path=", path
        for p in path:
            print "# %s ->" % p
        print "# %11s" % (end)

    return


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
# 
# main()
# 
