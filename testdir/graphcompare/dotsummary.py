#!/usr/bin/python
import sys
import re

# Sample input:
#     "T15_ADD"   -> "T8_ADD";   
#     "T10_MUL"   -> "T8_ADD";   
#   # "T1_ADD"    -> "T1_ADD";   # (tautology)
#   # "T10_MUL"   -> "T10_MUL";  # (tautology)
# 
# Sample output (in_edges,out_edges)
#    3 ADD(1,2)     # Found three ADD nodes each with 1 in_edge and 2 out_edges
#    1 const16(0,1) # Found one 'const16' node with 1 out_edge

global node_dict
node_dict = {} # Dictionary?  Is that what this is?
for line in sys.stdin:

    # Strip crlf
    line = line.strip()

    # Strip comments
    line = re.sub(r'#.*', '', line)

    # Only want lines containing "node" -> "node"
    parse = re.search('("\s*->\s*")', line)
    # if parse: print " FOO %s" % parse.group(1)
    if not parse: continue

    DBG=0
    if DBG: print line

    # What we want:
    # > line comes in, looks something like
    #       "T1_0x0000" -> "T1_ADD" -> "T10_out_s3t2_latch";
    # > this should turn into
    #       howmany["0x0000"] = (0,1)
    #       howmany["ADD"]    = (1,1)
    #       howmany["latch"]  = (1,0)
    #
    # Okay so here's the algowizzy:
    # 1. Strip out nonsense chars leaving only
    #    'T1_0x0000 T1_ADD T10_out_s3t2_latch'
    # 2. Turn it into a list, etc. etc.

    # '"T1_0x0000" -> "T1_ADD" -> "T10_out_s3t2_latch";'
    # becomes
    # 'T1_0x0000 T1_ADD T10_out_s3t2_latch'

    line1 = re.sub('[-">;]', '', line)
    line1 = re.sub('\s+', ' ', line1)
    if DBG and (line != line1):
        print "\nFOO< %s"   % line
        print   "FOO> %s\n" % line1

    # 'T1_0x0000 T1_ADD T10_out_s3t2_latch'
    # becomes list
    # (T1_0x0000,T1_ADD,T10_out_s3t2_latch)

    DBG=0
    line_array = line1.split(' ')

    # First node in list: increment out_edges ONLY
    firstnode = line_array[0]
    lastnode  = line_array[-1]
    line_array = line_array[1:-1]
    if DBG:
        print "FOO " + firstnode
        print "FOO " + lastnode
        print "FOO " + str(line_array)
        print ""

    def incnode(node,ein,eout):
        '''Add "in" in-edges and "out" out_edges to "node"'''

        DBG=0
        global node_dict
        if (node not in node_dict):
            # print "> initialize node '%s' = (%d,%d)" % (node, ein, eout)
            node_dict[node] = (ein,eout) # One edge OUT only
        else:
            # print "> inc node '%s' by (%d,%d)" % (node, ein,eout)
            (ein0,eout0) = node_dict[node]
            node_dict[node] = (ein0+ein, eout0+eout)

        if DBG: print "> %s %s" % (node, node_dict[node])

    # First node in list: add one out edge ONLY
    incnode(firstnode, 0, 1)
    incnode(lastnode,  1, 0)
    for node in line_array: incnode(node, 1, 1)

    if DBG: print ""
    continue


# Okay now we're done with phase 1
if DBG: print "phase 1 complete"
if DBG: print sorted(node_dict)  # Same as sorted(node_dict.keys()) 

# Phase 2: canonicalize and merge
# IN:
#    T10_MUL (2, 1)
#    T10_out_s3t2_latch (1, 1)
#    T14_ADD (2, 1)
#    T15_ADD (2, 1)
#    T16_0x000e (0, 1)
#    T16_MUL (2, 1)
#    T16_regA (1, 1)
#
# OUT:
#    MUL(2,1)   2
#    latch(1,1) 2
#    ADD(2,1)   2
#    const15    1
# 

howmany = {}
for node in sorted(node_dict):
    DBG=0
    if DBG: print "NODE %s %s" % (node, node_dict[node])
    (ein,eout) = node_dict[node] # We'll need these later.
    
    # T1_ADD             => ADD
    # T10_out_s3t2_latch => latch
    # T1_0x000b          => const11
    # T16_regA           => latch

    # Strip off tile number e.g. "T10_out_s3t2_latch" => "out_s3t2_latch"
    node = re.sub('^T\d+_','', node)
    if DBG: print "> %s" % node

    # All latches should just be latch e.g. "out_s3t2_latch" => "latch"
    node = re.sub('.*latch.*','latch', node)
    if DBG: print "> %s" % node

    # Also regs are latches e.g. "regA" => "latch"
    node = re.sub('^reg.*','latch', node)
    if DBG: print "> %s" % node

    # All constants should be dec e.g. '0x0011' => 'const17'
    # (Actually it's possible that bsview does this for us now...?

    if re.search('^0x', node):
        node = 'const%d' % int(node,16)
        if DBG: print "> %s" % node

    # Add in,out edges e.g. "const17" => "const17(0,1)"

    node = "%s(i%d,o%d)" % (node,ein,eout)
    if DBG: print "> %s" % node

    # Count 'em up!
    try: # Is this terrible?  It seems terrible
        howmany[node] = howmany[node] + 1
    except: howmany[node] = 1

    if DBG: print "> %s %d\n" % (node, howmany[node])


# The final accounting
if DBG: print "phase 3"
for node in sorted(howmany):
    print "%3d %-15s" % (howmany[node], node)
