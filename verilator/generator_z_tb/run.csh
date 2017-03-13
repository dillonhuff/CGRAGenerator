#!/bin/csh

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


set gdir = /nobackup/steveri/github/CGRAGenerator/verilator/generator_zsr/top
pushd $gdir
  if (-e ./genesis_clean.cmd) ./genesis_clean.cmd
  pwd
  ls

  ./run.csh
pushd $gdir

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
echo verilator -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top | fold -w
verilator -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top || exit -1

# build C++ project
# make -j -C obj_dir/ -f Vcounter.mk Vcounter
make -j -C obj_dir/ -f V${top}.mk V${top}

echo "now run executable simulation"
# echo "obj_dir/Vcounter"
$ obj_dir/Vcounter
echo "obj_dir/V${top}"
obj_dir/V${top}
