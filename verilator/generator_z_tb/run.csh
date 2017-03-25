#!/bin/csh

if ($#argv == 0) then
  # Use these defaults
  set echo
  exec $0 top_tb.cpp \
    -config   ../../bitstream/tmpconfigPNR.dat        \
    -io       ../../bitstream/example3/PNRguys_io.xml \
    -input    io/gray_small.png                       \
    -nclocks  1M                                      \
    -output   /tmp/output.raw                         \
  || exit -1
  exit 0
endif  



echo

# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...(?)

# CLEANUP
foreach f (obj_dir counter.cvd tile_config.dat)
  if (-e $f) rm -rf $f
end

set gdir = ../../hardware/generator_z

set nclocks = ''

# Process command-line switches.
set GENERATE
while ($#argv)
  # echo "  found switch '$1'"
  if ("$1" == "-clean") then
    exit 0
  else if ("$1" == "-nogen") then
    unset GENERATE
  else if ("$1" == "-config") then
    shift
    set config = "$1"
  else if ("$1" == "-io") then
    shift
    set iofile = "$1"
  else if ("$1" == "-input") then
    shift
    set input = "$1"
  else if ("$1" == "-output") then
    shift
    set output = "$1"
  else if ("$1" == "-nclocks") then
    shift
    # will accept e.g. "1,000,031" or "41K" or "3M"
    set nclocks = `echo $1 | sed 's/,//g' | sed 's/K/000/' | sed 's/M/000000/'`
    set nclocks = "-nclocks $nclocks"
  else
    set testbench = "$1"
  endif
  shift argv
end

# set testbench = top_tb.cpp
# set testbench = $1
if (! -e "$testbench") then
  echo ""
  echo "ERROR: Testbench '$testbench' not found."
  echo ""
  echo "Maybe try one of these:"
  foreach f (*tb*.cpp)
    echo "  $0 $f"
  end
  exit -1
endif

# SETUP (not needed for travis)
# /home/travis/build/StanfordAHA/CGRAGenerator/platform/verilator
if (`hostname` == "kiwi") then
  setenv VERILATOR_ROOT /var/local/verilator-3.900
  set path = (/var/local/verilator-3.900/bin $path)
endif


if (! $?GENERATE) then
  echo "No generate!"
  goto NOGEN
endif

# GENERATE (not needed for travis)
# No need for GENERATE phase on travis because travis script does it already.
# OOPS no have to run generate twice or don't get in/out wires from mapper(!)
if (`hostname` == "kiwi") then


  # Build CGRA (again), using correct wire names this time
  # SHOULD NOT HAPPEN HERE should instead hack top.v later below

  pushd ../..
    # setenv SR_VERILATOR_INWIRES "$inwires"
    # setenv SR_VERILATOR_OUTWIRES "$outwires"
    # echo "inwires  = $SR_VERILATOR_INWIRES"
    # echo "outwires = $SR_VERILATOR_OUTWIRES"
    ./travis-test.csh
  popd

#   pushd $gdir/top
#     # setenv SR_VERILATOR_INWIRES "top->wire_0_0_BUS16_S1_T0 top->wire_0_0_BUS16_S1_T77"
#     # setenv SR_VERILATOR_OUTWIRES "top->wire_0_0_BUS16_S1_T99"
#     setenv SR_VERILATOR_INWIRES "$inwires"
#     setenv SR_VERILATOR_OUTWIRES "$outwires"
#     if (-e ./genesis_clean.cmd) ./genesis_clean.cmd
#     # pwd; ls
#     ./run.csh
#   popd
endif

NOGEN:

set vdir = $gdir/top/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe do something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

echo ""
echo '------------------------------------------------------------------------'
echo "BEGIN find input and output wires"
echo ""

  if ($?iofile) then
    echo "  USING WIRE NAMES FROM FILE '${iofile}':"
    grep wire_name $iofile
    echo ""

    # Why the devil didn't this work in travis!?
    #     set inwires = `set echo; sed -n /source/,/wire_name/p $iofile\
    #        | grep wire_name | sed 's/[<>]/ /g' | awk '{print $2}'`
    # 
    #     set outwires = `set echo; sed -n /sink/,/wire_name/p $iofile\
    #        | grep wire_name | sed 's/[<>]/ /g' | awk '{print $2}'`

    sed -n /source/,/wire_name/p $iofile > /tmp/tmp1
    grep wire_name /tmp/tmp1 | sed 's/[<>]/ /g' | awk '{print $2}' > /tmp/tmp2
    set inwires = `cat /tmp/tmp2`
    echo "  IN $inwires"
   
    sed -n /sink/,/wire_name/p $iofile > /tmp/tmp1
    grep wire_name /tmp/tmp1 | sed 's/[<>]/ /g' | awk '{print $2}' > /tmp/tmp2
    set outwires = `cat /tmp/tmp2`
    echo "  OUT $outwires"
    echo ""

  else
    echo "  USING DEFAULT WIRE NAMES"

    # add4 2x2 (tile_config.dat)
    # set inwires  = (wire_0_m1_BUS16_S0_T0 wire_m1_0_BUS16_S1_T0 wire_1_m1_BUS16_S0_T2 wire_2_0_BUS16_S3_T2)
    # set outwires = (wire_0_1_BUS16_S0_T4)

    # add4 4x4 (tile_config.dat)
    # set inwires  = (wire_0_m1_BUS16_S0_T0 wire_m1_0_BUS16_S1_T0 wire_1_m1_BUS16_S0_T2 wire_4_0_BUS16_S3_T2)
    # set outwires = (wire_0_1_BUS16_S0_T4)

    # mul2/nikhil-config (PNRCONFIG.dat maybe)
    set inwires  = (wire_0_0_BUS16_S1_T0)
    set outwires = (wire_1_0_BUS16_S1_T0)

    # ../../bitstream/tmpconfigPNR.dat
    set inwires  = (wire_0_0_BUS16_S1_T0)
    set outwires = (wire_1_2_BUS16_S3_T0)
  endif

  echo "  inwires  = $inwires"
  echo "  outwires = $outwires"
  echo ""

echo "END find input and output wires"

echo ""
echo '------------------------------------------------------------------------'
echo ""

echo "BEGIN vtop manipulation (won't be needed after we figure out io pads..."
echo ""

set vtop = $gdir/top/genesis_verif/top.v
cp $vtop /tmp/top.v.orig

# Substitute in a complete new custom top.v
# (We don't really do this these days...)
# The old switcharoo
if ($testbench == "tbsr1.cpp") then
  cp ./top_sr.v $vtop
endif

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


echo END vtop manipulation
echo '------------------------------------------------------------------------'


  set bsdir = ../../bitstream
  perl $bsdir/example3/gen_bitstream.pl $bsdir/example3/PNRguys_mapped.xml PNRCONFIG
  set config = PNRCONFIG.dat


if ($testbench == "top_tb.cpp") then
  if (! $?config) set config = $gdir/top_tb/tile_config.dat
  echo "Copy latest config file from $config..."
  # set echo
  # pwd
  # ls -l
  # ls -l $config
  if (! -e "$config") then
    echo
    echo "ERROR Config file does not exist!"
    exit -1
  endif       
  cp $config tile_config.dat
endif

# set vdir = $gdir/genesis_verif


pushd $vdir >& /dev/null || echo Could not pushd $vdir
  # set vfiles = (*.v *.sv)
  set vfiles = (*.v)
popd >& /dev/null

# So many warnings it wants to DIE!
set myswitches = '-Wno-fatal'

set top = top

echo
echo verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
  | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
echo


verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
  >& /tmp/verilator.out

set verilator_exit_status = $status

echo 'To get the flavor of all the warnings, just showing first 40 lines of output...'
head -n 40 /tmp/verilator.out

if ($verilator_exit_status != 0) exit -1


# cat << eof
# 
# ****************************************************
# NOTE: Currently (3/13) runscript only works to here.
# To get the rest to work, someone is gonna have to
# write a working test bench "tb.cpp" :)
# ****************************************************
# THEN: uncomment the got/bypass in run-travis.csh below.
# ****************************************************
# 
# eof

# echo NOT DOING: make -j -C obj_dir/ -f V${top}.mk V${top}
# echo NOT DOING: obj_dir/V${top}
# echo
# echo "Good-bye!"
# goto END




# build C++ project
# make -j -C obj_dir/ -f Vcounter.mk Vcounter
echo
echo "# Build testbench"
echo make -j -C obj_dir/ -f V${top}.mk V${top}
# make -j -C obj_dir/ -f V${top}.mk V${top} || exit -1
make \
  VM_USER_CFLAGS="-DINWIRE='top->$inwires' -DOUTWIRE='top->$outwires'" \
  -j -C obj_dir/ -f V${top}.mk V${top} || exit -1


# # set input = /tmp/input.raw
# set input = /tmp/gray_small.raw
# # stream io/gray_small.png $input
# # convert io/gray_small.png /tmp/input.raw
# io/myconvert.csh io/gray_small.png /tmp/gray_small.raw

# Prepare an input file

if (! $?input) then
  echo No input\; testbench will use random numbers for its check (i think)
  set in = ''
endif

if ($?input) then
  if ("$input:e" == "png") then
    # Convert to raw format
    echo
    io/myconvert.csh $input /tmp/input.raw
    echo
  else if ("$input:e" == "raw") then
    cp $input /tmp/input.raw
  else
    echo "ERROR Input file '$input' has invalid extension"
    exit -1
  endif

  set in = "-input /tmp/input.raw"

  # echo "First few lines of input file for comparison..."
  # # set cmd = "od -t x1 /tmp/input.raw"
  # # echo $cmd
  # # $cmd | head
  # set echo
  #   od -t x1 /tmp/input.raw | head
  # unset echo >& /dev/null

endif

set out = ''
if ($?output) then
  set out = "-output $output"
endif

echo
echo "# Run executable simulation"
# echo "obj_dir/Vcounter"
# obj_dir/Vcounter
# echo "obj_dir/V${top}"
# obj_dir/V${top}
# obj_dir/V${top} -config tile_config.dat -input ifile || exit -1
# obj_dir/V${top} -config tile_config.dat -input $input || exit -1
# obj_dir/V${top} -config tile_config.dat $in || exit -1

# set cmd = "obj_dir/V${top} -config tile_config.dat $in"

# echo $cmd
# $cmd || exit -1

#    -output /tmp/output.raw \

#    -config tile_config.dat \
#    -config ~ankitan/CGRA/CONFIG_FIN.dat
#    -config newconfig.dat\

set echo
  obj_dir/V${top} \
    -config $config \
    $in \
    $out \
    $nclocks \
    || exit -1
unset echo >& /dev/null

if ($?input) then
  echo
  set cmd = "od -t x1 /tmp/input.raw"
  set cmd = "od -t u1 /tmp/input.raw"
  echo $cmd; $cmd | head

  echo
  set cmd = "od -t u1 $output"
  echo $cmd; $cmd | head
endif




if (`hostname` == "kiwi") then
cat << eof

************************************************************************
NOTE: If you want to clean up after yourself you'll want to do this:

  ./run.csh -clean
  pushd $gdir/top; ./genesis_clean.cmd; popd

************************************************************************

eof
endif

# END:
