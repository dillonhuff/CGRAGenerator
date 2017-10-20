#!/usr/bin/python

import sys;
import re;

# This should be in decode library I guess
# and/or why not a single line
# (reg,feature,tile,data) = myparse(line, "(..)(..)(....) (........)", 4)
def parse_bs_line(line):
    parse = re.search("(..)(..)(....) (........)", line)
    if parse:
        reg = parse.group(1) 
        feature = parse.group(2)
        tile    = parse.group(3)
        data    = parse.group(4)
        # tileno = int(tile,16)
        return (reg,feature,tile,data)
    else:
        print "ERROR bad bitstream line:\n%s" % line; sys.exit(-1)


def fix_cba(line, DBG=0):
    '''Connection box 'a' input'''

    # Feature == "02" => op_a_in
    # OLD (v0):
    # xx02xxxx 0000 000[01234] # a <= in_s1t[01234]
    # xx02xxxx 0000 000[56789] # a <= in_s3t[01234]
    # 
    # NEW (v1):
    # xx02xxxx 0000 000[56789] # a <= out_s2t[01234]
    # xx05xxxx 1550 0000
    # 
    # xx05xxxx 0010 0000       #      out_s2t0 <= in_s1t0 [21:20]==1
    # xx05xxxx 0040 0000       #      out_s2t1 <= in_s1t1 [23:22]==1
    # xx05xxxx 0100 0000       #      out_s2t2 <= in_s1t2 [25:24]==1
    # xx05xxxx 0400 0000       #      out_s2t3 <= in_s1t3 [27:26]==1
    # xx05xxxx 1000 0000       #      out_s2t4 <= in_s1t4 [29:28]==1

    # xx05xxxx 0020 0000       #      out_s2t0 <= in_s3t0 [21:20]==2
    # xx05xxxx 0080 0000       #      out_s2t1 <= in_s3t1 [23:22]==2
    # xx05xxxx 0200 0000       #      out_s2t2 <= in_s3t2 [25:24]==2
    # xx05xxxx 0800 0000       #      out_s2t3 <= in_s3t3 [27:26]==2
    # xx05xxxx 2000 0000       #      out_s2t4 <= in_s3t4 [29:28]==2

    (reg,feature,tile,data) = parse_bs_line(line)
    sel = int(data, 16)  # O.k. to use all 32 bits
    track = sel%5

    # v0: 'a' originally came from inwire on side 1 or 3 as indicated by sel bits
    if sel < 5: in_side = 1
    else:       in_side = 3

    # v1 step 1: change cb so 'a' input comes from out_s2
    cbnew = "%s%s%s 0000000%d" % (reg,feature,tile, track+5)

    # v1 step 2: tell sb to connect orig inwire to out_s2t<track> instead of 'a'
    out_side = 2
    (sel,shiftamt,sbstring) = sbconnect(in_side, out_side, track)
    sbnew = "%s%s%s %08x" % (reg,"05",tile, sel<<shiftamt)

    inwire  = "a <= in_s%dt%d"  % (in_side,  track)
    outwire = "a <= out_s%dt%d" % (out_side, track)
    return(cbnew, inwire, outwire, sbnew, sbstring)

