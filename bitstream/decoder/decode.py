#!/usr/bin/python
import sys;
import re;


# To use: decoder.py < examples/bitstream.ankita

from lib.sb_decode_5tracks import *

scriptname = sys.argv[0];
args = sys.argv[1:];

usage = "\n"\
  + "Decodes/annotates the indicated bitstream file\n"\
  + "Usage:\n"\
  + "   %s <bitstream-file>\n" % scriptname\
  + "   %s --help\n" % scriptname\
  + ""

if (len(args) < 1):      print usage; sys.exit(-1);
if (args[0] == '--help'): print usage; sys.exit(0);
bitstream_filename = args[0];


# def sb_decode(reg_num, reg_contents):
#   if (reg_num == 0): return sb_decode_r0(reg_contents);
#   if (reg_num == 1): return sb_decode_r1(reg_contents);
#   
# print sb_decode(0, 0);

# list = range(0,15)
# print list
# print list[0:3]
# print list[1:3]
# print list[3:20:5]


print "";
print "Assume 4x4 grid of tiles numbered like so:\n"+\
      "                           \n"+\
      "          0    4    8    12\n"+\
      "                           \n"+\
      "          1    5    9    13\n"+\
      "                           \n"+\
      "          2    6    10   14\n"+\
      "                           \n"+\
      "          3    7    11   15\n"+\
      "";
print "Assume all tiles have 2-input PEs";
print "";
print "'s1t3' means 'side 1 track 3' where sides [0123] map to [ESWN] respectively"
print "";

def EE_decode(EE):
    # Given string EE = one of "00", "01", ... "07", return element name
    # "pe", op", etc. as shown below

    #   EE   2-input PE    3-input PE
    #   --   ----------    ----------
    #   00   PE            PE
    #   01   OP            OP
    #   02   CB1           CB1
    #   03   CB2           CB2
    #   04   CB4           CB3
    #   05   SB1           CB4
    #   06   SB2           SB1
    #   07   N/A           SB2

    element = {};
    element["00"] =   "pe";
    element["01"] =   "op";
    element["02"] =   "cb1";
    element["03"] =   "cb2";
    element["04"] =   "cb4";
    element["05"] =   "sb1";
    element["06"] =   "sb2";
    return element[EE];

# Given 8-digit hex string DDDDDDDD = e.g. "00000002", tell what
# switchbox will do with the data, e.g. sb_decode("00000000") = "out <= in_0"
def cb_decode(EE, DDDDDDDD):
    # Connection box dataword only uses bottom 4 bits interpreted as shown below (see cb.v).
    #   cb1 connects pe input A to a north-south wire track
    #   cb2 connects pe input B to an east-west wire track
    #
    # cb1 (EE = 02):
    #     [01234]: pe_inp_a = in_BUS16_S1_T[01234]
    #     [56789]: pe_inp_a = in_BUS16_S3_T[01234]
    # 
    # cb2 (EE = 03):
    #     [01234]: pe_inp_b = in_BUS16_S0_T[01234]
    #     [56789]: pe_inp_b = in_BUS16_S2_T[01234]

    if (not re.search("0000000[0-9]", DDDDDDDD)):
        sys.stdout.flush();
        sys.stderr.write("\nERROR bad value '%s' for connection box\n" % DDDDDDDD);
        sys.exit(-1);

    st = {};

    # input A side 0 (S)
    st["02.00000000"] = "wireA <= in_s1t0"
    st["02.00000001"] = "wireA <= in_s1t1"
    st["02.00000002"] = "wireA <= in_s1t2"
    st["02.00000003"] = "wireA <= in_s1t3"
    st["02.00000004"] = "wireA <= in_s1t4"

    # input A side 3 (N)
    st["02.00000005"] = "wireA <= in_s3t5"
    st["02.00000006"] = "wireA <= in_s3t6"
    st["02.00000007"] = "wireA <= in_s3t7"
    st["02.00000008"] = "wireA <= in_s3t8"
    st["02.00000009"] = "wireA <= in_s3t9"

    # input B side 0 (E)
    st["03.00000000"] = "wireB <= in_s0t0"
    st["03.00000001"] = "wireB <= in_s0t1"
    st["03.00000003"] = "wireB <= in_s0t2"
    st["03.00000003"] = "wireB <= in_s0t3"
    st["03.00000004"] = "wireB <= in_s0t4"

    # input B side 2 (W)
    st["03.00000005"] = "wireB <= in_s2t5"
    st["03.00000006"] = "wireB <= in_s2t6"
    st["03.00000007"] = "wireB <= in_s2t7"
    st["03.00000008"] = "wireB <= in_s2t8"
    st["03.00000009"] = "wireB <= in_s2t9"

    return st[EE + '.' + DDDDDDDD]

