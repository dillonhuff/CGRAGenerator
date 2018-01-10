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

# cgra_info.read_cgra_info('foo')
# w = "T14_out_s5t1"
# cgra=cgra_info.canon2cgra(w)
# # print w, cgra
# glob = cgra_info.canon2global(w)
# print w, cgra, glob
# 
# exit()

def bs_addr_sort(addr):
    '''Bitstream address looks like this: RRFFTTTT;
    but want to sort tile first, then feature, then reg, e.g.
    TTTTFFRR'''
    RR =   addr[0:2]
    FF =   addr[2:4]
    TTTT = addr[4:9]
    if (0):
        print ""
        print '%s: RR=%s, FF=%s, TTTT=%s' % (addr, RR,FF,TTTT)
    return TTTT+FF+RR

def bs_comment_sort(comment):
    '''
    Sorted comments should look like this:
      # data[(13, 12)] : @ tile (0, 0) connect ...
      # data[(3, 2)] : @ tile (0, 0) connect ...
      # data[(1, 0)] : @ tile (0, 0) connect ...
    '''
    sortkey = re.search('^\D+(\d+)', comment).group(1)

    # return (0 - int(sortkey))
    # Ugh okay for compatibility have to do it the dumb way.
    return int(sortkey)


# Sort test(s)
def test_bs_addr_sort():
    tmp = {}
    for i in (
        "00020000",
        "F1000000",
        "FF000000",
        "00020001",
        "00050001",
        "F1000001",
        "FF000001",
        "00050002",
        "F0000002",
        "F1000002",
        "FF000002",
        "01050004",
        "00050005",
        "00050006"
        ):
        print i, bs_addr_sort(i)
        tmp[i] = 17
    print tmp
    
    # for a in sorted(connections.iterkeys())
    for a in sorted(tmp.iterkeys(), key=bs_addr_sort): print a


# Globals
VERBOSE = False
TEST    = False

bitstream = {}
bscomment = {}

curtile = None

# Keep track of what kind of operands each tile needs;
# use an array (dict indexed by integers I guess?)
opa = {}
opb = {}

# Sample input:
#   Tile 7
#   op=mul
#   s3=>a
#   2=>b
#   out=>s0

# Sample input:
# 
# T4_mul(wire,const15_15)    # mul_47515_476_PE
# T8_add(wire,wire)          # add_457_476_477_PE
# T10_mul(reg,const13_13$1)  # mul_48313_484_PE
# 
# T0_in_s2t0 -> T0_out_s0t0 (r)
# T1_in_s2t0 -> T1_out_s0t0
# T2_in_s2t0 -> T2_out_s0t0
# T3_in_s2t0 -> T3_mem_in

def main():
    process_args()

    if not VERBOSE: DBG=0
    else:           DBG=1

    io_info = []

    tileno = -1
    for line in input_lines:
        orig_line = line     # We can use this later...

        # Skip blank lines
        if re.search("^\s*$", line):
            if DBG: print ""
            continue

        # self.in -> T0_in_s2t0
        if re.search('self.in', line):
            io_info.append(process_input(line))
            continue

        # T0_out_s0t0 -> self.out
        if re.search('self.out', line):
            io_info.append(process_output(line))
            continue


        # Save I/O info for later
        # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
        # OUTPUT tile  0 (0,0) / in_BUS16_S1_T1 / wire_1_0_BUS16_S3_T1
        if re.search('^# (IN|OUT)PUT\s+tile', line):
            if DBG: print line
            io_info.append(line)
            if DBG>1: print 'IO_INFO', io_info
            continue

        # Skip comments
        if re.search("^\s*#", line):
            # print "%-40s (comment)" % line
            if DBG: print "#"+line
            continue

        # T4_mul(wire,const15_15)    # mul_47515_476_PE
        # Remove inline comments
        parse = re.search("^(.*\S)\s*#", line)
        if parse: line = parse.group(1)

        if DBG: print "# "+line

        # T4_mul(wire,const15_15) or T3_mem_64
        # Strip off the tile number, leaving e.g. 'mul(wire,const15_15)' or 'mem_64'
        parse = re.search("^T(\d+)_(.*)", line)
        if parse:
            tileno = int(parse.group(1))
            line = parse.group(2)
            if DBG>2: print '# tile%02d  %s' % (tileno,line)


        # mul(wire,const15_15)
        # add(wire,wire) 
        # mul(reg,const13_13$1)
        if bs_op(tileno,line,DBG-1):
            if DBG: print ''
            continue


        # T3_mem_64    # mem_1 fifo_depth=64 => 'mem_64'
        # T17_mem_64   # mem_2 fifo_depth=64 => 'mem_64'
        if bs_mem(tileno,line,DBG-1):
            if DBG: print ''
            continue

        if bs_connection(tileno, line, DBG-1):
            if DBG: print ''
            continue

        err_msg = "\n\n# %s\n" % orig_line\
                  + "I don't know what this is: '%s'\n\n" % line
        assert False, err_msg

        continue