def fix_cbb(line, DBG=0):
    '''Connection box 'b' input'''

    # OLD:
    # xx03xxxx 0000 000[01234] # b <= in_s0t[01234]
    # xx03xxxx 0000 000[56789] # b <= in_s2t[01234]
    # 
    # NEW:
    # xx03xxxx 0000 000[56789] # b <= out_s1t[01234]
    # xx05xxxx 0000 0000
    # 
    # xx05xxxx 0000 0000       #      out_s1t0 <= in_s0t0 [11:10]==0
    # xx05xxxx 0000 0000       #      out_s1t1 <= in_s0t1 [13:12]==0
    # xx05xxxx 0000 0000       #      out_s1t2 <= in_s0t2 [15:14]==0
    # xx05xxxx 0000 0000       #      out_s1t3 <= in_s0t3 [17:16]==0
    # xx05xxxx 0000 0000       #      out_s1t4 <= in_s0t4 [19:18]==0

    # xx05xxxx 0000 0400       #      out_s1t0 <= in_s2t0 [11:10]==1
    # xx05xxxx 0000 1000       #      out_s1t1 <= in_s2t1 [13:12]==1
    # xx05xxxx 0000 4000       #      out_s1t2 <= in_s2t2 [15:14]==1
    # xx05xxxx 0001 0000       #      out_s1t3 <= in_s2t3 [17:16]==1
    # xx05xxxx 0004 0000       #      out_s1t4 <= in_s2t4 [19:18]==1
        
    (reg,feature,tile,data) = parse_bs_line(line)
    sel = int(data, 16)  # O.k. to use all 32 bits
    track = sel%5

    # v0: 'b' originally came from inwire on side 0 or 2 as indicated by sel bits
    if sel < 5: in_side = 0
    else:       in_side = 2

    # v1 step 1: change cb so 'b' input comes from out_s1
    cbnew = "%s%s%s 0000000%d" % (reg,feature,tile, track+5)

    # v1 step 2: tell sb to connect orig inwire to out_s1t<track> instead of 'b'
    out_side = 1
    (sel,shiftamt,sbstring) = sbconnect(in_side, out_side, track)
    sbnew = "%s%s%s %08x" % (reg,"05",tile, sel<<shiftamt)

    inwire  = "b <= in_s%dt%d"  % (in_side,  track)
    outwire = "b <= out_s%dt%d" % (out_side, track)
    return(cbnew, inwire, outwire, sbnew, sbstring)

def print_cb_rewrite(cbold, cbnew, inwire, outwire, sbnew, sbstring):
    # What we did.
    print "# BEFORE: %s # %s"      % (cbold, inwire)
    print "# AFTER:  %s # %s"      % (cbnew, outwire)
    print "#         %s #      %s" % (sbnew, sbstring)
    print ""

def sbconnect(in_side, out_side, track):
    '''
    Build a switchbox that connects in_s<in_side>t<track> to out_s<out_side>t<track>
    '''

    # (input b)
    # For now only needs to work for output sides 1 and 2
    if out_side == 1:
        shiftamt = 10 + 2*track # output to side 1 (out_s1)
        # For now only needs to work for input sides 0 and 2
        if in_side == 0: sel = 0
        if in_side == 2: sel = 1


    # (input a)
    # For now only needs to work for output sides 1 and 2
    if out_side == 2:
        shiftamt = 20 + 2*track # output to side 2 (out_s2)
        # For now only needs to work for input sides 1 and 3
        if in_side == 1: sel = 1
        if in_side == 3: sel = 2


    # For debug purposes, make a text string e.g.
    # "out_s2t3 <= in_s2t3 ([17:16]=1)"
    #
    connection = "out_s%dt%d <= in_s%dt%d ([%d:%d]=%d)" \
                 % (out_side, track, in_side, track, shiftamt+1, shiftamt, sel)

    return (sel, shiftamt, connection)

def fix_cb(line, DBG=0):
    (reg,feature,tile,data) = parse_bs_line(line)

    # Only interested in a, b connection boxes
    # (Elsewhere, should have checked to make sure this is PE and not mem tile)
    if feature != "02" and feature != "03": return False

    if feature == "02":
        (cbnew, inwire, outwire, sbnew, sbstring) = fix_cba(line,DBG)

    if feature == "03":
        (cbnew, inwire, outwire, sbnew, sbstring) = fix_cbb(line,DBG)

    print_cb_rewrite(line, cbnew, inwire, outwire, sbnew, sbstring)


# NOTE MUST ADD 0005<TTTT> to a watchlist now!!!
# Keep a list of all switchboxes used;
# keep a list of all switchboxes modified;
# make sure the two lists have NO COMMON TILES.


