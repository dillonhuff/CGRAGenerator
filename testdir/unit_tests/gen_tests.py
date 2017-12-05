#!/usr/bin/python

import os
import sys
import re
import random

# Replace 'DEPTH' with a decimal integer %03d
MEM_TEMPLATE='''
  #DELAY DEPTH,0
  T3_mem_DEPTH # (fifo_depth=DEPTH)
  self.in -> T3_in_s2t0 -> T3_mem_in
  T3_mem_out -> T3_out_s2t0 -> self.out
'''

# Replace OPNAME with name of operand e.g. 'add'
OP_TEMPLATE='''
  #TEST OPNAME
  #DELAY 1,0
  self.in -> T0_in_s2t0
  T0_in_s2t0 -> T0_op1
  T0_in_s2t0 -> T0_out_s1t0
  T0_out_s1t0 -> T0_op2 (r)
  T0_OPNAME(wire,reg)
  T0_pe_out -> T0_out_s0t1 -> self.out
'''

TEST_LIST=[
    'lbuf10',
    'lbuf09',
    'add'
    ]

def build_optest(testname):
    # E.g. testname=add
    DBG=1

    bsb = re.sub('OPNAME','%s' % testname, OP_TEMPLATE)

    # Add test name and write the bsb file
    bsb = ('#TEST  %s' % testname) + bsb

    # Remove excess indentation
    bsb = re.sub('\n\s+', '\n', bsb)

    if DBG: print bsb
    write_bsb(testname + '.bsb', bsb)

    # Generate numbers for input file, plus one zero at the end for padding
    pixels = range(16) \
             + random.sample(range(0, 255), 48)\
             + [0]
    # ilist = random.sample(range(0, 255), 100)
    if DBG: print pixels
    write_pixels(testname + '_input.raw', pixels)
    if DBG: print ''

    # Generate output pixels based on opname
    outpixels = range(len(pixels)-1)
    if (testname == 'add'):
        for i in outpixels:
            outpixels[i] = (pixels[i] + pixels[i+1]) & 0xff
    if DBG: print outpixels
    write_pixels(testname + '_output.raw', outpixels)

def build_lbuftest(testname):
    # E.g. testname=mem09 for 9-deep fifo

    # E.g. 'fifo009' => delay='9'
    delay = str(int(re.search('lbuf(\d+)', testname).group(1)))
    bsb = re.sub('DEPTH','%s' % delay, MEM_TEMPLATE)

    # Remove excess indentation
    bsb = re.sub('\n\s+', '\n', bsb)

    # Add test name and write the bsb file
    bsb = ('#TEST  %s' % testname) + bsb
    if DBG: print bsb
    write_bsb(testname,bsb)

    # # Generate 100 random numbers for the input file
    # import random
    # ilist = random.sample(range(0, 255), 100)

    # Generate full range of numbers for input file;
    # add zero-padding to compensate for delay
    pixels = range(256)
    write_pixels(testname + '_input.raw', pixels + (int(delay) * [0]))

    # Because it's a FIFO (linebuffer), expect the same 100 numbers for output
    write_pixels(testname + '_output.raw', pixels)


def my_open(filename, mode):
    no_overwrite = False
    if no_overwrite and os.path.exists(filename):
        sys.stderr.write("Don't wanna write over existing file '%s'" % filename)
        sys.exit(-1)
    return open(filename, mode)

def write_bsb(filename, bsb):
    outputstream = my_open(filename, "w")
    outputstream.write(bsb)
    outputstream.close()

def write_pixels(filename, pixels):
    import struct
    outputstream = my_open(filename, "wb")
    for p in pixels: outputstream.write(struct.pack('B', p))
    outputstream.close()



def main ():
    # For each test e.g. 'lbuf10' build bsb file 'lbuf10.bsb'
    # plus input and output files 'lbuf10_{input,output}.raw'

    tests = {}
    for testname in TEST_LIST:
        if testname[0:4]=='lbuf': build_lbuftest(testname)
        else: build_optest(testname)


main()

