#!/bin/csh -f

# Generate a CGRA using generator's default "run.csh" script.

# Script should be in CGROOT/bin

if (! $?CGRA_GEN_ALL_REG) echo CGRA_GEN_ALL_REG NOT SET
if ($?CGRA_GEN_ALL_REG) echo CGRA_GEN_ALL_REG = $?CGRA_GEN_ALL_REG
setenv CGRA_GEN_ALL_REG 1
echo $?CGRA_GEN_ALL_REG


set scriptpath = "$0"
set scriptpath = $scriptpath:h
if ("$scriptpath" == "$0") then
  set scriptpath = `pwd`
  set CGROOT = `cd $scriptpath:h; pwd`
else
  set CGROOT = `cd $scriptpath/..; pwd`
endif

##############################################################################
# Set up to run Genesis2; installs genesis2 if necessary (in /tmp !)

set VERBOSE
if ("$1" == "-q") then
  # echo quiet
  unset VERBOSE
else
  # echo verbose
  set VERBOSE
endif

source $CGROOT/bin/genesis2_setup.csh
if ($?VERBOSE) which Genesis2.pl

##############################################################################
# Run the generator, but first clean up from prior runs.  Die if gen error.

# cd hardware/generator_z/top
cd $CGROOT/hardware/generator_z/top
    if (-e ./genesis_clean.cmd) ./genesis_clean.cmd

    # NOTE THIS IS THE RUN.CSH IN HARDWARE/GENERATOR_Z
    set run = run.csh
    
    echo ""; echo "Generator $run looks like this:"; cat $run | awk '{print "    " $0}'; echo ""

    if (! $?VERBOSE) then
      set logfile = /tmp/generate_log.$$
      echo "Generator output to $logfile"
      ./$run >& $logfile || exit -1
    else
      ./$run || exit -1

      ####################################################################
      # Use resulting top.v to print out information about what was built.

      $CGROOT/bin/find_cgra_info.csh .//genesis_verif/top.v || exit -1
      echo
    endif

    # New cgra_info is proof that something happened
    # ls -l cgra_info.txt examples/*.txt
    ls -l cgra_info.txt
