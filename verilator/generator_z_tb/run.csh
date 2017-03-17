#!/bin/csh

# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...

# CLEANUP
# if (-e obj_dir)         rm -rf obj_dir
# if (-e counter.vcd)     rm -f  counter.vcd
# if (-e tile_config.dat) rm -f  tile_config.dat

foreach f (obj_dir counter.cvd tile_config.dat)
  if (-e $f) rm -rf $f
end

# set gdir = /nobackup/steveri/github/CGRAGenerator/verilator/generator_zsr/top
# set gdir = /nobackup/steveri/github/CGRAGenerator/hardware/generator_z/top
# set gdir = /nobackup/steveri/github/CGRAGenerator/hardware/generator_z
# set gdir = ../../hardware/generator_z/top
  set gdir = ../../hardware/generator_z

# Process command-line switches.
set GENERATE
while ($#argv)
  echo "  found switch '$1'"
  if ("$1" == "-clean") then
    exit 0
  else if ("$1" == "-nogen") then
    unset GENERATE
  else if ("$1" == "-config") then
    set config = "$1"
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
if (`hostname` == "kiwi") then
  pushd $gdir/top
    setenv SR_VERILATOR
    if (-e ./genesis_clean.cmd) ./genesis_clean.cmd
    # pwd; ls
    ./run.csh
  popd
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

set top = top

# The old switcharoo
if ($testbench == "tbsr1.cpp") then
  mv $gdir/top/genesis_verif/top.v ./top.v.old
  cp ./top_sr.v $gdir/top/genesis_verif/top.v
endif

if ($testbench == "top_tb.cpp") then
  if (! $?config) set config = $gdir/top_tb/tile_config.dat
  echo "Copy latest config file from $config..."
  if (! -e "$config") then
    echo
    echo "ERROR Config file does not exist!"
    exit
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

echo
echo verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
  | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
echo
verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top || exit -1

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
make -j -C obj_dir/ -f V${top}.mk V${top}

echo
echo "# Run executable simulation"
# echo "obj_dir/Vcounter"
# obj_dir/Vcounter
echo "obj_dir/V${top}"
obj_dir/V${top}

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