#         ################################################################
#         # This is the old stuff.
#         # SKIP IT for now anyways
#         
#         # "tile=7" (also: "tile7" or "tile=7" or "TILE 7" ...)
#         # (tile) = myparse(line, "\s+tile\s+([0-9]+)")
#         if parse_tile_decl(line):
#             tilestr = "%04X" % int(curtile)
#             continue
# 
#         # "op=mul" or "op MUL"
#         if parse_op(line,tilestr): continue
# 
#         # "in_s3=>a" or "in_s3 -> a" or "in_s3 => wire a" or "in_s3 => reg a"
#         # or "out_s3 => reg a"
#         if parse_opa(line, tilestr): continue
#         
#         # FIXME have to extend above code for operand b (doofus)
# 
#         # "in_s3=>out_s0"
#         if parse_connection(line, tilestr): continue
# 
#         # Konstants: "2=>b"
#         if parse_const(line, tilestr): continue
# 
#         # pe_out=>out_s0
#         # pe_out_res=>out_s0
#         if parse_pe_out(line, tilestr): continue
# 
#         else:
#             print "ERROR I can't do that yet."
#             sys.exit(1)
#         ################################################################
            
    if DBG: print ''
    emit_bitstream()

    # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
    # OUTPUT tile  0 (0,0) / in_BUS16_S1_T1 / wire_1_0_BUS16_S3_T1
    for i in io_info: print i

    return

def preprocess(input_lines, DBG=0):
    # For lazy programmers:
    # Turn 't0_in_s2t0' into 'T0_in_s2t0'
    # Turn 'self.in -> T0_in_s2t0 -> T0_op1' into
    #   'self.in -> T0_in_s2t0'
    #   'T0_in_s2t0 -> T0_op1'

    output_lines = []
    for line in input_lines:
        line = line.strip()
        if DBG: print "LINE0", line

        # Maybe this is a bad road
        # # Turn 't0_in_s2t0' into 'T0_in_s2t0'
        # line1 = re.sub(r't(\d+)_(in|out)', r'T\1_', line)
        # if DBG: print "LINE1", line1
        line1 = line

        # Turn 'a -> b -> c' into 'a -> b', 'b -> c'
        nodes = re.split('\s*->\s*', line1)
        if len(nodes) <= 2:
            output_lines.append(line1)
            continue

        for i in range( len(nodes)-1 ):
            c = '%s -> %s' % (nodes[i], nodes[i+1])
            if DBG: print c
            output_lines.append(c)

        if DBG: print ""

    return output_lines

def process_input(line):
    '''
    line = 'self.in -> T0_in_s2t0'
    rval = 'INPUT  tile  0 (0,0) / in_BUS16_S2_T0 / wire_0_m1_BUS16_S0_T0'
    '''
    wire = re.search('self.in\s*->\s*(\S+)', line).group(1)
    # (tileno,lhs) = striptile(wire)
    # (tileno,lhs) = cgra_info.parse_resource(wire)
    (tileno, dir, side, track) = cgra_info.parse_canon(wire)
    (r,c) = cgra_info.tileno2rc(tileno)
    g = cgra_info.canon2global(wire)
    return '# INPUT  tile  %d (%d,%d) /  %s_BUS16_S%d_T%d / %s' %\
          (tileno, r, c, dir, side, track, g)


def process_output(line):
    '''
    line = 'T0_out_s0t0 -> self.out'
    rval = 'OUTPUT tile  0 (0,0) / out_BUS16_S0_T0 / wire_0_0_BUS16_S0_T0'
    '''
    wire = re.search('(\S+)\s*->\s*self.out', line).group(1)
    (tileno, dir, side, track) = cgra_info.parse_canon(wire)
    (r,c) = cgra_info.tileno2rc(tileno)
    g = cgra_info.canon2global(wire)
    return '# OUTPUT tile  %d (%d,%d) / %s_BUS16_S%d_T%d / %s' %\
          (tileno, r, c, dir, side, track, g)


