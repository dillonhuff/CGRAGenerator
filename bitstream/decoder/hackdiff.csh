#!/bin/csh -f

if ($#argv < 2) goto USAGE
goto MAIN

USAGE:
  echo "Usage: $0 -bs foo.bs -bsa foo.bsa -cgra cgra_info.txt"
  echo ""
  echo "-> decodes bitstream foo.bs and compares"
  echo "-> result to annotated bitstream foo.bsa"
  exit

MAIN:
set scripthome = $0:h
if ("$scripthome" == "$0") set scripthome = .

set bs   = 'None'
set bsa  = 'None'
set cgra = 'None'
while ($#argv)
  # echo "Found switch '$1'"
  switch ("$1")
    case '-bs':
      set bs = "$2"; shift; breaksw
    case '-bsa':
      set bsa = "$2"; shift; breaksw
    case '-cgra':
      set cgra = "$2"; shift; breaksw
  endsw
  shift;
end

foreach f ($bs $bsa $cgra)
  test -f $f || goto USAGE
end

# From bsa must remove wire-0-connect lines of the form
# ... connect wire 0 (in_0_BUS16_0_4) to sb_wire_in_1_BUS16_3_4
# ... connect wire 0 (in_1_BUS16_1_3) to sb_wire_out_1_BUS16_3_3
# ... connect wire 0 (sb_wire_in_1_BUS16_3_4) to out_1_BUS16_2_4
# but not
# ... connect wire 0 (in_BUS16_S0_T0) to b
egrep -v 'connect wire 0 .*to [soi]' $bsa > /tmp/tmp$$.bsa

$scripthome/decode.py $bs -cgra $cgra \
  | sed '/Summary/,$d' \
  > /tmp/tmp$$.bsd

set echo
diff /tmp/tmp$$.{bsa,bsd}
