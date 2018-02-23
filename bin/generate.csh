#!/bin/csh -f

# Generate a CGRA using generator's default "run.csh" script.

# Script should be in CGROOT/bin

##############################################################################
# Not used in the new regime;
# safe to delete after we've finished the move.
setenv CGRA_GEN_ALL_REG 1
##############################################################################

# Not everyone has access to readlink -f
unset no_readlink
readlink -f >& /dev/null || set no_readlink
if ($?no_readlink) then
  set scriptpath = "$0"
  set scriptpath = $scriptpath:h
  if ("$scriptpath" == "$0") then
    set scriptpath = `pwd`
    set CGROOT = `cd $scriptpath:h; pwd`
  else
    set CGROOT = `cd $scriptpath/..; pwd`
  endif
else
  # set scriptpath = "$0" # No good if symlinks exist maybe
  set scriptpath = `readlink -f $0`
  set scriptpath = $scriptpath:h
endif


# # Script lives in $CGROOT/bin/$0
# # Therefore scriptpath is "$CGROOT/bin"
# # Therefore CGROOT is $scriptpath:h
# set CGROOT = $scriptpath:h


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
    set path = (. $path)
    
    if ($?VERBOSE) then
      echo "";
      echo "generator.csh: Generator run.csh looks like this:"; 
      cat run.csh | sed -n '/^Genesis/,/echo/p' | awk '{print "    " $0}';
      echo ""
      run.csh -v || exit -1

      ####################################################################
      # Use resulting top.v to print out information about what was built.

      $CGROOT/bin/find_cgra_info.csh genesis_verif/top.v || exit -1
      echo
    else
      set logfile = /tmp/generate_log.$$
      echo "Generator output to $logfile"
      run.csh >& $logfile || exit -1
    else
    endif

    # New cgra_info is proof that something happened
    # ls -l cgra_info.txt examples/*.txt
    if ($?VERBOSE) ls -l cgra_info.txt