def bs_connection(tileno, line, DBG=0):
    DBG= max(0,DBG)
    # E.g. line = 'in_s2t0 -> T0_out_s0t0 (r)'
    # or   line = 'T1_in_s2t0 -> T1_out_s0t0/r'
    # or   line = 'T25_out_s2t0 -> T25_op1 (r)'

    parse = re.search('(\w+)\s*->\s*(\w+)[^r]*(r)*', line)
    if not parse: return False

    # print 'Found a connections'

    lhs = parse.group(1)
    rhs = parse.group(2)
    reg = parse.group(3)
    assert reg=='r' or reg==None

    (t,lhs) = striptile(lhs); assert t == -1 or t == tileno, 'wrong tile!?'
    (t,rhs) = striptile(rhs); assert t == -1 or t == tileno, 'wrong tile!?'
    if DBG>1: print "# lhs '%s', rhs '%s', reg '%s'" % (lhs,rhs,reg)

    # Connect lhs to rhs
    
    Tlhs = "T%d_%s" % (tileno,lhs)
    Trhs = "T%d_%s" % (tileno,rhs)
    cwt = cgra_info.connect_within_tile(tileno, Tlhs, Trhs, DBG-1)
    if not cwt:
        # Print useful connection hints
        src_cgra = cgra_info.canon2cgra(Tlhs)
        snk_cgra = cgra_info.canon2cgra(Trhs)
        tile = cgra_info.get_tile(tileno)
        cgra_info.find_mux(tile, src_cgra, snk_cgra, DBG=1)
        sys.exit(-1)
    (addr,data,ra,rd,comm,rcomm) = cwt

    # print 'sel %08X %08X' % (addr,data)
    # print '# ', comm, '\n'
    addbs(addr, data, comm)

    # process reg if one exists
    # (note registered ops are taken care of elsewheres)
    if reg=='r' and not rhs[0:2]=='op':
        # print 'reg %08X %08X' % (ra,rd)
        # print '# ', rcomm, '\n'
        addbs(ra, rd, rcomm)

    return True


def striptile(r):
    '''
    Given a resource name 'r' e.g. one of
        T0_in_s2t0
        in_s2t0
        T24_add(wire,wire)
    strip off the leading tilenumber 'T24' if one exists and return
    (tileno,stripped_name)
    If no leading tilenumber then tileno = -1
    '''
    # Strip off the tile number, if one exists
    parse = re.search("^T(\d+)_(.*)", r)
    if not parse: return(-1, r)

    tileno = int(parse.group(1))
    r      = parse.group(2)
    return(tileno,r)




def parse_tile_decl(line):
        # "tile=7" (also: "tile7" or "tile=7" or "TILE 7" ...)
        # (tile) = myparse(line, "\s+tile\s+([0-9]+)")
        DBG=0
        (tile) = myparse(line, "\s*tile\D*(\d)")
        if tile:
            # print tile
            tilestr = "%04X" % int(tile)
            if DBG: print "# Found tile '%s' = 0x%s" % (tile, tilestr)
            if DBG: print ""

            # No operands yet
            tileno = int(tile)
            print "# TILE %d (r,c)" % tileno
            global curtile; curtile = tileno
            (opa[tileno],opb[tileno]) = (False,False)

            return True
        else: return False











# def parse_op(line,tilestr):
#         # "op=mul" or "op MUL"
#         (op) = myparse(line, "\s*op\W+(\w+)")
#         if op:
#             tileno = int(tilestr,16)
#             # FF000001 0000800B
#             # # data[(4, 0)] : op = mul
#             # # data[(13, 13)] : read from reg `b`
#             # # data[(15, 15)] : read from wire `a`
#             # print "# Found op '%s'" % op
#             
#             # An op needs operands.  Default is "wire" for both
#             # operands 'a' and 'b' unless/until something overrides
#             if not opa[tileno]: set_opa(tileno, 'wire')
#             if not opb[tileno]: set_opb(tileno, 'wire')
# 
#             # Sample comment:
#             # 00020007 00000005 # data=5 => op=mul
# 
# 
#             # FIXME should probably be "op_reg + op_feat + tilestr" instead
#             addr = "FF00" + tilestr
#             data = op_data[op]
#             addbs(addr, data, line)
#             return True
#         else: return False
        
