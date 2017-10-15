#!/usr/bin/python

import sys;
import re;

def fix_cb(line, DBG=0):
    parse = re.search("(..)(..)(....) (........)", line)
    if parse:
        reg = parse.group(1) 
        feature = parse.group(2)
        tile    = parse.group(3)
        data    = parse.group(4)
        # tileno = int(tile,16)
    else:
        print "ERROR bad line:\n%s" % line; sys.exit(-1)

    # Only interested in a, b connection boxes
    # (Elsewhere, should have checked to make sure this is PE and not mem tile)
    if feature != "02" and feature != "03": return False

    # OLD:
    # xx02xxxx 0000 000[01234] # a <= in_s1t[01234]
    # xx02xxxx 0000 000[56789] # a <= in_s3t[01234]
    # 
    # NEW:
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

    # DBG=1
    parse = re.search("0000000([0-9])", data)
    sel = int(parse.group(1))
    if feature == "02":
        if sel < 5:
            inside = 1; track = sel%5; sbsel=1; sel2=(track+5)
        else:
            inside = 3; track = sel%5; sbsel=2; sel2=(track+5)

        line_out0 = "%s%s%s 0000000%d" % (reg,feature,tile,sel2)

        shiftamt = 20 + 2*track
        sbdata = sbsel << shiftamt
        sbline = "%s%s%s %08x" % (reg,feature,tile,sbdata)
        if DBG:
            print "# BEFORE: %s # a <= in_s%dt%d" % (line,inside,track)
            print "# AFTER:  %s # a <= out_s2t%d" % (line_out0,track)
            print "#         %s #      out_s2t%d <= in_s%dt%d ([%d:%d]=%d)" \
                  % (sbline,track,inside,track,shiftamt+1,shiftamt,sbsel)
            # print "# op_a_in <= out_s2t[01234]"
            print ""

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
        
    if feature == "03":
        if sel < 5:
            inside = 0; track = sel%5; sbsel=0; sel2=(track+5)
        else:
            inside = 2; track = sel%5; sbsel=1; sel2=(track+5)

        line_out0 = "%s%s%s 0000000%d" % (reg,feature,tile,sel2)

        shiftamt = 10 + 2*track
        sbdata = sbsel << shiftamt
        sbline = "%s%s%s %08x" % (reg,feature,tile,sbdata)
        if DBG:
            print "# BEFORE: %s # a <= in_s%dt%d" % (line,inside,track)
            print "# AFTER:  %s # a <= out_s2t%d" % (line_out0,track)
            print "#         %s #      out_s2t%d <= in_s%dt%d ([%d:%d]=%d)" \
                  % (sbline,track,inside,track,shiftamt+1,shiftamt,sbsel)
            # print "# op_a_in <= out_s2t[01234]"
            print ""
        

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
