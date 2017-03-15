#!/bin/csh -f

# goto TMP
# exit

perl -f tmp.pl
perl --version

pwd
set whereami = `pwd`
echo $whereami

setenv GENESIS_HOME "$whereami/Genesis2Tools"
set path=(. $GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
# setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions
setenv PERL5LIB $GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions

echo path=$path

setenv SR_VERILATOR
# printenv | sort

# hardware/generator_z/top/run.csh
cd hardware/generator_z/top
if (-e ./genesis_clean.cmd) ./genesis_clean.cmd
./run.csh || exit -1

pwd
ls -R

TMP:

set top=./genesis_verif/top.v
# cat $top

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

