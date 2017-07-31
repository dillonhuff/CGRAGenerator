#!/bin/csh -f

if ("$1" == "--help") then
  echo "Usage: $0 foo.bs foo.bsa"
  echo ""
  echo "-> decodes bitstream foo.bs and compares"
  echo "-> result to annotated bitstream foo.bsa"
  exit
endif

set scripthome = $0:h
if ("$scripthome" == "$0") scripthome = .

# From bsa must remove wire-0-connect lines of the form
# ... connect wire 0 (in_0_BUS16_0_4) to sb_wire_in_1_BUS16_3_4
# ... connect wire 0 (in_1_BUS16_1_3) to sb_wire_out_1_BUS16_3_3
# ... connect wire 0 (sb_wire_in_1_BUS16_3_4) to out_1_BUS16_2_4
# but not
# ... connect wire 0 (in_BUS16_S0_T0) to b
egrep -v 'connect wire 0 .*to [soi]' $2 > /tmp/tmp$$.bsa

$scripthome/decode.py $1 \
  | sed '/Summary/,$d' \
  > /tmp/tmp$$.bsd

set echo
diff /tmp/tmp$$.{bsa,bsd}
