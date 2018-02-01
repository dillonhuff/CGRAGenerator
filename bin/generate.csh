#!/bin/csh -f

set echo

# Generate a CGRA using generator's default "run.csh" script.

# Script should be in CGROOT/bin

##############################################################################
# Not used in the new regime;
# safe to delete after we've finished the move.
setenv CGRA_GEN_ALL_REG 1
##############################################################################

# Find out where we live
# set scriptpath = "$0" # No good if symlinks exist maybe
set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h

# if ("$scriptpath" == "$0") then
#   set scriptpath = `pwd`
#   set CGROOT = `cd $scriptpath:h; pwd`
# else
#   set CGROOT = `cd $scriptpath/..; pwd`
# endif

# Script lives in $CGROOT/bin/$0
# Therefore scriptpath is "$CGROOT/bin"
# Therefore CGROOT is $scriptpath:h
set CGROOT = $scriptpath:h


# echo "I think CGRAGenerator is here: $CGROOT"; exit

##############################################################################
# Set up to run Genesis2; installs genesis2 if necessary (in /tmp !)

unset VERBOSE
if ("$1" == "-v") then
  # echo verbose
  set VERBOSE
else if ("$1" == "-q") then
  # echo quiet
  unset VERBOSE
endif

source $CGROOT/bin/genesis2_setup.csh
if ($?VERBOSE) then
  echo -n "generate.csh: "; which Genesis2.pl
endif

##############################################################################
# Run the generator, but first clean up from prior runs.  Die if gen error.

# cd hardware/generator_z/top
cd $CGROOT/hardware/generator_z/top
    if (-e ./genesis_clean.cmd) ./genesis_clean.cmd

    # NOTE THIS IS THE RUN.CSH IN HARDWARE/GENERATOR_Z
    set run = run.csh
    
    if ($?VERBOSE) then
      echo "";
      echo "generator.csh: Generator $run looks like this:"; 
      cat $run | awk '{print "    " $0}';
      echo ""
    endif

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
    if ($?VERBOSE) ls -l cgra_info.txt
