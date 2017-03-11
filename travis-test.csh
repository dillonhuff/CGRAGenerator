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

echo path=$path

# hardware/generator_z/top/run.csh
cd hardware/generator_z/top
./run.csh

pwd
ls -R
# find . -name top.\*
# cat ./genesis_verif/top.v

echo "Here is what I built"
echo "(it's supposed to look like an array of tiles)"
echo "(yes it's cryptic, deal with it):"
echo
egrep '^//t' ./genesis_verif/top.v | sed 's/^../  /'


# setenv GENESIS_HOME "$GENESIS/r#####/Genesis2Tools"
# set path=($GENESIS_HOME/bin $GENESIS_HOME/gui/bin $path)
# setenv PERL5LIB "$PERL5LIB":$GENESIS_HOME/PerlLibs/ExtrasForOldPerlDistributions

# echo GREP1
# grep '//t' ./genesis_verif/top.v
# 
# echo GREP3
# egrep '^[/][/]t' ./genesis_verif/top.v

