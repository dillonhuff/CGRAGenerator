#!/bin/csh -f

set whereami = `pwd`

# This travis-script helper brings in Genesis2 from the github
# then uses Genesis2 to build the CGRA.

perl --version | head -1

##############################################################################
# Set up to run Genesis2

# Alternatively could maybe do this...
# If running locally, use existing Genesis2 install...
# if (hostname == kiwi) setenv GENESIS_HOME /cad/genesis2/r11879/Genesis2Tools/

# Clone Genesis2 from github

if (! -d /tmp/Genesis2/) then
  git clone https://github.com/StanfordVLSI/Genesis2.git /tmp/Genesis2
endif
setenv GENESIS_HOME /tmp/Genesis2/Genesis2Tools

# huh.  seems to break if don't remove distrib Zlib?
# Compress::Raw::Zlib object version 2.060 does not match bootstrap parameter 2.033 at /tmp/Genesis2/Genesis2Tools/PerlLibs/ExtrasForOldPerlDistributions/Compress/Raw/Zlib.pm line 98.
/bin/rm -rf /tmp/Genesis2/Genesis2Tools/PerlLibs/ExtrasForOldPerlDistributions/Compress
#
# popd

set path=(. $GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
if (! $?PERL5LIB) then
  setenv PERL5LIB $GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions
else
  setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions
endif

# echo path=$path

##############################################################################
# SR_VERILATOR tells generator to do verilator-specific optimizations
# TODO/FIXME I think this is no longer used; take it out and see if it still works.
# 
# setenv SR_VERILATOR
# printenv | sort


##############################################################################
# Run the generator, but first clean up from prior runs.  Die if gen error.

cd hardware/generator_z/top
if (-e ./genesis_clean.cmd) ./genesis_clean.cmd

echo "WARNING! TEMPORARY HACK TO USE OLD MEM TILES!"

# TEMPORARY HACK FOR BAD MEMTILE
set run = run.csh
set run = run_oldmemtile.csh
if ($?NEWMEMTILE) then
  echo "WARNING Found environment variable NEWMEMTILE"
  set run = run.csh
endif


which Genesis2.pl
echo ""
echo "$run looks like this:"
cat $run
echo ""
./$run || exit -1


##############################################################################
# Use resulting top.v to print out information about what was built.

# set top= ./genesis_verif/top.v
set top = `pwd`/genesis_verif/top.v
$whereami/bin/find_cgra_info.csh $top || exit -1