def parse_opa(line, tilestr):
        # "in_s3=>a" or "in_s3 -> a" or "in_s3 => wire a" or "in_s3 => reg a"
        # or "out_s3 => reg a"
        (io, side, wr) = myparse(line,"(in|out)_s([\d+])\W+(reg|wire)?.*a\s*$")

        if io:
            DBG=0
            tileno = int(tilestr,16)
            # print (io,side,wr)
            # sys.exit(0)
            # First let's take care of wire/reg spec
            if wr == "wire" or wr == 'reg':
                if DBG: print "# Found wire '%s_s%st0' => %s a" % (io, side, wr)
                set_opa(tileno, wr)

            # <cb feature_address='2' bus='BUS16'>
            #     <mux snk='op_a_in'>
            #       <src sel='0'>in_BUS16_S2_T0</src>
            #       <src sel='5'>out_BUS16_S2_T0</src>

            # We're only using track 0 (!), so only two choice is s2
            if side == '2':
                addr = "0002"+tilestr
                if io == "in": data = "00000000"
                else:          data = "00000005"
                addbs(addr, data, line)
                return True

            else:
                print "OOPS 'a' can only connect to side 2, not side %s" % side
                print "Maybe try this:"
                print "  in_s%s -> out_s2" % side
                print "  out_s2 -> a"
                print ""
                return True
                
        else: return False

def parse_connection(line,tilestr):
        # "in_s3=>out_s0"
        (inside,outside) = myparse(line,".*in_s(\d+).*out_s(\d+)")
        if inside:
            DBG=0
            if DBG: print "# Found in_s%s => out_s%s" % (inside, outside)

            inbus = "in_BUS16_S%s_T0" % inside
            outbus= "out_BUS16_S%s_T0" % outside
            # connectbus('pe_out_res', 'out_BUS16_S2_T0')
            (data,comment) = connectbus(inbus, outbus)
            # I think.  FIXME reg and feature should come from cgra_info, duh.
            addr = "0005"+tilestr
            addbs(addr, data, line+"\n# "+comment)
            return True
        else: return False
            


# def parse_const(line, tilestr):
#         # Konstants: "2=>b"
#         (k,operand) = myparse(line,"(\d+)[^ab]+([ab])")
#         if (k):
#             DBG=0
#             if DBG: print "# Found constant '%s' assigned to operand '%s'" % (k, operand)
# 
#             # A
#             # F0000008 00000002 # data[(15, 0)]=2 : init `a` reg with const `2`
#             # FF000008 0000000B # data[(15,15)]=0 : read from reg `a`
#             # 
#             # or B
#             # F1000008 00000002 # data[(15, 0)]=2 : init `b` reg with const `2`
#             # FF000008 0000000B # data[(13,13)]=0 : read from reg `b`
#                                  
#             comment = line
#             tileno = int(tilestr,16)
#             if (operand=='a'):
#                 addr = "F000"+tilestr; opa[tileno] = 'reg'
#                 # print "# Remember opa[%04X] = %s" % (tileno, opa[tileno])
#                 comment = "# Remember opa[%04X] = %s" % (tileno, opa[tileno])
#             else:
#                 addr = "F100"+tilestr; opb[tileno] = 'reg'
#                 # print "# Remember opb[%04X] = %s" % (tileno, opb[tileno])
#                 comment = "# Remember opb[%04X] = %s" % (tileno, opb[tileno])
#             
#             data = "%08X" % int(k)
#             addbs(addr, data, line+"\n"+comment)
#             return True
# 
#         else: return False

def parse_pe_out(line,tilestr):
        # Given a line that looks like that below, build bitstream info
        # pe_out=>out_s0
        # pe_out_res=>out_s0
        outside = myparse(line,"pe_out[^o]+out_s(\d+)")
        if outside:
            DBG=0
            if DBG: print "# Found pe_out_res => out_s%s" % outside
            # print "# use cgra_info library to look up mux for out_s%st0" % outside

            # inbus = "in_BUS16_S%s_T0" % inside
            inbus = "pe_out_res"
            outbus= "out_BUS16_S%s_T0" % outside
            # connectbus('pe_out_res', 'out_BUS16_S2_T0')
            (data,comment) = connectbus(inbus, outbus)

            # I think.  FIXME reg and feature should come from cgra_info, duh.
            addr = "0005"+tilestr
            addbs(addr, data, line+"\n# "+comment)
            return True
        else:
            return False




def emit_bitstream():
    DBG=0
    if VERBOSE: print "# FINAL PASS: EMIT BITSTREAM"
    if VERBOSE: print "#----------------------------------------------------------------"
    for addr in sorted(bitstream.iterkeys(), key=bs_addr_sort):
        if DBG:
            print "# " + addr, bscomment[addr]
            print "# " + addr, bitstream[addr]
            print ""

        # We don't do this no more (i think)
        # # If addr indicates an op, then merge in operands a, b
        # insert_operands(addr)

        data = merge_data(addr)
        if (data == "ERROR"): sys.exit(1)

        # print data, type(data)
        print "%s %08X" % (addr,data)

        for c in sorted(bscomment[addr], key=bs_comment_sort): print "# " + c
        print ""

        
# We don't do this no more (i think)
# def insert_operands(addr, DBG=1):
#     # If addr indicates an op, then merge in operands a, b
#     (is_op, tilestr) = myparse(addr, "(....)(....)")
#     if is_op == "FF00":
#         tileno = int(tilestr,16)
#         wra = opa[tileno]+'_a' # 'wire_a' or 'reg_a'
#         wrb = opb[tileno]+'_b' # 'wire_b' or 'reg_b'
#         bitstream[addr].append(op_data[wra])
#         bitstream[addr].append(op_data[wrb])
#         if DBG:
#             print "# Found a op.  Adding operands to merge-list..."
# 
#             print "# opa = %7s = %s" % (wra, op_data[wra])
#             print "# opb = %7s = %s" % (wrb, op_data[wrb])
#             print "# " + addr, bitstream[addr]
#             print ""





# <sb feature_address='5' bus='BUS16'>
#     <sel_width>2</sel_width>
#     <mux snk='out_BUS16_S0_T0' reg='1' configh='1' configl='0' configr='40'>
#       <src sel='0'>in_BUS16_S1_T0</src>
#       <src sel='1'>in_BUS16_S2_T0</src>
#       <src sel='2'>in_BUS16_S3_T0</src>
#       <src sel='3'>pe_out_res</src>


            #             print wire
            #             print tmp
            #             sys.exit(0)

#             addr = "FF00" + tilestr
#             data = op_data['wire_a']
#             addbs(addr,data)


def set_opa(tileno, wr):
    DBG=0
    # print "# Setting a input to default 'wire'"
    opa[tileno] = wr;
    if DBG: print "# opa[%04X] = %s" % (tileno, opa[tileno])
    
def set_opb(tileno, wr):
    DBG=0
    # print "# Setting a input to default 'wire'"
    opb[tileno] = wr;
    if DBG: print "# opb[%04X] = %s" % (tileno, opb[tileno])




# % grep localparam $top/../pe_new/pe/rtl/test_pe_comp.svp | grep _OP
# localparam PE_ADD_OP     = 6'h0;
# localparam PE_SUB_OP     = 6'h1;
# localparam PE_ABS_OP     = 6'h3;
# localparam PE_GTE_MAX_OP = 6'h4;
# localparam PE_LTE_MIN_OP = 6'h5;
# localparam PE_EQ_OP      = 6'h6;
# localparam PE_SEL_OP     = 6'h8;
# localparam PE_RSHFT_OP   = 6'hF;
# localparam PE_LSHFT_OP   = 6'h11;
# localparam PE_MULT_0_OP  = 6'hB;
# localparam PE_MULT_1_OP  = 6'hC;
# localparam PE_MULT_2_OP  = 6'hD;
# localparam PE_OR_OP      = 6'h12;
# localparam PE_AND_OP     = 6'h13;
# localparam PE_XOR_OP     = 6'h14;
# no
# localparam PE_CNTR_OP    = 6'h18;
# localparam PE_DIV_OP     = 6'h19;

op_data = {} # dictionary
# op_data['add']   = 0x00000000
# op_data['mul']   = 0x0000000B
op_data['add']     = 0x00000000
op_data['sub']     = 0x00000001
op_data['abs']     = 0x00000003
op_data['gte']     = 0x00000004
op_data['lte']     = 0x00000005
op_data['eq']      = 0x00000006
op_data['sel']     = 0x00000008
op_data['rshft']   = 0x0000000F
op_data['lshft']   = 0x00000011
op_data['mul']     = 0x0000000B
op_data['or']      = 0x00000012
op_data['and']     = 0x00000013
op_data['xor']     = 0x00000014




# A (data0) mode bits are 16,17; REG_CONST=0; REG_DELAY=3; REG_BYPASS=2
op_data['const_a'] = (0 << 16)
op_data['wire_a']  = (2 << 16)
op_data['reg_a']   = (3 << 16)

# B (data1) mode bits are 18,19; REG_CONST=0; REG_DELAY=3; REG_BYPASS=2
op_data['const_b'] = (0 << 18)
op_data['wire_b']  = (2 << 18)
op_data['reg_b']   = (3 << 18)


def bs_mem(tileno, line, DBG=0):
    # IN:
    # mem_64

    # OUT (see e.g. ../examples/bw1000.bsa)
    # 00040003 00000204
    # data[(1, 0)] : mode = linebuffer
    # data[(2, 2)] : tile_en = 1
    # data[(15, 3)] : fifo_depth = 64
    # data[(18, 16)] : almost_full_count = 0
    # data[(19, 19)] : chain_enable = 0

    parse = re.search('mem_(\d+)', line)
    if not parse: return False

    fd = int(parse.group(1))
    # print '666foo found mem w/fd=%s' % fd

    addr = 0x00040000 | tileno
    data = 0x00000004 | (fd<<3)
    comment = [
        "data[(1, 0)] : mode = linebuffer",
        "data[(2, 2)] : tile_en = 1",
        "data[(15, 3)] : fifo_depth = %d" % fd,
        "data[(18, 16)] : almost_full_count = 0",
        "data[(19, 19)] : chain_enable = 0",
        ]
    addbs(addr, data, comment)
    return True



def bs_op(tileno, line, DBG=0):
    # IN:
    # mul(wire,const15_15)
    # add(wire,wire) 
    # mul(reg,const13_13$1)

    # OUT (../examples/bw1000.bsa):
    # FF000001 0003 000B
    # data[(4, 0)] : alu_op = mul
    # data[(17, 16)] : data0: REG_DELAY
    # data[(19, 18)] : data1: REG_CONST

    parse = re.search('(\S+)\s*\(\s*(\S+)\s*,\s*(\S+)\s*\)', line)
    if not parse: return False

    opname = parse.group(1)       # 'mul'
    op1    = parse.group(2)+"_a"  # 'reg_a' or 'wire_a' or 'const19_19$1_a'
    op2    = parse.group(3)+"_b"

    if DBG>1: print '# tile%02d  %s %s %s' % (tileno,opname,op1,op2)
    if opname not in op_data: return False

    # If op is a const, returns 'const_a' or 'const_b'
    op1 = bs_const(tileno, op1, 'op1')
    op2 = bs_const(tileno, op2, 'op2')

    assert op1=='reg_a' or op1=='wire_a' or op1=='const_a',op1
    assert op2=='reg_b' or op2=='wire_b' or op2=='const_b',op2

    data = op_data[opname] | op_data[op1] | op_data[op2] 

    # Address for a PE is reg 'FF' + elem '00' + tileno e.g. '0001'
    addr = "FF00%04X" % tileno
    
    # data[(4, 0)] : alu_op = mul
    # data[(17, 16)] : data0: REG_DELAY
    # data[(19, 18)] : data1: REG_CONST

#     # "reg_a" => "reg 'a'"
#     op1 = re.sub(r'_([ab])', r" '\1'", op1)
#     # comment = op1

    comment = [
        "data[(4, 0)] : alu_op = %s" % opname,
        "data[(17, 16)]: data0: %s" % regtranslate(op1),
        "data[(19, 18)]: data1: %s" % regtranslate(op2),
        ]
    addbs(addr, data, comment)
    return True

def regtranslate(op):
    if op[0:3]=='reg': return 'REG_DELAY'
    if op[0:3]=='wir': return 'REG_BYPASS'
    if op[0:3]=='con': return 'REG_CONST'



def bs_const(tileno,op,operand):
    '''
    Where const = e.g. "const13_13$1" and operand= "op1"
    If 'op' not a const, return 'op' unchanged.
    If 'op' is a const, process it and return
    'const_a' or 'const_b' as appropriate.
    '''

    if op[0:5] != 'const': return op
    
    const = op

    DBG=0
    if DBG: print "# Found constant '%s' assigned to operand '%s'" \
              % (const, operand)

    # OP1
    # F0000008 00000002 # data[(15, 0)]=2 : init `a` reg with const `2`
    # FF000008 0000000B # data[(15,15)]=0 : read from reg `a`
    # 
    # or OP2
    # F1000008 00000002 # data[(15, 0)]=2 : init `b` reg with const `2`
    # FF000008 0000000B # data[(13,13)]=0 : read from reg `b`

    # Parse the constant e.g. 'const13_13$1' == 13
    k = int(re.search('const(\d+)', const).group(1))
    #data = "%08X" % k
    data = k
    
    # Address for a const is reg 'F0' + elem '00' + tileno e.g. '0008'
    # (op2 constant is 'F1' instead of 'F0')
    if operand=='op1':
        const = 'const_a'
        addr = "F000%04X" % tileno
        comment = "data[(15, 0)] : init `data0` reg with const `%d`" % k
    else:
        const = 'const_b'
        addr = "F100%04X" % tileno
        comment = "data[(15, 0)] : init `data1` reg with const `%d`" % k

    addbs(addr, data, comment)
    return const
    # return "%s %s %s" % (addr, data, comment)

#     comment = line
#     tileno = int(tilestr,16)
#     if (operand=='a'):
#         addr = "F000"+tilestr; opa[tileno] = 'reg'
#         # print "# Remember opa[%04X] = %s" % (tileno, opa[tileno])
#         comment = "# Remember opa[%04X] = %s" % (tileno, opa[tileno])
#     else:
#         addr = "F100"+tilestr; opb[tileno] = 'reg'
#         # print "# Remember opb[%04X] = %s" % (tileno, opb[tileno])
#         comment = "# Remember opb[%04X] = %s" % (tileno, opb[tileno])
# 
#     data = "%08X" % int(k)
#     addbs(addr, data, line+"\n"+comment)
#     return True
# 
# 








# sb_config and sb_annote are dictionaries of lists of strings
# containing sb config and annote strings
#   sb_config["00050007"] = ("02020000","00001100")
#   sb_annote["00050007"] = ("# annote1...", "# annote2...")

# cb_config = {}; cb_annote = {}
# sb_config = {}; sb_annote = {}
def addbs(addr,data, comment=''):
    if type(addr) == int: addr = "%08X" % addr
    data = '%08X' % data

    try: bitstream[addr]
    except:
        bitstream[addr] = []
        bscomment[addr] = []

    # Watch for redundant info
    for d in bitstream[addr]:
        if d == data:
            if VERBOSE:
                print '# '
                print "# WARNING redundant instruction, this was already done (and/or it's the default)"
                print "# %s %s" % (addr,data),
                print ":: bs['%s'] = %s" % (addr, bitstream[addr])

            # BUT!  Still want a comment :(
            if data != '00000000': return


    bitstream[addr].append(data)

    if type(comment)==str: comment = [comment]
    bscomment[addr] = bscomment[addr] + comment

    if VERBOSE:
        print '# '
        print "# %s %s" % (addr,data),
        print ":: bs['%s'] = %s" % (addr, bitstream[addr])

        # if comment != '': print "# " + comment
        for c in comment: print "# " + c
        
    # Howzabout a quick error check on cb, sb elements
    feature = int(addr[2:4],16)

    # FIXME this should really be a cgra_info function!!!
    # hack (2,3,5) are cba, cbb and sb16 in PE tiles FIXME
    if feature in (2,3,5,7):
        valid = merge_data(addr) # Just for the error check
        if valid == "ERROR":
            print "ERROR This connection collides with a previous one"


def merge_data(addr, DBG=0):
    mdata = 0
    for data in bitstream[addr]:
        d = int(data,16)
        # print "%08x %08x" % (d, mdata)
        if (d & mdata):
            print "ERROR Collision in data for address '%s'" % addr
            return "ERROR"
        else: mdata = mdata | d
    return mdata



def myparse(line, regexp):
    #     print line
    #     print regexp
    ngroups = re.compile(regexp).groups

    match = re.search(regexp, line)
    #     match = re.search(".*tile", "tile")
    #     print re.search("\s*.*tile\s*(\d)", "tile 7").group(1)
    #     sys.exit(0)
    #     print match
    #     print match.group(1)
    if match:
        g = match.groups()
        if ngroups == 1: return g[0]
        else:           return match.groups()
    else:
        if ngroups == 1: return False
        else:            return [False] * ngroups


# def num_groups(regex):
#     return re.compile(regex).groups





