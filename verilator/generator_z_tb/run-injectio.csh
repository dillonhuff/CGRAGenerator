#!/bin/csh -f

#------------------------------------------------------------------------
if ($1 == '--help') then
cat << eof
Input:  Bitstream 'foo.bs'  w/ bitstream-embedded I/O
               or 'foo.bsa' w/ comment-formatted I/O
Output: Bitstream w/ comment-formatted I/O ONLY

Examples:
  $0:t -v foo.bs  -o foo.bsio
  $0:t -v foo.bsa -o foo.bsio

eof
exit
endif

#------------------------------------------------------------------------
set VSWITCH = ''

if ($1 == '-v') set VSWITCH = "$1"
if ($1 == '-v') set VERBOSE
if ($1 == '-v') shift

if ($1 == '-q') set VSWITCH = "$1"
if ($1 == '-q') unset VERBOSE
if ($1 == '-q') shift

#------------------------------------------------------------------------
# Use decoder to replace input bitstream with
# an annotated bitstream that has embedded I/O comments

set config    = $1
set config_io = $3
if (-e $config_io) rm $config_io

# Use decoder to produce an annotated bitstream WITH I/O COMMENTS
# (Skip if config is already a 'bsa' file)
if ($config:e == 'bs') then
    # Must extract I/O info from bitstream

    set cgra_info = ../../hardware/generator_z/top/cgra_info.txt
    # pwd; ls -l $cgra_info

    set decoded = /tmp/$$

    # NOTE decode.py -v is messy and should be avoided unless you're trying to debug
    echo run-injectio: decode.py -cgra $cgra_info $config
    ../../bitstream/decoder/decode.py -cgra $cgra_info $config > $decoded

    # Returns a CLEAN bitstream with no bitstream-embedded I/O,
    # plus just two I/O comments at the end
    run-stripio.csh $VSWITCH $decoded -o $config_io
    /bin/rm $decoded

else
    set VERBOSE
    echo "Looks like config file already has embedded IO comments."
    echo "Test it for correctness, otherwise leave it unchanged."

    # Check config file for consistency/correctness (bsa_verify)
    grep . $config > /tmp/tmpconfig$$
    set cgra_info = ../../hardware/generator_z/top/cgra_info.txt
    ../../testdir/bsa_verify.csh -v /tmp/tmpconfig$$ -cgra $cgra_info

    # Pass config through unchanged, it's okay
    cp $config $config_io

endif

# if ($?VERBOSE) cat $config
cat $config

