#!/bin/csh -f

if ($#argv == 0) then
  echo 'Where should I put the bsa output files?'
  echo "Example: $0:t /tmp/build42/"
  exit -1
endif

if (! -d $1) then
  echo 'Where should I put the bsa output files?'
  echo "Example: $0:t /tmp/build42/"
  exit -1
endif
set tmp = $1

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h
cd $scriptpath

# Script is maybe in $gen/bitstream/bsbuilder/testdir
set gen = `(cd ../../..; pwd)`
alias json2dot $gen/testdir/graphcompare/json2dot.py


# Do benchmarks in order
set bmarks = (conv_1_2)
set bmarks = (pointwise conv_2_1 conv_3_1 conv_bw)
set bmarks = (pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw)

echo "set tmp = $tmp"
echo 'set gen = CGRAGenerator'
echo 'cd $gen/bitstream/bsbuilder'
echo 'alias json2dot $gen/testdir/graphcompare/json2dot.py'
echo ''

set t = '$tmp'
foreach b ($bmarks)
  set result = 'PASSED'
  echo "------------------------------------------------------------------------"
  echo "PROCESSING $b"

  set map_json = examples/${b}_mapped.json
  set map_dot  =   ${b}_mapped.dot
  set bsb      =   ${b}.bsb
  set bsa      =   ${b}.bsa

  echo "  json2dot < $map_json > $t/$map_dot"
  json2dot < $map_json > $tmp/$map_dot || exit -1

  echo "  cmp examples/$map_dot $t/$map_dot"
  cmp examples/$map_dot $tmp/$map_dot || set result = 'FAILED'
  echo ""


  echo "  ../serpent.py $t/$map_dot -o $t/$bsb > \$t/$b.log.serpent"
  ../serpent.py $tmp/$map_dot -o $tmp/$bsb > $tmp/$b.log.serpent || exit -1

  echo "  cmp examples/$bsb $tmp/$bsb"
  cmp examples/$bsb $tmp/$bsb || set result = 'FAILED'
  echo ""

  if ($?VERBOSE) then
    echo ''
    echo '========================================================================'
    echo "BSB FILE $bsb"
    echo '========================================================================'
    cat $bsb
    echo ''
    echo ''
    echo ''
  endif

  echo "  ../bsbuilder.py < $tmp/$bsb > $tmp/$bsa"
  ../bsbuilder.py < $tmp/$bsb | sed -n '/FINAL PASS/,$p' | sed '1,2d' > $tmp/$bsa || exit -1

  echo "  cmp examples/$bsa $tmp/$bsa"
  cmp examples/$bsa $tmp/$bsa || set result = 'FAILED'

  if ($?VERBOSE) then
    echo ''
    echo '========================================================================'
    echo "BSA FILE $bsa"
    echo '========================================================================'
    cat $bsa
    echo ''
  endif

  echo "TEST $b $result"
  echo ""

  if ($result == "FAILED") exit -1

end

# Clean up
# No! Not my job!
# /bin/rm -rf $tmp
