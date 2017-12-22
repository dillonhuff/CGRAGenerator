#!/usr/bin/python

import sys
import re
import os

VERBOSE = True

# Script dir is maybe '$gen/testdir/unit_tests'
mypath = os.path.realpath(__file__)
mydir  = os.path.dirname(mypath)
global PYPAT_DIR
PYPAT_DIR = mydir + '/../../../pe'
sys.path.insert(0, PYPAT_DIR)
import pe 

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

VERILATOR_DIR = ''
OPTIONS = {}

def main():
    DBG=0
    mypath = os.path.realpath(__file__)
    mydir  = os.path.dirname(mypath)
    if VERBOSE:
        print ""
        print "Script dir = '%s'" % mydir

    # Script dir is maybe '$gen/testdir/unit_tests'
    global VERILATOR_DIR
    VERILATOR_DIR = mydir + '/../../verilator/generator_z_tb'

#     os.chdir(mydir);
#     if DBG: os.system('pwd');

    process_args()
    show_options()

    # Always build all bsb and bsa files b/c why not
    os.system(mydir+'/gen_bsb_files.py')
    print ""
    sys.stdout.flush()

    if not os.path.exists('op_add.bsa'):
        os.system(mydir+'/gen_bsa_files.csh')
        sys.stdout.flush()

    # n_iter = 'forever'
    # n_iter = 3

    n_iter = OPTIONS['repeat']
    i = 0
    while (i != n_iter):
        i = i + 1
        do_one_round(i)


def show_options():
    for i in OPTIONS:
        print "  OPTIONS['%-7s'] = %s" % (i, OPTIONS[i])


def do_one_round(i):
    print "----------------------------------------------------------------"
    print "Iteration %06d," % i,
    
    # Build input file 'test_in.raw'
    # Build one input file per iteration
    gen_input_file_seq()
    print ""

    t = OPTIONS['tests']
    if t == 'all': tests = ['add','mul','lbuf09']
    else: tests = t.split(",")

    for test in tests:
        do_one_test(test)
        print ""


# E.g. test = 'add'
# bsa files have names like 'mem_lbuf09.bsa', 'op_add.bsa'
def do_one_test(test):
    print "Testing '%s'" % test
    tname_op  = 'op_'  + test
    tname_mem = 'mem_' + test
    if   os.path.exists(tname_op  + '.bsa'): tname = tname_op
    elif os.path.exists(tname_mem + '.bsa'): tname = tname_mem
    else:
        assert False, 'Could not find bsa file'

    DBG=0
    gen_output_file_gold(test, DBG=DBG)
    gen_output_file_cgra(tname, DBG=DBG)
    compare_outputs(tname, DBG=DBG)



def compare_outputs(tname, DBG=0):
    gold_out = '%s_gold_out.raw' % tname
    cgra_out  = '%s_CGRA_out.raw' % tname
    print "  Comparing %s and %s..." % (gold_out,cgra_out)
    cmd = 'cmp %s %s' % (gold_out,cgra_out)
    print "  " + cmd
    err = os.system(cmd)
    if err:
        print "OOPS thatsa no good"
        sys.exit(13)
    else:
        print "   IT'S GOOD!!!"



# pypat['add'](1,3)[0] should yield '4' I think
PYPAT = {}
# PYPAT['add'] = pe.isa.add()
# print PYPAT['add'](1,3)[0]

PYPAT['add']   = pe.isa.add()
PYPAT['sub']   = pe.isa.sub()
PYPAT['abs']   = pe.isa.abs()
# PYPAT['gte']   = pe.isa.ge()
# PYPAT['lte']   = pe.isa.le()
# PYPAT['eq']    = pe.isa.eq()
PYPAT['sel']   = pe.isa.sel()
PYPAT['rshft'] = pe.isa.lshr()
PYPAT['lshft'] = pe.isa.lshl()
PYPAT['or']    = pe.isa.or_()
PYPAT['and']   = pe.isa.and_()
PYPAT['xor']   = pe.isa.xor()

# PYPAT['add'] = (lambda a, b: [a + b,0])
PYPAT['mul']   = (lambda a, b: [a * b,0])
PYPAT['lbuf09']   = (lambda a, b: [a,0])
PYPAT['lbuf10']   = (lambda a, b: [a,0])



def gen_output_file_gold(tname, DBG=0):
    gold_out = 'op_%s_gold_out.raw' % tname

    outpixels = []

    if tname[0:4] == 'lbuf':
        gold_out = 'mem_%s_gold_out.raw' % tname
        outpixels = PIXELS
    else:
        for i in range(len(PIXELS)-1):
            (a,b) = (PIXELS[i], PIXELS[i+1])
            outpixels.append(\
                PYPAT[tname](a,b)[0] & 0xFF \
                )


    # print PYPAT['add'](1,3)[0]
    # print outpixels

    filename = gold_out
    write_pixels(filename, outpixels)
    if DBG>1: print ''

    if VERBOSE:
        print "  gold-model output file '%s':" % filename
        sys.stdout.flush()
        os.system('od -t u1 ' + filename + " | egrep -v '^.......$' | sed 's/^/  /'")
        print ""
    

