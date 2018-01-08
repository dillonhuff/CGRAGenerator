#!/usr/bin/python

import os
import sys
import re
import random

# Version for CGRA w/o IO tiles
# # Replace 'DEPTH' with a decimal integer %03d
# MEM_TEMPLATE='''
#   #DELAY DEPTH,0
#   #
#   T3_mem_DEPTH # (fifo_depth=DEPTH)
#   self.in -> T3_in_s2t0 -> T3_mem_in
#   T3_mem_out -> T3_out_s2t0 -> self.out
# '''

<<<<<<< HEAD
# OOPS with IO tiles included, first mem tile is...?  tile 14?
# Replace 'DEPTH' with a decimal integer %03d
MEM_TEMPLATE='''
  #DELAY DEPTH,DEPTH
  #
  T14_mem_DEPTH # (fifo_depth=DEPTH)
  self.in -> T14_in_s2t0 -> T14_mem_in
  T14_mem_out -> T14_out_s2t0 -> self.out
'''

=======
# # OOPS with IO tiles included, first mem tile is...?  tile 14?
# # Replace 'DEPTH' with a decimal integer %03d
# MEM_TEMPLATE='''
#   #DELAY DEPTH,DEPTH
#   #
#   T14_mem_DEPTH # (fifo_depth=DEPTH)
#   self.in -> T14_in_s2t0 -> T14_mem_in
#   T14_mem_out -> T14_out_s2t0 -> self.out
# '''

# # Send output to PE tile T11
# MEM_TEMPLATE='''
#   #DELAY DEPTH,DEPTH
#   #
#   self.in -> T11_in_s2t0
#   T11_in_s2t0 -> T11_out_s0t0
#   T12_in_s2t0 -> T12_out_s0t0
#   T13_in_s2t0 -> T13_out_s0t0
#   T14_in_s2t0 -> T14_mem_in
#   T14_mem_DEPTH # (fifo_depth=DEPTH)
#   T14_mem_out -> T14_out_s2t1
#   T13_in_s0t1 -> T13_out_s2t1
#   T12_in_s0t1 -> T12_out_s2t1
#   T11_in_s0t1 -> T11_out_s2t1 -> self.out
# '''

# Input from PE tile 11, output to mem tile T14
MEM_TEMPLATE='''
  #DELAY DEPTH,DEPTH
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_out_s0t0
  T12_in_s2t0 -> T12_out_s0t0
  T13_in_s2t0 -> T13_out_s0t0
  T14_in_s2t0 -> T14_mem_in
  T14_mem_DEPTH # (fifo_depth=DEPTH)
  T14_mem_out -> T14_out_s1t1
  T14_in_s7t1 -> T14_out_s5t1 -> self.out
'''

# MEM_TEMPLATE='''
#   #DELAY DEPTH,DEPTH
#   #
#   self.in -> T11_in_s2t0 -> T11_out_s0t0 -> T12_out_s0t0 -> T13_out_s0t0
#   T14_in_s2t0 -> T14_mem_in
#   T14_mem_DEPTH # (fifo_depth=DEPTH)
#   T14_mem_out -> T14_out_s2t0 -> self.out
# '''


>>>>>>> srdev

# Version for CGRA w/o IO tiles
# # Replace OPNAME with name of operand e.g. 'add'
# OP_TEMPLATE_OLD='''
#   #DELAY 1,1
#   #
#   self.in -> T0_in_s2t0
#   T0_in_s2t0 -> T0_op1
#   T0_in_s2t0 -> T0_out_s1t0
#   T0_out_s1t0 -> T0_op2 (r)
#   T0_OPNAME(wire,reg)
#   T0_pe_out -> T0_out_s0t1 -> self.out
# '''

<<<<<<< HEAD
=======
# THIS ONE CRASHES!!
>>>>>>> srdev
# OOPS with IO tiles included, first PE tile is...? tile 11?
# Replace OPNAME with name of operand e.g. 'add'
# BAD reg op1 ba
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T11_in_s2t0
<<<<<<< HEAD
  T11_in_s2t0 -> T11_op1
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2 (r)
  T11_OPNAME(wire,reg)
  T11_pe_out -> T11_out_s0t1 -> self.out
'''

=======
  T11_in_s2t0 -> T11_op1 (r)
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2
  T11_OPNAME(reg,wire)
  T11_pe_out -> T11_out_s0t1 -> self.out
'''

# OOPS with IO tiles included, first PE tile is...? tile 11?
# Replace OPNAME with name of operand e.g. 'add'
# GOOD reg op2 ab
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_op1
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2 (r)
  T11_OPNAME(wire,reg)
  T11_pe_out -> T11_out_s0t1 -> self.out
'''

# Input from PE tile 11, output to mem tile T14
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_op1
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2 (r)
  T11_OPNAME(wire,reg)
  T11_pe_out -> T11_out_s0t1
  T12_in_s2t1 -> T12_out_s0t1
  T13_in_s2t1 -> T13_out_s0t1
  T14_in_s2t1 -> T14_out_s1t1
  T14_in_s7t1 -> T14_out_s5t1 -> self.out
'''




>>>>>>> srdev

# bsbuilder now has support for...
# op_data['add']     = 0x00000000
# op_data['sub']     = 0x00000001
# op_data['abs']     = 0x00000003
# op_data['gte']     = 0x00000004
# op_data['lte']     = 0x00000005
# op_data['eq']      = 0x00000006
# op_data['sel']     = 0x00000008
# op_data['rshft']   = 0x0000000F
# op_data['lshft']   = 0x00000011
# op_data['mul']     = 0x0000000B
# op_data['or']      = 0x00000012
# op_data['and']     = 0x00000013
# op_data['xor']     = 0x00000014

OP_LIST=[
    'add',
    'sub',
    'abs',
    'gte',
    'lte',
    'eq',
    'sel',
    'rshft',
    'lshft',
    'mul',
    'or',
    'and',
    'xor',
    ]

LBUF_LIST=[
    'lbuf10',
    'lbuf09'
    ]

DBG=0
VERBOSE = True

def main ():
    # For each test e.g. 'lbuf10' build bsb file 'lbuf10.bsb'
    # plus input and output files 'lbuf10_{input,output}.raw'

    if VERBOSE: print "gen_bsb_files.py:"
    for testname in OP_LIST:   build_optest(testname)
    for testname in LBUF_LIST: build_lbuftest(testname)

def build_optest(testname):
    bsb = re.sub('OPNAME','%s' % testname, OP_TEMPLATE)
    write_bsb('op_' + testname, bsb, DBG=DBG)

def build_lbuftest(testname):
    delay = str(int(re.search('lbuf(\d+)', testname).group(1)))
    bsb = re.sub('DEPTH','%s' % delay, MEM_TEMPLATE)
    write_bsb('mem_' + testname, bsb, DBG=DBG)

def write_bsb(testname, bsb, DBG=1):
    # Remove excess indentation
    bsb = re.sub('\n\s+', '\n', bsb)

    # Add test name
    bsb = ('#TEST %s' % testname) + bsb
    if DBG: print bsb

    # ...and write the bsb file
    testfile = testname + '.bsb'
    outputstream = my_open(testfile, "w")
    outputstream.write(bsb)
    outputstream.close()
    if VERBOSE: print "  Built " + testfile

def my_open(filename, mode):
    no_overwrite = False
    if no_overwrite and os.path.exists(filename):
        sys.stderr.write("Don't wanna write over existing file '%s'" % filename)
        sys.exit(-1)
    return open(filename, mode)

main()