def sb_print(RR, DDDDDDDD):
    # if (RR == "00"): connection_list = sb_decode_r0(int(DDDDDDDD, 16));
    # if (RR == "01"): connection_list = sb_decode_r1(int(DDDDDDDD, 16));
    connection_list = sb_decode(int(RR), int(DDDDDDDD, 16));

    # Connection list should contain fifteen items
    # ['in_s1t0 -> out_s0t0', 'in_s1t0 -> out_s0t1', 'in_s1t0 -> out_s0t2',
    #  'in_s1t0 -> out_s0t3', 'in_s1t0 -> out_s0t4', 'in_s0t1 -> out_s1t0',
    #  'in_s0t1 -> out_s1t1', 'in_s0t1 -> out_s1t2', 'in_s0t1 -> out_s1t3',
    #  'in_s0t1 -> out_s1t4', 'in_s0t2 -> out_s2t0', 'in_s0t2 -> out_s2t1',
    #  'in_s0t2 -> out_s2t2', 'in_s0t2 -> out_s2t3', 'in_s0t2 -> out_s2t4',
    #  'in_s0t3 -> out_s3t0']

    # This sorts them into three columns of five rows each:
    #     in_s1t0 -> out_s0t0    in_s0t1 -> out_s1t0    in_s0t2 -> out_s2t0
    #     in_s1t0 -> out_s0t1    in_s0t1 -> out_s1t1    in_s0t2 -> out_s2t1
    #     in_s1t0 -> out_s0t2    in_s0t1 -> out_s1t2    in_s0t2 -> out_s2t2
    #     in_s1t0 -> out_s0t3    in_s0t1 -> out_s1t3    in_s0t2 -> out_s2t3
    #     in_s1t0 -> out_s0t4    in_s0t1 -> out_s1t4    in_s0t2 -> out_s2t4
    col1 = connection_list[0:5];   # print col1;
    col2 = connection_list[5:10];  # print col2;
    col3 = connection_list[10:15]; # print col3;

    for i in range(0,5):
        # print "%8s %8s" % ("", ""),
        if (i): print "%8s %8s %19s" % ("", "", ""),
        print "%-19s    %-19s    %-19s" % (col1[i], col2[i], col3[i]);

