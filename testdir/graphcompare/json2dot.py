#!/usr/bin/python


# -*- coding: utf-8 -*-
# python

# example of reading JSON from a file

import json
import re
import sys

filename = "examples/cascade_mapped.json"

# my_data = json.loads(open(filename).read())
my_data = json.loads(sys.stdin.read())

# print my_data
# print "------------------------------------------------------------------------------"

instances = my_data["namespaces"]["global"]["modules"]["DesignTop"]["instances"]
connections = my_data["namespaces"]["global"]["modules"]["DesignTop"]["connections"]


def print_header():
    print "digraph Diagram {"
    print "  node [shape=box]; # Comment"

def print_trailer():
    print "}"

print_header()

DBG=0
if DBG:
    print "INSTANCES"
    for k in instances:
        # print "%s - %s" % (k, instances[k])
        # try:    print "%-12s %s" % (k, instances[k]['configargs'])
        try:    print "%-12s %s" % (k, instances[k]['modargs'])
        except: print "%-12s %s" % (k, "N/A")

def uniquify(nodename):
    '''Turn e.g. "PE_U70.data.out, PE_U8.data.in.1" into "PE_U70, PE_U8"'''
    parse = re.search('([^.]*)[.]', nodename)
    if parse: nodename = parse.group(1)

    # Now turn e.g.
    #    "PE_U70" -> "PE_U70_mul"
    #    "Const_U112" -> "const999"

    # Sample PE node:
    # instances["PE_U8"] = 
    # {u'configargs': {u'op': u'add'}, u'genargs': {u'numin': 2, u'width': 16}, u'genref': u'cgralib.PE'}
    parse = re.search("^PE", nodename)
    if parse:
        # print "FOO", ; print nodename
        # print "FOO", ; print instances[nodename]
        nodename = "%s_%s" % (nodename, instances[nodename]['configargs']['op'])
        return nodename
    
    # Sample const node:
    # instances["Const_U112"] = 
    # {u'configargs': {u'value': 999}, u'genargs': {u'width': 16}, u'genref': u'cgralib.Const'}

    parse = re.search("^Const", nodename)
    if parse:
        # print "FOO", ; print nodename
        # print "FOO", ; print instances[nodename]
        nodename = "const%s" % (instances[nodename]['configargs']['value'])
        return nodename

    # Inputs and outputs BEFORE:
    #   io16in_U0 -> PE_U48_mul
    #   io16_U1 -> PE_U4_add
    #   io16in_U0 -> lb_repeat_edge_2_stencil_update_stream$reg_0_1
    #   io16in_U0 -> lb_repeat_edge_2_stencil_update_stream$mem_1
    # AFTER:
    #   INPUT -> PE_U48_mul
    #   PE_U4_add -> OUTPUT (!!???) (fixed elsewhere i guess)
    #   INPUT -> lb_repeat_edge_2_stencil_update_stream$reg_0_1
    #   INPUT -> lb_repeat_edge_2_stencil_update_stream$mem_1
    parse = re.search("^io16_", nodename)
    if parse: return "OUTPUT"

    parse = re.search("^io16in_", nodename)
    if parse: return "INPUT"


    return nodename

if DBG:
    print "CONNECTIONS"
    print connections

def to_or_from(nodename):

    # Apparently connections are unordered!!?
    # I guess ".in", ".out" is supposed to be some kind of clue... :(

    # Some node names include:
    #   PE_U6.data.out
    #   PE_U66.data.in.1
    #   lb_conv1_2_stencil_update_stream$mem_1.rdata
    #   lb_conv1_2_stencil_update_stream$mem_1.wdata
    #   lb_conv1_2_stencil_update_stream$reg_0_1.out

#     # Special cases for i/o nodes: up is down and down is up
#     if re.search("io16in.*\.out$", nodename): return "from"
#     if re.search("io16.*\.in$",    nodename): return "to"

    parse = re.search("\.out$", nodename)
    if parse:
        # connections go FROM output TO input
        # print "FOO I think conn goes FROM %s" % nodename
        return "from"

    parse = re.search("\.in\.\d+$", nodename)
    if parse:
        # connections go FROM output TO input
        return "to"

    # Not sure this case ever happens
    parse = re.search("\.in$", nodename)
    if parse:
        # connections go FROM output TO input
        return "to"

    if re.search("\.wdata$", nodename): return "to"
    if re.search("\.rdata$", nodename): return "from"

    print "FOO I don't know what '%s' is" % nodename
    return "unknown"

if DBG: print "CONNECTIONS"
for k in connections:
    # print k
    if DBG: print "# %s , %s" % (k[0], k[1])

    u0 = uniquify(k[0])
    u1 = uniquify(k[1])

    # "lb_p4_clamped_stencil_update_stream$mem_1$cgramem":{
    #   "genref":"cgralib.Mem",
    #   "genargs":{"depth":["Int",1024], "width":["Int",16]},
    #   "modargs":{"almost_full_cnt":["Int",0], "fifo_depth":["Int",64], ...
    try:
        fifo_depth = instances[u1]['modargs']['fifo_depth'][1]
        # print "*** %-12s %s" % (u1, fifo_depth)
        fdcomment = ' # fifo_depth %s' % fifo_depth
    except:
        fdcomment = ''

    # Turn "PE_U70.data.out, PE_U8.data.in.1" into "PE_U70, PE_U8"
    from_node = u0
    to_node   = u1

    tf0 = to_or_from(k[0]); 
    tf1 = to_or_from(k[1]); 
    
    if (tf0 == "to") or (tf1 == "from"):
        from_node = u1
        to_node   = u0