def gen_output_file_cgra(tname, DBG=0):

    # Note this output name is 'magic' and directs run.csh to do things :(
    # Maybe (FIXME)
    cgra_out = '%s_CGRA_out.raw' % tname

    print "  Will use bsa file '%s.bsa' to generate '%s'" % (tname,cgra_out)
    sys.stdout.flush()
    if DBG: os.system('(cd %s; ls -l run.csh)' % VERILATOR_DIR)

    # Calculate the appropriate delay e.g. '1,0' for PE ops or '9,0' for 9-deep lbuf.
    delay = find_delay(tname, DBG=0)
    
    cwd = os.getcwd() + '/'
    config = cwd + tname+'.bsa'
    input  = cwd + "test_in.raw"
    output = cwd + cgra_out
    logfile = cwd + "run_csh.log"

    run_csh = './run.csh -v'
    # echo "./run.csh -hackmem -config $bsa -input $in -output $cout -delay $delay"
    cmd = "%s -hackmem -config %s -input %s -output %s -delay %s"\
          % (run_csh, config, input, output, delay)

    DBG=0
    if DBG: savelog = ''
    else:   savelog = ' > ' + logfile + ' 2>&1'

    # How to redo on error:
    print ""
    print "  set d = " + cwd
    print "  cd " + VERILATOR_DIR
    print "  " + re.sub(cwd, '$d/', cmd)
    if savelog != '': print "  " + savelog
    print ""
    sys.stdout.flush()

    # (cd $v; ./run.csh -hackmem -config $bsa -input $in -output $cout -delay $delay ) || exit -1
    os.system('(cd %s; %s%s)' % (VERILATOR_DIR, cmd, savelog))
    # if not VERBOSE: os.system('egrep ^run.csh %s' % logfile)
    sys.stdout.flush()

    if VERBOSE:
        print "  CGRA output file '%s':" % cgra_out
        sys.stdout.flush()
        os.system('od -t u1 ' + cgra_out + " | egrep -v '^.......$' | sed 's/./  /'")




def find_delay(tname, DBG=0):
    # Calculate the appropriate delay e.g. '1,0' for PE ops or '9,0' for 9-deep lbuf.
    if tname[0:2] == "op":
        delay = '1,0'
    elif tname[0:8] == 'mem_lbuf':
        # E.g. name might be 'mem_lbuf09'
        d = int(tname[8:])
        delay = '%d,%d' % (d,d)
        # delay = '%d,0' % (d)
    if DBG: print "  delay should be " + delay
    return delay





# Generate an input file full of sequential 8-bit pixels {0,1,2,3,4,5,6,7,8,9}
def gen_input_file_seq():

    DBG=0
    nvecs = 10
    pixels = range(nvecs)

    if DBG>1: print pixels
    filename = 'test_in.raw'
    write_pixels(filename, pixels)
    if DBG>1: print ''

    if VERBOSE:
        print "input file '%s':" % filename
        sys.stdout.flush()
        os.system('od -t u1 ' + filename + " | egrep -v '^.......$'")

    # Save the pixels for later
    global PIXELS
    PIXELS = pixels


def write_pixels(filename, pixels):
    import struct
    outputstream = my_open(filename, "wb")
    for p in pixels: outputstream.write(struct.pack('B', p))
    outputstream.close()

def my_open(filename, mode):
    no_overwrite = False
    if no_overwrite and os.path.exists(filename):
        sys.stderr.write("Don't wanna write over existing file '%s'" % filename)
        sys.exit(-1)
    return open(filename, mode)

def process_args():
    # Get name of this script
    scriptname = sys.argv[0]
    scriptname_tail = scriptname
    parse = re.search('([/].*$)', scriptname)
    parse = re.search('([^/]+$)', scriptname)
    if (parse): scriptname_tail = parse.group(1)
    args = sys.argv[1:] # shift

    usage = '''Run unit tests.

Usage:
   %s <testname> --repeat <nr> --vectype <vt> --nvecs <nv> --seed <s>

Where:
   <testname> = "all" (default) or one of
                {add,sub,abs,gte,lte,eq,sel,rshft,lshft,mul,or,and,xor}
                {lbuf09,lbuf10}

   <nr> = any integer or "forever" DEFAULT=1
   <vt> = seq, rand or drand       DEFAULT="rand"
   <nv> = any integer              DEFAULT=10
   <s>  = any integer              DEFAULT=none

Examples:
   # Run through all tests once w/sequential vectors
   %s --vectype seq

   # Run through all tests until error.
   %s --repeat forever
''' % (scriptname_tail, scriptname_tail, scriptname_tail)

    global VERBOSE
    global OPTIONS
    OPTIONS = {}
    OPTIONS['tests']   = 'all'
    OPTIONS['repeat']  = 1
    OPTIONS['vectype'] = 'random'
    OPTIONS['nvecs']   = 10
    OPTIONS['seed']    = False

    # cgra_filename = get_default_cgra_info_filename()
    while (len(args) > 0):
        if   (args[0] == '--help'): print usage; sys.exit(0);
        elif (args[0] == '-v'):    VERBOSE = True
        elif (args[0] == '--repeat'):
            OPTIONS['repeat'] = args[1];
            args = args[1:];
        elif (args[0] == '--vectype'):
            OPTIONS['vectype'] = args[1];
            args = args[1:];
        elif (args[0] == '--nvecs'):
            OPTIONS['nvecs'] = args[1];
            args = args[1:];
        elif (args[0] == '--seed'):
            OPTIONS['seed'] = args[1];
            args = args[1:];
        else:
            OPTIONS['tests'] = args[0];
        args = args[1:]

    if VERBOSE: print OPTIONS

main()