def pe_decode(RR, DDDDDDDD):

    global asrc, bsrc, csrc, dsrc
    global areg, breg, creg, dreg

    # F000xxxx xxxxDDDD => load reg a w/ DDDD (once)
    # F100xxxx xxxxDDDD => load reg b w/ DDDD (once)
    # F300xxxx xxxxDDDD => load reg d w/ DDDD (once)

    # Load constants
    k = 0;
    DDDD = DDDDDDDD[4:8]   # last four hex digits
    dstring = "0x" + DDDD  # Same, with a "0x" in front
    # Note: C input unused/invalid for 2-input PEs!
    if (RR == "F0"): areg = dstring; k="A"
    if (RR == "F1"): breg = dstring; k="B"
    if (RR == "F2"): creg = dstring; k="C"
    if (RR == "F3"): dreg = dstring; k="D"; print "\n\nFOOOOOOOOOOOOOOO\n\n"
    if (k):
        # print "\n\nFOOAA %s\n\n" % breg
        print "reg%s <= %s" % (k, dstring);
        return;

    # Only other valid option is "FF" (load opcode)
    if (RR != "FF"):
        print "ERROR Unknown register code for PE"
        sys.stdout.flush()
        sys.stderr.write("\n\nERROR Unknown register code for PE");
        sys.exit(-1);

    # (Note default value for all tiles is opcode = 16'h0000 (ADD)

    ########################################################################
    # Figure out sources for A, B inputs

    # FF00xxxx xxxxDDDD =>
    # case DDDD[15:8]: program behavior of operands A, B, D

    dddd = int(DDDD,16) >> 8;

    # 0xxx,xxxx => (always) read A from reg_a
    # 1xxx,xxxx => (always) read A from wire op_a_in
    # x1xx,xxxx => (always) load reg a from wire op_a_in
    # 
    # xx0x,xxxx => (always) read B from reg_b
    # xx1x,xxxx => (always) read B from wire op_b_in
    # xxx1,xxxx => (always) load reg b from wire op_b_in
    # 
    # xxxx,xx0x => (always) read D from reg_d
    # xxxx,xx1x => (always) read D from wire op_d_in
    # xxxx,xxx1 => (always) load reg a from wire op_d_in

    # (Note default value for all tiles is opcode = 16'h0000 (ADD, src=reg, reg=wire)

    if (dddd & 0x80): asrc = "wireA";
    if (dddd & 0x40): areg = "wireA";

    if (dddd & 0x20): bsrc = "wireB";
    if (dddd & 0x10): breg = "wireB";

    if (dddd & 0x02): dsrc = "wireD";
    if (dddd & 0x01): dreg = "wireD";  print "BOOOOOOOOOOOOOOOOO " + DDDD + "  " + str(dddd);

    ########################################################################
    # Set the PE operation

    # case DDDD[4:0]: program PE op type (default out1 = carry from adder)
    #   00: out16 = ADD(a,b)           out1 = carry
    #   01: out16 = SUB(a,b)           out1 = carry
    #   04: out16 = MAX(A,B)           out1 = GE(a,b)
    #   05: out16 = MIN(A,B)           out1 = LT(a,b)
    #   06: out16 = B                  out1 = XNOR reduction ~|(a^b) (?)
    #   07: out16 = A                  out1 = XOR  reduction  |(a^b) (?)
    #   08: out16 = MUX d ? a : b      out1 = carry
    #   0B: out16 = MUL(a,b)[15: 0]    out1 = carry
    #   0C: out16 = MUL(a,b)[23: 8]    out1 = carry
    #   0D: out16 = MUL(a,b)[31:16]    out1 = carry
    #   0F: LSHR out16 = a  >> b[3:0]  ...
    #   10: ASHR out16 = a >>> b[3:0]
    #   11: SHL  out16 = a <<< b[3:0]
    #   12: OR   out16 = a | b
    #   13: AND  out16 = a & b
    #   14: XOR  out16 = a ^ b
    #   15: NOT  out16 = ~a

