#!/bin/csh -f

# Given bmark name e.g. 'pointwise'
# Assumes existence of
#   tmpdir/pointwise_CGRA_out.raw and
#   examples/pointwise_halide_out.raw


set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h
cd $scriptpath

# Script is maybe in $gen/bitstream/bsbuilder/testdir
# set gen = `(cd ../../..; pwd)`
# set v =  $gen/verilator/generator_z_tb


# Do them in order
# set bmarks = (pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw)
set bmarks = (pointwise conv_2_1 conv_3_1 conv_bw)

set b = $1
# foreach b ($bmarks)

  # set test = examples/${b}_input.raw
  set test =   tmpdir/${b}_CGRA_out.raw
  set gold = examples/${b}_halide_out.raw

  echo "$test looks like this:"
  set cmd = "od -t u1 $test"
  echo $cmd; $cmd | head; echo ...; $cmd | tail -n 3
  echo ''

  echo "$gold looks like this:"
  set cmd = "od -t u1 $gold"
  echo $cmd; $cmd | head; echo ...; $cmd | tail -n 3
  echo ''
  cmp $test $gold\
    && echo "TEST RESULT $b PASSED"\
    || echo "TEST RESULT $b FAILED"\

  echo '------------------------------------------------------------------------'

# end
