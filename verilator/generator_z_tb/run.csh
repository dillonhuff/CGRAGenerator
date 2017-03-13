#!/bin/csh

# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...

# Can I run a local test bench using remote v-sources?

# cleanup
if (-e obj_dir)     rm -rf obj_dir
if (-e counter.vcd) rm -f  counter.vcd
if ("$1" == "-clean") exit 0

# setup
setenv VERILATOR_ROOT /var/local/verilator-3.900
set path = (/var/local/verilator-3.900/bin $path)

# set testbench = tb_remote.cpp

set testbench = $1
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

# set gdir = /nobackup/steveri/github/CGRAGenerator/verilator/generator_zsr/top
  set gdir = /nobackup/steveri/github/CGRAGenerator/hardware/generator_z/top

pushd $gdir
  if (-e ./genesis_clean.cmd) ./genesis_clean.cmd
  # pwd; ls
  ./run.csh
popd

set vdir = $gdir/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe do something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

pushd $vdir >& /dev/null || echo Could not pushd $vdir
  set vfiles = (*.v)
popd >& /dev/null

set top = top
echo
echo verilator -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
  | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
echo
verilator -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top || exit -1

cat << eof

****************************************************
NOTE: Currently (3/13) runscript only works to here.
To get the rest to work, someone is gonna have to
write a working test bench "tb.cpp" :)
****************************************************


eof

# build C++ project
# make -j -C obj_dir/ -f Vcounter.mk Vcounter
echo
echo "# Build testbench"
echo make -j -C obj_dir/ -f V${top}.mk V${top}
make -j -C obj_dir/ -f V${top}.mk V${top}

echo
echo "# Run executable simulation"
# echo "obj_dir/Vcounter"
$ obj_dir/Vcounter
echo "obj_dir/V${top}"
obj_dir/V${top}


cat << eof

************************************************************************
NOTE: If you want to clean up after yourself you'll want to do this:

  ./run.csh -clean
  $gdir/genesis_clean.cmd

************************************************************************



eof
