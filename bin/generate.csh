#!/bin/csh -f

# Generate a CGRA using generator's default "run.csh" script.

# Script should be in CGROOT/bin

set scriptpath = "$0"
set scriptpath = $scriptpath:h
if ("$scriptpath" == "$0") set scriptpath = `pwd`
set CGROOT = $scriptpath:h

# Clean it up
pushd $CGROOT >& /dev/null
  set CGROOT = `pwd`; 
popd >& /dev/null

# echo "scriptpath=$scriptpath"
# echo "CGROOT=$CGROOT"
# exit

##############################################################################
# Set up to run Genesis2; installs genesis2 if necessary (in /tmp !)

source $CGROOT/bin/genesis2_setup.csh
# echo path=$path
which Genesis2.pl

##############################################################################
# Run the generator, but first clean up from prior runs.  Die if gen error.

# cd hardware/generator_z/top
cd $CGROOT/hardware/generator_z/top
    if (-e ./genesis_clean.cmd) ./genesis_clean.cmd

    # if ($?OLDMEM) then
    #   echo "OLDMEM REGIME"
    #   set run = run_oldmemtile.csh
    # else
    #   echo "NEWMEM REGIME"
    #   set run = run.csh
    # endif

    # NOTE THIS IS THE RUN.CSH IN HARDWARE/GENERATOR_Z
    set run = run.csh
    echo ""; echo "Generator $run looks like this:"; cat $run; echo ""

    ./$run || exit -1


    ##############################################################################
    # Use resulting top.v to print out information about what was built.

#     # set top= ./genesis_verif/top.v
#     # set top = `pwd`/genesis_verif/top.v
#     set top = $CGROOT/genesis_verif/top.v
#     $CGROOT/bin/find_cgra_info.csh $top || exit -1
    $CGROOT/bin/find_cgra_info.csh .//genesis_verif/top.v || exit -1

    echo
    ls -l cgra_info.txt examples/*.txt
    echo


