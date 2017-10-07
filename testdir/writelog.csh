#!/bin/csh -f


if ("$1" == "--help") then
cat << ' eof'
  Usage examples:
        testdir/writelog.csh log1 -init TEST SUMMARY
        testdir/writelog.csh log1 BEGIN `date`
        testdir/writelog.csh log1 -print
' eof'
  exit
endif

# This should totally work right?
set f = /tmp/$USER_$1
shift

if ("$1" == '-init') then
  if (-e $f) rm $f
  shift
endif

if ("$1" == '-print') then
  cat $f
endif

echo $* >> $f