#     # For some reason output is emitted backwards-assed...!!?
#     if (innode == "OUTPUT"):
#         innode = outnode
#         outnode = "OUTPUT"

    # print "  %s" % instances[innode]['configargs']

    # print '    "%s" -> "%s";' % (from_node, to_node)
    print '    "%s" -> "%s";%s' % (from_node, to_node, fdcomment)

    if DBG: print ""

print_trailer()

# mydict = 
# for k0 in mydict:
#     print k0
# #     parse = re.search("u'(.*)'", k0)
# #     if parse: k0 = parse.group(1)
#     print mydict[k0]
# #     print "------------------------------------------------------------------------------"
# #     for k1 in my_data[k0]:
# #         print k1



# json file looks like this:
# 
# {"top": "global.DesignTop",
# "namespaces":{
#   "global":{
#     "modules":{
#       "DesignTop":{
#         "type":["Record",{
#           "out":["Array",16,"Bit"],
#           "in":["Array",1,["Array",16,"BitIn"]]
#         }],
#         "instances":{
#           "Const_U100":{
#             "genref":"cgralib.Const",
#             "genargs":{"width":16},
#             "configargs":{"value":999}
#           },
# ...
#           "PE_U12":{
#             "genref":"cgralib.PE",
#             "genargs":{"numin":2, "width":16},
#             "configargs":{"op":"add"}
#           },
# ...
#           "io16in_U0":{
#             "genref":"cgralib.IO",
#             "genargs":{"width":16},
#             "configargs":{"mode":"i"}
#           },
#           "lb_conv1_2_stencil_update_stream$mem_1":{
#             "genref":"cgralib.Mem",
#             "genargs":{"depth":258, "width":16},
#             "configargs":{"mode":"linebuffer"}
#           },
#           "lb_conv1_2_stencil_update_stream$mem_2":{
#             "genref":"cgralib.Mem",
#             "genargs":{"depth":258, "width":16},
#             "configargs":{"mode":"linebuffer"}
#           },
#           "lb_conv1_2_stencil_update_stream$reg_0_1":{
#             "genref":"cgralib.Reg",
#             "genargs":{"width":16}
#           },
# ...
#         "connections":[
#           ["PE_U8.data.in.1","PE_U70.data.out"],
#           ["PE_U72.data.in.1","Const_U112.out"],
#           ["PE_U72.data.in.0","lb_conv1_2_stencil_update_stream$reg_0_1.out"],
#           ["PE_U70.data.in.0","lb_conv1_2_stencil_update_stream$mem_1.rdata"],
#           ["PE_U68.data.in.1","Const_U104.out"],
#           ["PE_U68.data.in.0","lb_repeat_edge_2_stencil_update_stream$reg_0_1.out"],
#           ["PE_U66.data.in.1","Const_U82.out"],
#           ["PE_U66.data.in.0","lb_conv1_2_stencil_update_stream$reg_2_1.out"],
#           ["PE_U64.data.in.1","Const_U84.out"],
#           ["PE_U64.data.in.0","lb_repeat_edge_2_stencil_update_stream$reg_1_2.out"],
#           ["PE_U62.data.in.1","Const_U74.out"],
#           ["PE_U62.data.in.0","lb_repeat_edge_2_stencil_update_stream$reg_1_1.out"],
#           ["PE_U60.data.in.1","Const_U86.out"],
#           ["PE_U60.data.in.0","lb_repeat_edge_2_stencil_update_stream$reg_2_1.out"],
#           ["PE_U6.data.in.1","PE_U58.data.out"],
#           ["PE_U6.data.in.0","PE_U36.data.out"],
#           ["PE_U58.data.in.1","Const_U106.out"],
#           ["PE_U36.data.in.1","PE_U54.data.out"],
#           ["PE_U36.data.in.0","PE_U18.data.out"],
#           ["PE_U12.data.in.0","PE_U10.data.out"],
#           ["PE_U10.data.in.1","PE_U52.data.out"],
#           ["PE_U10.data.in.0","PE_U8.data.out"],
#           ["PE_U4.data.out","io16_U1.in"],
#           ["PE_U16.data.out","lb_conv1_2_stencil_update_stream$reg_0_1.in"],
#           ["PE_U16.data.out","lb_conv1_2_stencil_update_stream$mem_1.wdata"],
#           ["lb_repeat_edge_2_stencil_update_stream$reg_2_2.in","lb_repeat_edge_2_stencil_update_stream$reg_2_1.out"],
#           ["lb_repeat_edge_2_stencil_update_stream$reg_2_1.in","lb_repeat_edge_2_stencil_update_stream$mem_2.rdata"],
#           ["lb_conv1_2_stencil_update_stream$reg_1_2.in","lb_conv1_2_stencil_update_stream$reg_1_1.out"],
#           ["lb_conv1_2_stencil_update_stream$reg_1_1.in","lb_conv1_2_stencil_update_stream$mem_1.rdata"],
#           ["lb_conv1_2_stencil_update_stream$reg_0_2.in","lb_conv1_2_stencil_update_stream$reg_0_1.out"],
#           ["lb_conv1_2_stencil_update_stream$mem_2.wdata","lb_conv1_2_stencil_update_stream$mem_1.rdata"]
#         ]
#       },
# 
# 
# 
