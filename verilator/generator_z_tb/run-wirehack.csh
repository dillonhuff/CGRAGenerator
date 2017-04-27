#!/bin/csh -f

# Helper for run.csh; hacks wirenames into top.v for verilator i/o.
# Example: $0
#     -inwires  'wire_0_m1_BUS16_S0_T0 wire_m1_0_BUS16_S1_T0 wire_1_m1_BUS16_S0_T2 wire_4_0_BUS16_S3_T2'
#     -outwires 'wire_1_2_BUS16_S3_T0'
#     -vtop     '../../hardware/generator_z/top/genesis_verif/top.v'

while ($#argv)
  switch ("$1")

    case -vtop:
      set vtop = "$2"; shift; breaksw

    case -inwires:
      set inwires = "$2"; shift; breaksw

    case -outwires:
      set outwires = "$2"; shift; breaksw

    default:
      echo "ERROR Unknown switch '$1'"; exit -1
  endsw
  shift;
end

# Don't do it if it's already done!
unset already_done
egrep 'wire.*VERILATOR_PORT' $vtop > /dev/null && set already_done
if ($?already_done) then
  echo 'WARNING: wirehack appears to already be done, will not do again.'
  exit 0
endif

cp $vtop /tmp/top.v.orig

# // VERILATOR_PORT1,2,3...
# Build ports for verilator input and output signals
set i = 0; echo "  Adding ports for verilator inputs and outputs..."
foreach port ($inwires $outwires)
  sed "s|\(// VERILATOR_PORT$i\)|$port,               \1|" $vtop > /tmp/tmp
  echo "    $port..."; mv /tmp/tmp $vtop; @ i = $i + 1
end
echo
# diff /tmp/top.v.orig $vtop | sed 's/  */ /g' | sed 's/^/    /'

# // VERILATOR_IN1,2,3...
# Declare verilator input signals...
set i = 0; echo "  Adding verilator input declarations..."
foreach wirename ($inwires)
  sed "s|\(// VERILATOR_IN$i\)|input  [15:0] $wirename; \1|" $vtop > /tmp/tmp
  echo "    $wirename..."; mv /tmp/tmp $vtop; @ i = $i + 1
end
echo
# diff /tmp/top.v.orig $vtop | sed 's/  */ /g' | sed 's/^/    /'

# // VERILATOR_OUT1,2,3...
# Declare verilator output signals...
set i = 0; echo "  Adding verilator output declarations..."
foreach wirename ($outwires)
  sed "s|\(// VERILATOR_OUT$i\)|output [15:0]  $wirename; \1|" $vtop > /tmp/tmp
  echo "    $wirename..."; mv /tmp/tmp $vtop; @ i = $i + 1
end
echo
# diff /tmp/top.v.orig $vtop | sed 's/  */ /g' | sed 's/^/    /'

# Disconnect "input" wires from internal net (and route to ports instead)
echo "  Disconnecting input wires from internal net..."
foreach inwire ($inwires)
  (egrep "out.*$inwire" $vtop > /dev/null)\
    || echo "    Wire not found in internal net of top.v"
  sed "s/\(.*[.]out.*\)$inwire/\1/" $vtop > /tmp/tmp
  # diff $vtop /tmp/tmp | egrep '^[<>]' | sed 's/  */ /g' | sed 's/^/    /'
  echo "    $inwire..."; mv /tmp/tmp $vtop
end
echo

# Show what we did
echo Changes to top.v:  ; echo
  diff /tmp/top.v.orig $vtop | sed 's/  */ /g' | sed 's/^/    /' > /tmp/tmp

  cat /tmp/tmp | egrep '^ *<' | egrep 'PORT'; echo "    ---"
  cat /tmp/tmp | egrep '^ *>' | egrep 'PORT'; echo; echo

  cat /tmp/tmp | egrep '^ *<' | egrep 'IN|OUT'; echo "    ---"
  cat /tmp/tmp | egrep '^ *>' | egrep 'IN|OUT'; echo; echo

  cat /tmp/tmp | egrep '^ *<' | egrep -v 'VERILATOR'; echo "    ---"
  cat /tmp/tmp | egrep '^ *>' | egrep -v 'VERILATOR'; echo; echo



# Suggestion for how to see all changes in context...
echo To see all changes in context, try:
echo "  diff --side-by-side -W 100 /tmp/top.v.orig $vtop | less"
echo
