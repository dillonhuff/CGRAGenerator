#!/bin/csh -f

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h
cd $scriptpath

# Script is maybe in $gen/bitstream/bsbuilder/testdir
set gen = `(cd ../../..; pwd)`
set v =  $gen/verilator/generator_z_tb



# Do them in order
set bmarks = (pointwise conv_2_1 conv_3_1 conv_bw)
set bmarks = (pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw)

# DB for delay, extracted below
#   - make build/pointwise.correct.txt DELAY=0,0   
#   - make build/conv_1_2.correct.txt  DELAY=1,0   
#   - make build/conv_2_1.correct.txt  DELAY=10,0  
#   - make build/conv_3_1.correct.txt  DELAY=20,0  
#   - make build/conv_bw.correct.txt   DELAY=130,0 

if (! -e tmpdir) mkdir tmpdir
if (-e tmpdir/test_results.log) rm tmpdir/test_results.log

foreach b ($bmarks)
  echo "------------------------------------------------------------------------"
  echo "TESTING $b"

  set bsa   = $scriptpath/tmpdir/$b.bsa
  set input = $scriptpath/examples/${b}_input.raw

  set delay = `grep ${b}.correct $0:t | sed 's/.*DELAY=\(.*\)/\1/'`
  # echo $b $delay

  # Note this output name is 'magic' and directs run.csh to do things :(
  set out = $scriptpath/tmpdir/${b}_CGRA_out.raw

  setenv SERPENT_HACK
  (cd $v; ./run.csh -hackmem -config $bsa -input $input -output $out -delay $delay )

  echo "FINAL COMPARE FOR SUMMARY"
  ./compare_images.csh $b | tee -a tmpdir/test_results.log

#   set map_json = examples/${b}_mapped.json
#   set map_dot  =   tmpdir/${b}_mapped.dot
#   set bsb      =   tmpdir/${b}.bsb
#   json2dot < $map_json > $map_dot
#   echo "../serpent.py $map_dot -o $bsb > tmpdir/$b.log.serpent"
#   ../serpent.py $map_dot -o $bsb > tmpdir/$b.log.serpent
#   cat $bsb
#   echo ''
end

grep RESULT tmpdir/test_results.log