def test_cbfix():
    fix_cb("xx020007 00000000", DBG=1)
    fix_cb("xx020007 00000001", DBG=1)
    fix_cb("xx020007 00000002", DBG=1)
    fix_cb("xx020007 00000003", DBG=1)
    fix_cb("xx020007 00000004", DBG=1)
    fix_cb("xx020007 00000005", DBG=1)
    fix_cb("xx020007 00000006", DBG=1)
    fix_cb("xx020007 00000007", DBG=1)
    fix_cb("xx020007 00000008", DBG=1)
    fix_cb("xx020007 00000009", DBG=1)

    print "##########################################################################"

    fix_cb("xx030007 00000000", DBG=1)
    fix_cb("xx030007 00000001", DBG=1)
    fix_cb("xx030007 00000002", DBG=1)
    fix_cb("xx030007 00000003", DBG=1)
    fix_cb("xx030007 00000004", DBG=1)
    fix_cb("xx030007 00000005", DBG=1)
    fix_cb("xx030007 00000006", DBG=1)
    fix_cb("xx030007 00000007", DBG=1)
    fix_cb("xx030007 00000008", DBG=1)
    fix_cb("xx030007 00000009", DBG=1)

test_cbfix()


# OLD:
# xx03xxxx 0000 000[01234] # b <= in_s0t[01234]
# 
# NEW:
# xx03xxxx 0000 000[56789] # b <= out_s1t[01234]
# xx05xxxx 0000 0000
# 
# xx05xxxx 0000 0000       #      out_s1t0 <= in_s0t0 [11:10]==0
# xx05xxxx 0000 0000       #      out_s1t1 <= in_s0t1 [13:12]==0
# xx05xxxx 0000 0000       #      out_s1t2 <= in_s0t2 [15:14]==0
# xx05xxxx 0000 0000       #      out_s1t3 <= in_s0t3 [17:16]==0
# xx05xxxx 0000 0000       #      out_s1t4 <= in_s0t4 [19:18]==0
# 
# 
# 
# 
# OLD:
# xx03xxxx 000000[56789] # b <= in_s3t[01234]
# 
# NEW:
# xx03xxxx 0000 000[56789] # b <= out_s1t[01234]
# xx05xxxx 000A A800       #
# 
# xx05xxxx 0000 0800       #      out_s1t0 <= in_s3t0 [11:10]==2
# xx05xxxx 0000 2000       #      out_s1t1 <= in_s3t1 [13:12]==2
# xx05xxxx 0000 8000       #      out_s1t2 <= in_s3t2 [15:14]==2
# xx05xxxx 0002 0000       #      out_s1t3 <= in_s3t3 [17:16]==2
# xx05xxxx 0008 0000       #      out_s1t4 <= in_s3t4 [19:18]==2
# 
# 
# 
# 
# 
# 
# 
# 0 21:20 = 1
# 1 23:22 = 1
# 2 25:24 = 1
# 3 27:26 = 1
# 4 29:28 = 1
# 
# 
# 
# a <= in_s3t[01234]
# 
# 
# xx05xxxx 0010 0000 # a <= out_s2t0 [7:0]; out_s2t0 <= in_s1t0 [21:20]
# xx05xxxx 0040 0000 # a <= out_s2t1; out_s2t1 <= in_s1t1 [23:22]
# xx05xxxx 0100 0000 # a <= out_s2t2; out_s2t2 <= in_s1t2 [25:24]
# xx05xxxx 0400 0000 # a <= out_s2t3; out_s2t3 <= in_s1t3 [27:26]
# xx05xxxx 1000 0000 # a <= out_s2t4; out_s2t4 <= in_s1t4 [29:28]
# 
# 
# 
# 
# 



##############################################################################
##############################################################################
##############################################################################
# OLD:
# xx02xxxx 0000 000[56789] # a <= in_s3t[01234]
# 
# NEW:
# xx02xxxx 0000 000[56789] # a <= out_s2t[01234]
# xx05xxxx 2660 0000
# 
# 
# xx05xxxx 0020 0000       #      out_s2t0 <= in_s3t0 [21:20]==2
# xx05xxxx 0080 0000       #      out_s2t1 <= in_s3t1 [23:22]==2
# xx05xxxx 0200 0000       #      out_s2t2 <= in_s3t2 [25:24]==2
# xx05xxxx 0800 0000       #      out_s2t3 <= in_s3t3 [27:26]==2
# xx05xxxx 2000 0000       #      out_s2t4 <= in_s3t4 [29:28]==2
# 
# 