#     op = DDDDDDDD[6:8] # last two hex digits
# 
#     if   (op == "00"): opstr = "pe_out <= ADD(A,B)"
#     elif (op == "01"): opstr = "pe_out <= SUB(A,B)"
# 
#     elif (op == "04"): opstr = "pe_out <= MAX(A,B), pe_out_p <= GE(A,B)"
#     elif (op == "05"): opstr = "pe_out <= MIN(A,B), pe_out_p <= LT(A,B)"
# 
#     elif (op == "06"): opstr = "pe_out <= B, pe_out_p <= XNOR reduction ~|(a^b) (?)"
#     elif (op == "07"): opstr = "pe_out <= A, pe_out_p <= XOR  reduction  |(a^b) (?)"
# 
#     elif (op == "08"): opstr = "pe_out <= MUX d ? a : b"
# 
#     elif (op == "0B"): opstr = "pe_out <= MUL(A,B)"
#     elif (op == "0C"): opstr = "pe_out <= MUL(A,B) [23:8]"
#     elif (op == "0D"): opstr = "pe_out <= MUL(A,B) [31:16]"
# 
#     elif (op == "0F"): opstr = "pe_out <= LSHR(A,B[3:0])"
#     elif (op == "10"): opstr = "pe_out <= ASHR(A,B[3:0])"
#     elif (op == "11"): opstr = "pe_out <=  SHL(A,B[3:0])"
# 
#     elif (op == "12"): opstr = "pe_out <=  OR(A,B)"
#     elif (op == "13"): opstr = "pe_out <= AND(A,B)"
#     elif (op == "14"): opstr = "pe_out <= XOR(A,B)"
#     elif (op == "15"): opstr = "pe_out <= NOT(A,B)"
# 
#     else:
#         sys.stdout.flush()
#         sys.stderr.write("\n\nERROR Unknown/invalid opcode for PE");
#         sys.exit(-1);
# 
#     print opstr;

    iohack = 0;

    op = DDDDDDDD[6:8] # last two hex digits
    A = "A"; B = "B";
    A = asrc; B = bsrc;

    # areg can be one of "wireA", "0x[0-9]+", "unset"
    if ((asrc == "regA") and re.search("0x", areg)): A = areg;
    if ((bsrc == "regB") and re.search("0x", breg)): B = breg;
    if ((asrc == "regC") and re.search("0x", creg)): A = creg;
    if ((asrc == "regD") and re.search("0x", dreg)): A = dreg;

    if   (op == "00"): opstr = "ADD(%s,%s)" % (A,B)
    elif (op == "01"): opstr = "SUB(%s,%s)" % (A,B)

    elif (op == "04"): opstr = "MAX(%s,%s), pe_out_p <= GE(%s,%s)" % (A,B,A,B)
    elif (op == "05"): opstr = "MIN(%s,%s), pe_out_p <= LT(%s,%s)" % (A,B,A,B)

    elif (op == "06"): opstr = "%s, pe_out_p <= XNOR reduction ~|(a^b) (?)" % (B)
    elif (op == "07"): opstr = "%s, pe_out_p <= XOR  reduction  |(a^b) (?)" % (A)

    elif (op == "08"): opstr = "MUX d ? a : b"

    elif (op == "0B"): opstr = "MUL(%s,%s)"         % (A,B)
    elif (op == "0C"): opstr = "MUL(%s,%s) [23:8]"  % (A,B)
    elif (op == "0D"): opstr = "MUL(%s,%s) [31:16]" % (A,B)

    elif (op == "0F"): opstr = "LSHR(%s,%s[3:0])" % (A,B)
    elif (op == "10"): opstr = "ASHR(%s,%s[3:0])" % (A,B)
    elif (op == "11"): opstr = " SHL(%s,%s[3:0])" % (A,B)

    elif (op == "12"): opstr = " OR(%s,%s)" % (A,B)
    elif (op == "13"): opstr = "AND(%s,%s)" % (A,B)
    elif (op == "14"): opstr = "XOR(%s,%s)" % (A,B)
    elif (op == "15"): opstr = "NOT(%s,%s)" % (A,B)

    elif (op == "F0"):
        # IO hack/inputs
        #   FF00xxxx 000000F0    # (op==F0): pe_out is input to CGRA
        #   F000xxxx FFFFFFFF   # IO input pad: ignore pe_in_a
        #   F100xxxx FFFFFFFF   # IO input pad: ignore pe_in_b

        opstr = "IO hack: pe_out is CGRA INPUT"; iohack = 1;
        opstr = opstr + "\n                                     " + \
                "(IN  wire_0_0_BUS16_S1_T0) (out_s1t0)"

    elif (op == "FF"):
        # IO hack/outputs
        #   FF00xxxx 000000FF    # (op==FF): pe_in_a (wireA) is CGRA output
        #   F1000004 00000000    # IO output pad: ignore pe_in_b
        opstr = "IO hack: pe_in_a (wireA) is CGRA OUTPUT"; iohack = 1;
        opstr = opstr + "\n                                     " + \
                "(OUT wire_1_0_BUS16_S1_T0) (in_s1t0)"

    else:
        print "ERROR Unknown/invalid opcode for PE"
        sys.stdout.flush()
        sys.stderr.write("\n\nERROR Unknown/invalid opcode for PE");
        sys.exit(-1);

    if (iohack): print opstr
    else:        print "pe_out <= " + opstr;

    indent = "%8s %8s %20s" % ('','','')
    if (areg == "wireA"): print indent + "regA <= wireA (always)"
    if (breg == "wireB"): print indent + "regB <= wireB (always)"
    if (creg == "wireC"): print indent + "regC <= wireC (always)"
    if (dreg == "wireD"): print indent + "regD <= wireD (always)"


