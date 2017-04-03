#!/bin/csh -f

# This travis-script helper sets up the Genesis2 run environment,
# then uses Genesis2 to build the CGRA.  Note this is only used
# for the CGRAGenerator travis script, not CGRAFlow
#
# FIXME/TODO: use Genesis2 from github instead maybe...

perl --version | head -1

##############################################################################
# Trying a thang


##############################################################################
# Set up to run Genesis2
# TODO/FIXME project: maybe bring in genesis from github instead of using local copy?


# Used to do this...
# OLD
# set whereami = `pwd`
# # echo $whereami
# setenv GENESIS_HOME "$whereami/Genesis2Tools"


# Alternatively could maybe do this...
# If running locally, use existing Genesis2 install...
# if (hostname == kiwi) setenv GENESIS_HOME /cad/genesis2/r11879/Genesis2Tools/

# Clone Genesis2 from github
# NEW
# pushd /tmp
git clone https://github.com/StanfordVLSI/Genesis2.git /tmp/Genesis2
setenv GENESIS_HOME /tmp/Genesis2/Genesis2Tools
#
# huh.
# Compress::Raw::Zlib object version 2.060 does not match bootstrap parameter 2.033 at /tmp/Genesis2/Genesis2Tools/PerlLibs/ExtrasForOldPerlDistributions/Compress/Raw/Zlib.pm line 98.
/bin/rm -rf /tmp/Genesis2/Genesis2Tools/PerlLibs/ExtrasForOldPerlDistributions/Compress
#
# popd



set path=(. $GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
# setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions
setenv PERL5LIB $GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions

# echo path=$path




##############################################################################
# SR_VERILATOR tells generator to do verilator-specific optimizations
# TODO/FIXME I think this is no longer used; take it out and see if it still works.
# 
setenv SR_VERILATOR
# printenv | sort


##############################################################################
# Run the generator, but first clean up from prior runs.  Die if gen error.

cd hardware/generator_z/top

if (-e ./genesis_clean.cmd) ./genesis_clean.cmd

which Genesis2.pl
./run.csh || exit -1




##############################################################################
# Use resulting top.v to print out information about what was built.

set top=./genesis_verif/top.v
if (! -e $top) then
  echo "Cannot find TOP '$top'"
  exit -1
endif

# <tile_type>#<tile_loc>#<tile_section>
#    ====================
#    t0#0_0#0    t0#0_1#0    
#    t0#1_0#0    t0#1_1#0    

echo ''
echo '-------------------------------------------------------------------'
echo "Here is what I built (it's supposed to look like an array of tiles)."
echo ""
echo "    --------------------"
# egrep '^//t' $top  | sed 's/^../    /' | sed 's/\( *\)\(.*\) */\1|\2|/'

egrep '^//t' $top  | sed 's/^../    /'
# egrep '^//t' $top  | sed 's/    / | /g' | sed 's/^../    /'

# egrep '^//t' $top  |  sed 's/^..//' |\
# awk '\
#   {\
#     row = sprintf("| %s ", $1);\
#     for (i=2; i<=NF; i++) {\
#       row = row sprintf("| %s ", $1);\
#     }\
#     printf "    "; for (i=0; i<length(row); i++) printf "-"; print ""\
#     print "    " row "|";\
#   }\
# END { printf "    "; for (i=0; i<length(row); i++) printf "-"; print "" }'

echo "    --------------------"
echo ''
echo 'Each tile is designated as <tile_type>#<tile_loc(x,y)>#<tile_section>'
echo 'E.g. current default in top.vp calls stamp_pattern('top') where top is defined as'
echo ''
echo '   $tile_pattern {'p1'} = "t0_1_1";'
echo '   $tile_pattern {'top'} = "p1_2_2";'
echo ''
echo ' resulting in a 2x2 grid of "t0" tiles, defined as follows'
echo ''
echo '    $tile_config->{ 't0' } = {'
echo '         type => 'pe_tile_new','
echo '         sides => $sides,'
echo '         is_bidi => 0,'
echo '         bus_config => $bus_config,'
echo '         cb_connections => $cb_connections,'
echo '         has_constant => 1,'
echo '         tile_height => 1,'
echo '         tile_width => 1,'
echo '         reg_inputs => 0,'
echo '         reg_out => 0, '
echo '         use_add => 1,'
echo '         bool_inps => 1,'
echo '         use_shift => 1,'
echo '         mult_mode => 1,'
echo '         sb_fs => $sb_fs,'
echo '         all_segments_for_all_tiles => $all_segments_for_all_tiles'
echo '   };'
echo '-------------------------------------------------------------------'
echo ''


# setenv GENESIS_HOME "$GENESIS/r#####/Genesis2Tools"
# set path=($GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
# setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions

# echo GREP1
# grep '//t' ./genesis_verif/top.v
# 
# echo GREP3
# egrep '^[/][/]t' ./genesis_verif/top.v

