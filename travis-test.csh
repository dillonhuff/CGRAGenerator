#!/bin/csh -f

perl -f tmp.pl
perl --version

pwd
set whereami = `pwd`
echo $whereami

setenv GENESIS_HOME "$whereami/Genesis2Tools"
set path=(. $GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
# setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions
setenv PERL5LIB $GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions

# hardware/generator_z/top/run.csh
cd hardware/generator_z/top
./run.csh



# setenv GENESIS_HOME "$GENESIS/r#####/Genesis2Tools"
# set path=($GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
# setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions


