#!/usr/bin/python

import sys;
import re;

# from ../decoder/lib import cgra_info
sys.path.append("../decoder")
from lib import cgra_info


# Sort test(s)

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

def main():

    process_args()

#     print cgra_info.tileno2rc(7)
# 
#     # find_mux_deets('pe_out_res', 'out_BUS16_S2_T0')
#     connectbus('pe_out_res', 'out_BUS16_S2_T0')


#     sys.exit(0)


    # Read the input, store to 'input_lines' tuple
    input_lines = [] # for line in sys.stdin: input_lines.append(line)
    for line in sys.stdin: input_lines.append(line)

    for line in input_lines:
        line = line.strip().lower()

        # Skip blank lines
        if re.search("^\s*$", line):
            print ""
            continue

        # Skip comments
        if re.search("^\s*#", line):
            # print "%-40s (comment)" % line
            print "#"+line
            continue

        DBG=0
        if DBG: print "# "+line

        # "tile=7" (also: "tile7" or "tile=7" or "TILE 7" ...)
        # (tile) = myparse(line, "\s+tile\s+([0-9]+)")
        if parse_tile_decl(line):
            tilestr = "%04X" % int(curtile)
            continue

        # "op=mul" or "op MUL"
        if parse_op(line,tilestr): continue

        # "in_s3=>a" or "in_s3 -> a" or "in_s3 => wire a" or "in_s3 => reg a"
        # or "out_s3 => reg a"
        if parse_opa(line, tilestr): continue
        
        # FIXME have to extend above code for operand b (doofus)

        # "in_s3=>out_s0"
        if parse_connection(line, tilestr): continue

        # Konstants: "2=>b"
        if parse_const(line, tilestr): continue

        # pe_out=>out_s0
        # pe_out_res=>out_s0
        if parse_pe_out(line, tilestr): continue

        else:
            print "ERROR I can't do that yet."
            sys.exit(1)
            
    emit_bitstream()

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



def parse_op(line,tilestr):
        # "op=mul" or "op MUL"
        (op) = myparse(line, "\s*op\W+(\w+)")
        if op:
            tileno = int(tilestr,16)
            # FF000001 0000800B
            # # data[(4, 0)] : op = mul
            # # data[(13, 13)] : read from reg `b`
            # # data[(15, 15)] : read from wire `a`
            # print "# Found op '%s'" % op
            
            # An op needs operands.  Default is "wire" for both
            # operands 'a' and 'b' unless/until something overrides
            if not opa[tileno]: set_opa(tileno, 'wire')
            if not opb[tileno]: set_opb(tileno, 'wire')

            # Sample comment:
            # 00020007 00000005 # data=5 => op=mul


            # FIXME should probably be "op_reg + op_feat + tilestr" instead
            addr = "FF00" + tilestr
            data = op_data[op]
            addbs(addr, data, line)
            return True
        else: return False
        
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
            


def parse_const(line, tilestr):
        # Konstants: "2=>b"
        (k,operand) = myparse(line,"(\d+)[^ab]+([ab])")
        if (k):
            DBG=0
            if DBG: print "# Found constant '%s' assigned to operand '%s'" % (k, operand)

            # A
            # F0000008 00000002 # data[(15, 0)]=2 : init `a` reg with const `2`
            # FF000008 0000000B # data[(15,15)]=0 : read from reg `a`
            # 
            # or B
            # F1000008 00000002 # data[(15, 0)]=2 : init `b` reg with const `2`
            # FF000008 0000000B # data[(13,13)]=0 : read from reg `b`
                                 
            comment = line
            tileno = int(tilestr,16)
            if (operand=='a'):
                addr = "F000"+tilestr; opa[tileno] = 'reg'
                # print "# Remember opa[%04X] = %s" % (tileno, opa[tileno])
                comment = "# Remember opa[%04X] = %s" % (tileno, opa[tileno])
            else:
                addr = "F100"+tilestr; opb[tileno] = 'reg'
                # print "# Remember opb[%04X] = %s" % (tileno, opb[tileno])
                comment = "# Remember opb[%04X] = %s" % (tileno, opb[tileno])
            
            data = "%08X" % int(k)
            addbs(addr, data, line+"\n"+comment)
            return True

        else: return False


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
    DBG=1
    print "# FINAL PASS: EMIT BITSTREAM"
    print "#----------------------------------------------------------------"
    for addr in sorted(bitstream.iterkeys(), key=bs_addr_sort):
        if DBG:
            print "# " + addr, bscomment[addr]
            print "# " + addr, bitstream[addr]
            print ""

        # If addr indicates an op, then merge in operands a, b
        insert_operands(addr)
        data = merge_data(addr)
        if (data == "ERROR"): sys.exit(1)

        # print data, type(data)
        print "%s %08X" % (addr,data)
        for c in bscomment[addr]: print "# " + c
        print ""


        # Merge all the data into one
#         mdata = 0
#         for d in bitstream[addr]:
            
        

        
def insert_operands(addr, DBG=1):
    # If addr indicates an op, then merge in operands a, b
    (is_op, tilestr) = myparse(addr, "(....)(....)")
    if is_op == "FF00":
        tileno = int(tilestr,16)
        wra = opa[tileno]+'_a' # 'wire_a' or 'reg_a'
        wrb = opb[tileno]+'_b' # 'wire_b' or 'reg_b'
        bitstream[addr].append(op_data[wra])
        bitstream[addr].append(op_data[wrb])
        if DBG:
            print "# Found a op.  Adding operands to merge-list..."

            print "# opa = %7s = %s" % (wra, op_data[wra])
            print "# opb = %7s = %s" % (wrb, op_data[wrb])
            print "# " + addr, bitstream[addr]
            print ""





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



op_data = {} # dictionary
op_data['mul'] = "0000000B"

# B mode bits are 12,13
op_data['reg_b']  = "%08X" % (0 << 12)
op_data['wire_b'] = "%08X" % (2 << 12)

# A mode bits are 14,15
op_data['reg_a']  = "%08X" % (0 << 14)
op_data['wire_a'] = "%08X" % (2 << 14)




# sb_config and sb_annote are dictionaries of lists of strings
# containing sb config and annote strings
#   sb_config["00050007"] = ("02020000","00001100")
#   sb_annote["00050007"] = ("# annote1...", "# annote2...")

# cb_config = {}; cb_annote = {}
# sb_config = {}; sb_annote = {}
def addbs(addr,data, comment=''):
    try:
        bitstream[addr].append(data)
        bscomment[addr].append(comment)
    except:
        bitstream[addr] = []
        bitstream[addr].append(data)
        bscomment[addr] = []
        bscomment[addr].append(comment)

    if comment != '': print "# " + comment

    print "# %s %s" % (addr,data),
    print ":: bs['%s'] = %s" % (addr, bitstream[addr])

    # Howzabout a quick error check on cb, sb elements
    feature = int(addr[2:4],16)

    # FIXME this should really be a cgra_info function!!!
    # hack (2,3,5) are cba, cbb and sb16 in PE tiles FIXME
    if feature in (2,3,5,7):
        valid = merge_data(addr) # Just for the error check
        if valid == "ERROR":
            print "ERROR This connection collides with a previous one"
    print ""


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






def get_default_cgra_info_filename():
    '''
    Look for default cgra_info file in <decoder-directory>/examples/cgra_info.txt
    '''
    import os
    mydir = os.path.dirname(os.path.realpath(__file__))
    cgra_filename = mydir + "../decoder/examples/cgra_info.txt"

    # global verbose #(implied because use before def)
    if VERBOSE: print("I think I am here:\n  %s" % mydir)
    if VERBOSE: print("Default cgra_info file is\n  %s" % cgra_filename)
    return cgra_filename

def process_args():

    scriptname = sys.argv[0];
    args = sys.argv[1:];


    scriptname_tail = scriptname
    parse = re.search('([/].*$)', scriptname)
    parse = re.search('([^/]+$)', scriptname)
    if (parse): scriptname_tail = parse.group(1)

    usage = '''
Decodes/annotates the indicated bitstream file
Usage:
   %s [ -v ] <bitstream-file> -cgra <cgra_info_file>
   %s --help
''' % (scriptname_tail, scriptname_tail)

    # sbdefaults = True;
    cgra_filename = get_default_cgra_info_filename()

    # if (len(args) < 1):       print usage; sys.exit(-1);

    global VERBOSE
    while (len(args) > 0):
        if (args[0] == '--help'): print usage; sys.exit(0);
        # global VERBOSE # this causes problems/errors
        # if   (args[0] == '-nodefaults'): sbdefaults = False
        if   (args[0] == '-v'):    VERBOSE = True
        elif (args[0] == '-4x4'): print 'WARNING switch "-4x4" not used'
        elif (args[0] == '-8x8'): print 'WARNING switch "-8x8" not used'
        elif (args[0] == '-cgra' or args[0] == '-cgra_info'):
            cgra_filename = args[1]
            args = args[1:];
        else:
            bitstream_filename = args[0];
        args = args[1:]

    # read_cgra_info() does this...
    # if VERBOSE: print("Using uh cgra_info file %s" % cgra_filename)
    # if VERBOSE: print("and VERBOSE is '%s'" % str(VERBOSE))
    cgra_info.read_cgra_info(cgra_filename, verbose=VERBOSE)



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



# print '''
# NEXT:
# - sort bs by index
# - emit each bs_addr data, merging where appropriate
# - when feature = '00' (pe), remember to merge in the operands
# '''
# 