# see cgra_info.get_default_cgra_info_filename() instead
# def get_default_cgra_info_filename():
#     '''
#     Look for default cgra_info file in <decoder-directory>/examples/cgra_info.txt
#     '''
#     import os
#     mydir = os.path.dirname(os.path.realpath(__file__))
#     cgra_filename = mydir + "../decoder/examples/cgra_info.txt"
# 
#     # global verbose #(implied because use before def)
#     if VERBOSE: print("I think I am here:\n  %s" % mydir)
#     if VERBOSE: print("Default cgra_info file is\n  %s" % cgra_filename)
#     return cgra_filename


input_lines = []
def process_args():
    DBG=0
    bitstream_filename = False

    # Get name of this script
    scriptname = sys.argv[0]
    scriptname_tail = scriptname
    parse = re.search('([/].*$)', scriptname)
    parse = re.search('([^/]+$)', scriptname)
    if (parse): scriptname_tail = parse.group(1)
    args = sys.argv[1:] # shift

    usage = '''
Decodes/annotates the indicated bitstream file, output to stdout
Usage:
   %s [ -v ] -cgra [cgra_info_file] < [bsb-file]
   %s [ -v ] -cgra [cgra_info_file] [bsb-file]
   %s [ -v ] < [bsb-file]
   %s [ -v ] [bsb-file]
   %s --help
''' % (scriptname_tail, scriptname_tail, scriptname_tail, scriptname_tail, scriptname_tail)

    # Load cgra_info
    cgra_filename = cgra_info.get_default_cgra_info_filename()

    # if (len(args) < 1): print usage; sys.exit(-1);

    global VERBOSE
    # cgra_filename = get_default_cgra_info_filename()
    while (len(args) > 0):
        if   (args[0] == '--help'): print usage; sys.exit(0);
        elif (args[0] == '-v'):    VERBOSE = True
        elif (args[0] == '-q'):    VERBOSE = False
        elif (args[0] == '-cgra' or args[0] == '-cgra_info'):
            cgra_filename = args[1]
            args = args[1:];
        else:
            bitstream_filename = args[0];
        args = args[1:]

    cgra_info.read_cgra_info(cgra_filename, verbose=VERBOSE)

    global input_lines
    if bitstream_filename:
        input_stream = open(bitstream_filename)
        for line in input_stream: input_lines.append(line)
        input_stream.close()
    else:
        for line in sys.stdin: input_lines.append(line)
        
    # Read the input, store to 'input_lines' tuple
    input_lines = preprocess(input_lines)
    if DBG>1:
        for i in input_lines: print i


def find_outreg16(outwire):
    mux = find_outmux16(outwire)
    r = mux.attrib['configr']
    print "# To enable register just do 1 << r"


def connectbus(inbus, outbus):
    DBG = 0
    mux = find_outmux16(outbus)
    h = int(mux.attrib['configh'])
    l = int(mux.attrib['configl'])
    if h>31 or l>31: print "ERROR ERROR ERROR "

    for src in mux:
        sel = int(src.attrib['sel'])
        if src.text == inbus:
            comment = "bits[%s:%s]=%s for %s => %s" % (h, l, sel, src.text, outbus)

            # print "#     bits[%s:%s]=%s to select source %s" % (h, l, sel, src.text)
            if DBG: print "# "+comment
            data = "%08X" % (sel << l)
            # print "# %s" % data
            # return (sel, h, l, r)
            return (data, comment)
        


    # FIXME TROUBLE if configl or configr > 31...




def find_outmux16(outwire):
    DBG = 0
    sb = find_sb16()
    for item in sb:
        if item.tag == 'mux':
            # print 'found a mux'
            snk = item.attrib['snk']
            if snk == outwire:
                if DBG: print "#    Found the mux for outwire '%s'" % snk
                return item



def find_sb16():
    DBG = 0
    # if DBG: print "Looking up tile %d element %d" % (tileno, elemno)
    if DBG: print "# use cgra_info library to look up mux connections"
    if DBG: print "# Find first tile that's a PE"
    for tile in cgra_info.CGRA.findall('tile'):
        type = tile.attrib['type']
        if DBG: print "#  Found tile type '%s'" % type
        if type == 'pe_tile_new':
            for feature in tile:
                # if DBG: print "# Found feature '%s'" % feature.tag
                if feature.tag == "sb" and feature.attrib['bus'] == 'BUS16':
                    if DBG: print "#   Found the sb for 16-bit track"
                    return feature
                    
                

main()



