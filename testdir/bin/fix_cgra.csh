#!/bin/csh -f

# Fix errors in cgra_info.txt
#    "<src sel=0>" => "<src sel='0'>"
#    "<src sel=1>" => "<src sel='1'>"

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h

# Scriptpath should be $gen/testdir/bin   ...right?

set top = ../../hardware/generator_z/top

cd $top

# grep 'sel=[01]' cgra_info.txt

cat cgra_info.txt \
  | sed "s/sel=0/sel='0'/" \
  | sed "s/sel=1/sel='1'/" \
  > /tmp/tmp

# diff cgra_info.txt /tmp/tmp
cp /tmp/tmp cgra_info.txt

