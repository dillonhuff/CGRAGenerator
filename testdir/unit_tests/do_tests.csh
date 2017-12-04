#!/bin/csh -f

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h

# Scriptpath should be $gen/testdir/unit_tests...right?
set gen = `cd ../..; pwd`
set v =  $gen/verilator/generator_z_tb

set tmpdir = /tmp/$$
mkdir $tmpdir

foreach test (`ls *.bsb`)
  set b = $test:r

  echo "Found test '$b'"
  set delay = `cat $test | awk 'BEGIN {d="0,0"} /DELAY/ {d=$NF} END {print d}'`
  echo "  Looks like delay should be '$delay'"

  echo "  Building bitstream using bsbuilder..."
  $gen/bitstream/bsbuilder/bsbuilder.py $test > $test:r.bsa

  set bsa = $scriptpath/${b}.bsa
  set in  = $scriptpath/${b}_input.raw

  # Note this output name is 'magic' and directs run.csh to do things :(
  # Maybe (FIXME)
  set cout = $tmpdir/${b}_CGRA_out.raw


  echo "cd $v"
  echo "./run.csh -hackmem -config $bsa -input $in -output $cout -delay $delay"
  (cd $v; ./run.csh -hackmem -config $bsa -input $in -output $cout -delay $delay )

  echo "FINAL COMPARE FOR SUMMARY"
  ./compare_images.csh $b $cout ${b}_output.raw

end
