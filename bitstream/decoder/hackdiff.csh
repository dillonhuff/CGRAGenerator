#!/bin/csh -f

if ($#argv < 2) goto USAGE
goto MAIN

USAGE:
  echo    "Usage:"
  echo    "  $0:t foo.bs foo.bsa -cgra cgra_info.txt"
  echo -n "  # Decodes bitstream foo.bs and compares "
  echo    "result to annotated bitstream foo.bsa"
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
    case '-cgra':
      set cgra = "$2"; shift; breaksw
    default:
      expr "$1" : '-' > /dev/null && goto USAGE
      grep '#' "$1"   > /dev/null && set bsa="$1" || set bs="$1"
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
