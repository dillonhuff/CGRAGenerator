#!/usr/bin/python

import os
import sys
import re

TEST_STRING='''

#TEST mem10
T3_mem_10                             # (fifo_depth=10)
self.in -> T3_in_s2t0 -> T3_mem_in
T3_mem_out -> T3_out_s2t0 -> self.out

#DELAY 10,0
#IN  0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,13
#OUT 0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,13
#--------------------------------------------

#TEST mem09
T3_mem_9                              # (fifo_depth=9)
self.in -> T3_in_s2t0 -> T3_mem_in
T3_mem_out -> T3_out_s2t0 -> self.out

#DELAY 9,0
#IN  0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,19
#OUT 0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,19

'''

def main ():
    delay = 0
    tests = {}
    test_inputs = {}
    test_outputs = {}
    testname = False
    test_lines = TEST_STRING.split('\n')
    for line in test_lines:

        parse = re.search('#\s*TEST\s+(\S+)', line)
        if parse:
            testname = parse.group(1)
            # print "Found test '%s'" % testname
            tests[testname] = []

        parse = re.search('#\s*DELAY\s+(\d+)', line)
        if parse:
            delay = parse.group(1)

        parse = re.search('#\s*IN\s+(.*)', line)
        if parse:
            inputs = parse.group(1)

            # Automatically add nulls to compensate for delay
            if delay:
                for i in range(101,101+int(delay)):
                    # inputs = inputs + ',' + str(i)
                    inputs = inputs + ',255'

            # print "Found inputs '%s'" % inputs
            test_inputs[testname] = inputs

        parse = re.search('#\s*OUT\s+(.*)', line)
        if parse:
            outputs = parse.group(1)
            # print "Found outputs '%s'" % outputs
            test_outputs[testname] = outputs

        if testname: tests[testname].append(line)
            
    for testname in tests:
        write_lines(tests[testname], testname + '.bsb')
        write_array(test_inputs[testname], testname + '_input.raw')
        write_array(test_outputs[testname], testname + '_output.raw')


def my_open(filename, mode):
    no_overwrite = False
    if no_overwrite and os.path.exists(filename):
        sys.stderr.write("Don't wanna write over existing file '%s'" % filename)
        sys.exit(-1)
    return open(filename, mode)


def write_lines(lines, filename):
    outputstream = my_open(filename, "w")
    for line in lines: outputstream.write(line+'\n')
    outputstream.close()

def write_array(astring, filename):
    import struct
    outputstream = my_open(filename, "wb")
    pixels = astring.split(',')
    for p in pixels:
        s = re.search('(\S+)',p).group(1)
        n = int(s, 0) # base '0' => convert according to string e.g. '0x14' => 20
        outputstream.write(struct.pack('B', n))
    outputstream.close()






#         outputstream = open(test_filename, "wb")
#         outputstream.write(struct.pack('i', 69))
        


main()