#     print "\n"
#     print "\n"
# 
# 








# Maybe do this:
# FF000008 0000F00B # rFF e00 (pe)  :: pe_out <= MUL(pe_A,reg_B)
#                                   :: reg_A <= pe_A, reg_B <= pe_B


##############################################################################
# MAIN
prevtile = -1
# inputstream = sys.stdin;
inputstream = open(bitstream_filename);
# print inputstream.next();
for line in inputstream:
    line = line.strip(); # Ugh "strip is the worst...ugly but necessary.

    # Address RREETTTT
    f = re.search("(..)(..)(....) (........)", line);
    RR = f.group(1);       # register
    EE = f.group(2);       # element
    TTTT = f.group(3);     # tile
    DDDDDDDD = f.group(4); # data


    thistile = int(TTTT,16)
    if (thistile != prevtile):

        # Sources for PE inputs (defaults from verilog test_pe.v and test_opt_reg.v)
        global asrc, bsrc, csrc, dsrc
        asrc = 'regA' # valid values: 'wireA' or 'regA' or "0x[0-9]+"
        bsrc = 'regB' # valid values: 'wireB' or 'regB' or "0x[0-9]+"
        csrc = 'regC' # valid values: 'wireC' or 'regC' or "0x[0-9]+"
        dsrc = 'regD' # valid values: 'wireD' or 'regD' or "0x[0-9]+"

        # Contents of PE input regs
        global areg, breg, creg, dreg
        areg = "unset"   # valid values: "0x[0-9]+" or 'wireA' or 'unset'
        breg = "unset"   # valid values: "0x[0-9]+" or 'wireB' or 'unset'
        creg = "unset"   # valid values: "0x[0-9]+" or 'wireC' or 'unset'
        dreg = "unset"   # valid values: "0x[0-9]+" or 'wireD' or 'unset'

        prevtile = thistile
        print ""
        print "# TILE %d (r,c)" % thistile
        # TBD/FIXME decode r,c

    print line,
    print "[ r%02X e%02X %-5s ]  " % (int(RR,16)    \
                                  ,int(EE,16)    \
                                  ,"(" + EE_decode(EE) + ")" \
                              ),

    # Processing element
    if (EE == "00"): pe_decode(RR, DDDDDDDD);

    # Connection box
    elif (EE == "02" or EE == "03"):
        # print "%s   # %s" % (line, cb_decode(EE,DDDDDDDD));
        print "%s" % (cb_decode(EE,DDDDDDDD));

    elif (EE == "05"):
        # print "";
        sb_print(RR, DDDDDDDD);
        # print "";
    #     if (EE == "05"):
    #         if (RR == "00"): prettyprint(sb_decode_r0(int(DDDDDDDD, 16)));
    #         if (RR == "01"): prettyprint(sb_decode_r1(int(DDDDDDDD, 16)));

    else:
        print "";

inputstream.close();

# prettyprint(sb_decode_r0(0));
# sys.exit(0);


#     regno = int(RR, 16);
#     elno  = int(EE, 16);
#     tileno = int(TTTT, 16);
#     print "  Tile %d, element %d, register %d\n" % (tileno, elno, regno);
