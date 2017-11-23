#!/bin/csh -f

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h
cd $scriptpath

# Script is maybe in $gen/bitstream/bsbuilder/testdir
set gen = `(cd ../../..; pwd)`
# echo $gen
alias json2dot $gen/testdir/graphcompare/json2dot.py


# Do them in order
set bmarks = (conv_1_2)
set bmarks = (pointwise conv_2_1 conv_3_1 conv_bw)
set bmarks = (pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw)



foreach b ($bmarks)
  echo "------------------------------------------------------------------------"
  echo "PROCESSING $b"

  set map_json = examples/${b}_mapped.json
  set map_dot  =   tmpdir/${b}_mapped.dot
  set bsb      =   tmpdir/${b}.bsb
  set bsa      =   tmpdir/${b}.bsa

  json2dot < $map_json > $map_dot

  echo "../serpent.py $map_dot -o $bsb > tmpdir/$b.log.serpent"
  ../serpent.py $map_dot -o $bsb > tmpdir/$b.log.serpent
  echo ''
  echo '========================================================================'
  echo "BSB FILE $bsb"
  echo '========================================================================'
  cat $bsb
  echo ''
  echo ''
  echo ''
  echo "../bsbuilder.py < $bsb > $bsa"
  ../bsbuilder.py < $bsb | sed -n '/FINAL PASS/,$p' | sed '1,2d' > $bsa
  echo ''
  echo '========================================================================'
  echo "BSA FILE $bsa"
  echo '========================================================================'
  cat $bsa
  echo ''
end
