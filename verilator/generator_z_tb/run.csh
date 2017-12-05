#!/bin/csh -f

set VERBOSE

# Build a tmp space for intermediate files
set tmpdir = deleteme
if (! -e $tmpdir) then
  unset ERR
  mkdir $tmpdir || set ERR
  if ($?ERR) then
    echo "Could not make dir '$tmpdir'"
    exit 99
  endif
endif


# ALWAYS BE USING MEMORY
setenv CGRA_GEN_USE_MEM 1


# setenv CGRA_GEN_ALL_REG 1

# Travis flow (CGRAFlow/.travis.yml)
#  travis script calls "generate.csh" to do the initial generate
#  travis script calls PNR to build map, io info from generated cgra_info.txt
#  builds the full parrot

# Travis flow (CGRAGenerator/.travis.yml)
#  travis script calls "generate.csh" to do the initial generate
#  travis script calls run.csh using pre-built bitstream w/embedded io info
#  builds small parrot

# Local flow (test):
#  run.csh calls generate.csh to do the initial generate
#  run.csh uses pre-built io, map files in bitstream/example3 to build config file
# builds small parrot

# DEFAULTS
set testbench = top_tb.cpp
set GENERATE  = "-gen"

# Default configuration bitstream
set config   = ../../bitstream/examples/940/pw.bs

# Sometimes may need to know what branch we are in
git branch | grep '^*' > $tmpdir/tmp
set branch = `sed 's/^..//' $tmpdir/tmp`

# In travis, 'git branch' returns something like
#   "* (HEAD detached at 09a4672)"
#   "  master"

# Travis branch comes up as 'detached' :(
#   * (HEAD detached at a220e19)
#     master
if (`expr "$branch" : ".*detached"`) then
  set branch = `git branch | grep -v '^*' | awk '{print $1}'`
endif
echo "run.csh: I think we are in branch '$branch'"

if ("$branch" == "srdev") set config = ../../bitstream/examples/pwv2.bs
if ("$branch" == "avdev") set config = ../../bitstream/examples/pwv2.bs

set DELAY = '0,0'

set input     = io/gray_small.png
set output    = $tmpdir/output.raw
set nclocks   = "1M"
unset tracefile

if ($#argv == 1) then
  if ("$argv[1]" == '--help') then
    echo "Usage:"
    echo "    $0 <textbench.cpp> -q [-gen | -nogen]"
    echo "        -usemem -allreg"
    echo "        -config <config_filename.bs>"
    echo "        -input   <input_filename.png>"
    echo "        -output <output_filename.raw>"
    echo "        -delay <ncy_delay_in>,<ncy_delay_out>"
    echo "       [-trace   <trace_filename.vcd>]"
    echo "        -nclocks <max_ncycles e.g. '100K' or '5M' or '3576602'>"
    echo
    echo "Defaults:"
    echo "    $0 top_tb.cpp \"
    echo "       $GENERATE         \"
    echo "       -config  $config \"
    echo "       -input   $input  \"
    echo "       -output  $output \"
    echo "        -delay $DELAY"
    if ($?tracefile) then
      echo "       -trace $tracefile \"
    endif
    echo "       -nclocks  $nclocks                                          \"
    echo
    exit 0
  endif
endif

echo config = $config 2

# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...(?)

# CLEANUP
foreach f (obj_dir counter.cvd tile_config.dat)
  if (-e $f) rm -rf $f
end

# I GUESS 4x4 vs. 8x8 is implied by presence or absence of CGRA_GEN_USE_MEM (!!???)
# I can't find anything else that does it :(

unset HACKMEM

while ($#argv)
  # echo "Found switch '$1'"
  switch ("$1")

    case '-hackmem':
      echo "WARNING USING TEMPORARY TERRIBLE HACKMEM"
      echo "WARNING USING TEMPORARY TERRIBLE HACKMEM"
      echo "WARNING USING TEMPORARY TERRIBLE HACKMEM"
      set HACKMEM = 1
      breaksw

    case '-clean':
      exit 0;

    case '-q':
      unset VERBOSE; breaksw;
    case '-v':
      set VERBOSE; breaksw;



    # DEPRECATED SWITCHES
    case '-4x4':
    case '-8x8':
      echo "WARNING Switch '$1' no longer valid"; breaksw

    case -usemem:
    case -newmem:
      echo "WARNING Switch '$1' no longer valid"; breaksw
      # setenv CGRA_GEN_USE_MEM 1; # always set
      breaksw;

#     case -egregious_conv21_hack:
#       set EGREGIOUS_CONV21_HACK
#       breaksw

    case '-gen':
      set GENERATE = '-gen'; breaksw;

    case '-nogen':
      set GENERATE = '-nogen'; breaksw;

    case '-config':
      set config = "$2"; shift; breaksw

    # "bitstream" is an alias for "config"
    case '-bitstream':
      set config = "$2"; shift; breaksw

    case -io:
      echo "WARNING -io no longer supported; this switch will be ignored."
      set iofile = "$2"; shift; breaksw

    case -input:
      set input = "$2"; shift; breaksw

    case -output:
      set output = "$2"; shift; breaksw

    case -delay:
      set DELAY = "$2"; shift; breaksw

    case -trace:
      set tracefile = "$2"; shift; breaksw

    case -nclocks:
      # will accept e.g. "1,000,031" or "41K" or "3M"
      set nclocks = $2;
      shift; breaksw

    case -allreg:
      setenv CGRA_GEN_ALL_REG 1; breaksw

    # Unused / undocumented for now
    case -oldmem:
      echo "WARNING Switch '$1' no longer valid"; breaksw
      unsetenv CGRA_GEN_USE_MEM
      unsetenv CGRA_GEN_ALL_REG
      breaksw

    default:
      if (`expr "$1" : "-"`) then
        echo "ERROR: Unknown switch '$1'"
        exec $0 --help
        exit -1
      endif
      set testbench = "$1";
  endsw
  shift;
end

if (! -e "$testbench") then
  echo ""
  echo "ERROR: Testbench '$testbench' not found."
  echo ""
  echo "Maybe try one of these:"
  foreach f (*tb*.cpp)
    echo "  $0 $f"
  end
  exit -1
endif


##############################################################################
##############################################################################
##############################################################################
# # Here's a weird hack, okay...srdev travis only gets to run with pwv2 config
# 
# # # Set config conditionally depending on current branch
# # # bsview = v0, master = v1, srdev = v2
# # 
# if ("$branch" == "srdev" || "$branch" == "avdev") then
#   if ("$config" == "../../bitstream/examples/pwv1.bs") then
#     echo
#     echo '  SRDEV TRAVIS hack'
#     echo '  SRDEV TRAVIS hack'
#     echo '  SRDEV TRAVIS hack'
#     echo '  pwv1 was requested; using pwv2 instead...'
#     echo ''
#     set config = ../../bitstream/examples/pwv2.bs
#   endif
# endif
# 
##############################################################################
##############################################################################
##############################################################################





if ($?VERBOSE) then
  # Backslashes line up better when printed...
  echo "Running with the following switches:"
  echo "$0 top_tb.cpp \"
  echo "   $GENERATE                    \"
  echo "   -config   $config   \"
  #echo "   -io       $iofile   \"
  echo "   -input    $input  \"
  echo "   -output   $output    \"
  echo "   -delay   $DELAY    \"
  if ($?tracefile) then
    echo "   -trace $tracefile \"
  endif
  echo "   -nclocks  $nclocks                 \"
endif

if (! -e $config) then
  echo "run.csh: ERROR Cannot find config file '$config'"
  exit -1
endif

# Turn nclocks into an integer.
set nclocks = `echo $nclocks | sed 's/,//g' | sed 's/K/000/' | sed 's/M/000000/'`
set nclocks = "-nclocks $nclocks"

# which verilator

# By default, we assume generate has already been done.
# Otherwise, user must set "-gen" to make it happen here.

echo
# if (! $?GENERATE) then
if ("$GENERATE" == "-nogen") then
  echo "No generate!"

else
  # Build CGRA 
  if ($?VERBOSE) echo "Building CGRA because you asked for it with '-gen'..."

  if ($?VERBOSE) then
    ../../bin/generate.csh -v || exit -1
  else
    ../../bin/generate.csh -q || exit -1
  endif

endif



#------------------------------------------------------------------------
# BSB HACK
echo BSB $config
unset bsb_hack

if ("$config" == "/nobackup/steveri/github/CGRAGenerator/bitstream/bsbuilder/pw2_bsb.bs") set bsb_hack

if ($?bsb_hack) then
  echo ""
  echo "BSB HACK"
  echo "BSB HACK"
  echo "BSB HACK"
  echo "bsb hack because config = pw2_bsb.bs"
  echo ""
endif
if ($?VERBOSE) echo run.csh line 337 ish
#------------------------------------------------------------------------


########################################################################
# Now process bitstream file $config


if (! $?bsb_hack) then

  # Verify that embedded IO info exists (skip if using bsbuilder)

  unset embedded_io
  grep "FFFFFFFF" $config > /dev/null && set embedded_io
  if (! $?embedded_io) then
    echo "ERROR run.csh: Bitstream appears NOT to have embedded I/O information."
    echo "ERROR run.csh: We don't support that no more."
    exit -1
  else if ($?VERBOSE) then
    echo
    echo "Bitstream appears to have embedded i/o information (as it should)."
    echo "Will strip out IO hack from '$config'"
    echo
  endif

endif


# Nowadays decoder needs cgra_info to work correctly
set cgra_info = ../../hardware/generator_z/top/cgra_info.txt
# pwd; ls -l $cgra_info

set decoded = $tmpdir/{$config:t}.decoded
if (-e $decoded) rm $decoded

# Why?  Leftover debug stuff I guess?
# # Possible locations for pnr stuff
# ls ../../.. | grep -i smt


# echo \
# ../../bitstream/decoder/decode.py -v -cgra $cgra_info $config
# ../../bitstream/decoder/decode.py -v -cgra $cgra_info $config > $decoded
# 
# NOTE -v is messy and should be avoided unless you're trying to debg things.
echo           run.csh: decode.py -cgra $cgra_info $config
set VERBOSE
if ($?VERBOSE) then
  ../../bitstream/decoder/decode.py -cgra $cgra_info $config | tee $decoded || exit -1
else
  ../../bitstream/decoder/decode.py -cgra $cgra_info $config > $decoded || exit -1
endif
unset VERBOSE


# Show IO info derived from bitstream
if ($?VERBOSE) then
  echo; sed -n '/O Summary/,$p' $decoded; echo
else
  echo; sed -n '/O Summary/,$p' $decoded | grep PUT | sort; echo
endif


# Clean bitstream (strip out comments and hacked-in IO info)
set newbs = $decoded.bs
if (-e $newbs) rm $newbs

##############################################################################
unset LUT_HACK
if ($?LUT_HACK) then
  echo
  echo '  LUT hack'
  echo '  LUT hack'
  echo '  LUT hack'
  echo '  Temporarily stripping out LUT code...'
  echo ''
  set lut_hack_en = "^FF00.... 00000080"
  set lut_hack_ld = "^0000.... ........"

  cat $decoded \
    | egrep -v "$lut_hack_en" \
    | egrep -v "$lut_hack_ld" \
    > $tmpdir/lut_hack

  echo diff $decoded $tmpdir/lut_hack
  diff $decoded $tmpdir/lut_hack | grep -v d
  echo ""

  mv $tmpdir/lut_hack $decoded 
endif
##############################################################################



# grep -v HACK $decoded | sed -n '/TILE/,$p' | awk '/^[0-9A-F]/{print $1 " " $2}' > $newbs
cat $decoded \
  | egrep -v '^F000.... FFFFFFFF' \
  | egrep -v '^F100.... FFFFFFFF' \
  | egrep -v '^FF00.... 000000F0' \
  | egrep -v '^FF00.... 000000FF' \
  > $tmpdir/decode2


# This is small and SHOULD NOT BE OPTIONAL!
# Meh.  Now it's optional.
if ($?VERBOSE) then
  echo diff $decoded $tmpdir/decode2
  diff $decoded $tmpdir/decode2 | grep -v d
endif


if (! $?bsb_hack) then

  # Another useful test
  set ndiff = `diff $decoded $tmpdir/decode2 | grep -v d | wc -l`
  if ("$ndiff" == "5") then
    if ($?VERBOSE) echo "run.csh: Five lines of diff.  That's good!"
  else
    echo "ERROR run.csh: Looks like we messed up the IO"
    exit -1
  endif

endif


# Strip out comments from decoded bitstream
cat $tmpdir/decode2\
  | awk '/^[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]/{print $1 " " $2}' \
  > $newbs

set config = $newbs



# This is what we're looking for:
#     "# INPUT  tile  0 (0,0) / out_s1t0 / wire_0_0_BUS16_S1_T0"
#     "# INPUT  tile  0 (0,0) / out_s1t0 / wire_0_0_BUS16_S1_T1"
#     "# OUTPUT tile  2 (2,0) /  in_s3t0 / wire_1_0_BUS16_S1_T0"
set inwires = `egrep '^# INPUT' $decoded | awk '{print $NF}'`
set outwires = `egrep '^# OUTPUT' $decoded | awk '{print $NF}'`

if ($?bsb_hack) then

  set inwires  = wire_0_m1_BUS16_S0_T0
  set outwires = wire_0_0_BUS16_S2_T0;

  echo ""
  echo "BSB HACK"
  echo "BSB HACK"
  echo "BSB HACK"
  echo "For now only works with (input,output)='$inwires,$outwires'"
  echo ""

endif

if ($?VERBOSE) then
    echo ""
    echo '------------------------------------------------------------------------'
    echo "BEGIN find input and output wires"
    echo ""
    echo "  USING I/O WIRE NAMES DERIVED FROM BITSTREAM"
    echo ""
    echo "  inwires  = $inwires"
    echo "  outwires = $outwires"
    echo
    echo "END find input and output wires"
    echo ""
    echo '------------------------------------------------------------------------'
endif


set vdir = ../../hardware/generator_z/top/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe build it by doing something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

# echo "BEGIN top.v manipulation (won't be needed after we figure out io pads)..."
#     echo
#     echo "Inserting wirenames into verilog top module '$vdir/top.v'..."
#     echo


    echo "run.csh: Inserting IO wirenames into verilog top module '$vdir/top.v'..."
    ./run-wirehack.csh \
        -inwires "$inwires" \
        -outwires "$outwires" \
        -vtop "$vdir/top.v" > $tmpdir/wirehack.log

    if ($?VERBOSE) cat $tmpdir/wirehack.log

# echo END top.v manipulation

echo ''
echo '------------------------------------------------------------------------'
echo "Building the verilator simulator executable..."

  # (Temporary (I hope)) SRAM hack(s)

  echo
  echo '  SRAM hack'
  echo '  SRAM hack'
  echo '  SRAM hack'
  if ($?CGRA_GEN_USE_MEM) then
     cp ./sram_stub.v $vdir/sram_512w_16b.v
     ls -l $vdir/sram*
#  else
#     echo "NOT USING MEMORY.  TURNING OFF HACKMEM.  It causes trouble."
#     unset HACKMEM
  endif

  # Temporary wen/ren hacks.  
  if ($?HACKMEM) then
    # In memory_core_unq1.v, change:
    #   assign wen = (`$ENABLE_CHAIN`)?chain_wen_in:xwen;
    # To:
    #   assign wen = WENHACK

    # ls -l $vdir
    mv $vdir/memory_core_unq1.v $tmpdir/memory_core_unq1.v.orig
    cat $tmpdir/memory_core_unq1.v.orig \
      | sed 's/^assign wen = .*/assign wen = WENHACK;/' \
      > $vdir/memory_core_unq1.v

    # No longer doing:
    #  | sed 's/assign int_ren = .*/assign int_ren = 1;/' \
    #  | sed 's/assign int_wen = .*/assign int_wen = 1;/' \
    #  | sed 's/assign wen = .*/assign wen = 1;/' \

    echo
    echo '------------------------------------------------------------------------'
    echo WARNING REWROTE memory_core_unq1.v BECAUSE TEMPORARY TERRIBLE MEMHACK
    echo WARNING REWROTE memory_core_unq1.v BECAUSE TEMPORARY TERRIBLE MEMHACK
    echo WARNING REWROTE memory_core_unq1.v BECAUSE TEMPORARY TERRIBLE MEMHACK
    echo diff $tmpdir/memory_core_unq1.v.orig $vdir/memory_core_unq1.v
    diff $tmpdir/memory_core_unq1.v.orig $vdir/memory_core_unq1.v
    echo '------------------------------------------------------------------------'
    echo
    echo

  endif

echo ''
echo '------------------------------------------------------------------------'
echo "run.csh: Build the simulator..."

  # Build the necessary switches

  # Gather the verilog files for verilator command line
  pushd $vdir >& /dev/null
    # set vfiles = (*.v *.sv)
    set vfiles = (*.v)
  popd >& /dev/null

  # So many warnings it wants to DIE!
  set myswitches = '-Wno-fatal'
  set top        = 'top'

  # Add trace switch if trace requested
  if ($?tracefile) set myswitches = "$myswitches --trace"

  # Note default trace_filename in top_tb.cpp is "top_tb.vcd"

  # Run verilator to build the simulator.

  # build C++ project

  echo
  echo verilator -Wall $myswitches --cc --exe $testbench \
    -y $vdir $vfiles --top-module $top \
    | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
  echo

  verilator $myswitches -Wall $myswitches --cc --exe $testbench \
    -y $vdir $vfiles --top-module $top \
    >& $tmpdir/verilator.out

  set verilator_exit_status = $status

  if ($?VERBOSE) then
    echo "%Warning1 Ignoring warnings about unoptimizable circularities in switchbox wires (see SR for explainer)."
    echo '%Warning2 To get the flavor of all the warnings, just showing first 40 lines of output.'
    echo '%Warning3 See $tmpdir/verilator.out for full log.'
    echo
    cat $tmpdir/verilator.out \
      | awk -f ./run-verilator-warning-filter.awk \
      | head -n 40 
  else
    echo "See $tmpdir/verilator.out for full log of verilator warnings."
  endif

  if ($verilator_exit_status != 0) exit -1

  echo
  echo "run.csh: Build the testbench..."

  if ($?VERBOSE) then
    echo
    echo "make \"
    echo "  VM_USER_CFLAGS='-DINWIRE=top->$inwires -DOUTWIRE=top->$outwires' \"
    echo "  -j -C obj_dir/ -f V$top.mk V$top"
  endif

  echo
  echo "TODO/FIXME this only works if there is exactly ONE each INWIRE and OUTWIRE\!\!"
  echo "make V$top -DINWIRE='top->$inwires' -DOUTWIRE='top->$outwires'"
  make \
    VM_USER_CFLAGS="-DINWIRE='top->$inwires' -DOUTWIRE='top->$outwires'" \
    -j -C obj_dir/ -f V$top.mk V$top \
    >& $tmpdir/make_vtop.log \
    || set ERROR

  if ($?ERROR) then
    cat $tmpdir/make_vtop.log; exit -1
  endif

  if ($?VERBOSE) then
    cat $tmpdir/make_vtop.log; echo
  endif


echo '------------------------------------------------------------------------'
echo "run.csh: Run the simulator..."
echo ''
if ($?VERBOSE) echo '  First prepare input and output files...'

  # Prepare an input file
  #   if no input file requested => use random numbers generated internally
  #   if input file has extension ".png" => convert to raw
  #   if input file has extension ".raw" => use input file as is

  if (! $?input) then
    echo No input\; testbench will use random numbers for its check (i think)
    set in = ''

  else if ("$input:e" == "png") then
    # Convert to raw format
    if ($?VERBOSE) then
      echo "  Converting input file '$input' to '.raw'..."
      echo "  io/myconvert.csh $input $tmpdir/input.raw"
      echo
      echo -n "  "
      io/myconvert.csh $input $tmpdir/input.raw
    else
      io/myconvert.csh -q $input $tmpdir/input.raw
    endif
    set in = "-input $tmpdir/input.raw"

  else if ("$input:e" == "raw") then
    if ($?VERBOSE) then
      echo "Using raw input from '$input'..."
      echo cp $input $tmpdir/input.raw
    endif
    cp $input $tmpdir/input.raw
    set in = "-input $tmpdir/input.raw"

  else
    echo "ERROR run.csh: Input file '$input' has invalid extension"
    exit -1

  endif

  # echo "First few lines of input file for comparison..."
  # od -t x1 $tmpdir/input.raw | head

  # If no output requested, simulator will not create an output file.
  set out = ''
  if ($?output) then
      set out = "-output $output"
  endif

  set delay = "-delay $DELAY"

  # If no trace requested, simulator will not create a waveform file.
  set trace = ''
  if ($?tracefile) then
    set trace = "-trace $tracefile"
  endif

  echo
  echo "run.csh: Run executable simulation"

  # 00020: Two times 19 = 38  *PASS*
  # 00021: Two times 22 = 44  *PASS*
  # 00022: Two times 23 = 46  *PASS*
  # ...
  # 00058: Two times 31 = 62  *PASS*
  # 00059: Two times 29 = 58  *PASS*

  # For 'quiet' execution, use these two filters to limit output;
  # Otherwise just cat everything to stdout
  if (! $?VERBOSE) then
    set quietfilter = (grep -v "scanned config")
    set qf2 = (grep -v "^000[23456789].*Two times")
  else
    set quietfilter = (cat)
    set qf2         = (cat)
  endif

  if ($?VERBOSE) then
    echo
    echo "BITSTREAM '$config':"
    cat $config
  endif

  echo
  echo "run.csh: TIME NOW: `date`"
  echo "run.csh: V$top -output $output:t"

  # OOPS big parrot won't work in travis if output gets filtered...
  # Must have the printf every 10K cycles
  set quietfilter = (cat)
  set qf2         = (cat)


  if ($?VERBOSE) set echo
    obj_dir/V$top \
      -config $config \
      $in \
      $out \
      $delay \
      $trace \
      $nclocks \
      | tee $tmpdir/run.log.$$ \
      | $quietfilter:q | $qf2:q \
      || exit -1
  unset echo >& /dev/null
  echo -n " TIME NOW: "; date

  unset FAIL
  grep FAIL $tmpdir/run.log.$$ && set FAIL


  echo
  echo "# Show output vs. input; output should be 2x input for most common testbench"

  if ($?input) then
    echo
    ls -l $tmpdir/input.raw $output

    if ("$output:t" == "conv_1_2_CGRA_out.raw") then
      # echo; set cmd = "od -t u1 $output"; echo $cmd; $cmd | head

      echo; echo "FOUND conv_1_2 output; converting to 9x9..."
      ./bin/conv_1_2_convert < $output > $tmpdir/tmp.raw
      mv $tmpdir/tmp.raw $output
      ls -l $output

      # echo; set cmd = "od -t u1 $output"; echo $cmd; $cmd | head

    endif

    if ("$output:t" == "conv_bw_CGRA_out.raw") then
      echo; echo "FOUND conv_bw output; converting to 62x62..."
      ./bin/crop31 < $output > $tmpdir/tmp.raw
      mv $tmpdir/tmp.raw $output
      ls -l $output
    endif

    echo
    set cmd = "od -t x1 $tmpdir/input.raw"
    set cmd = "od -t u1 $tmpdir/input.raw"
  # echo $cmd; $cmd | head
    echo $cmd; $cmd | head; echo ...; $cmd | tail -n 3

    echo
    set cmd = "od -t u1 $output"
  # echo $cmd; $cmd | head
    echo $cmd; $cmd | head; echo ...; $cmd | tail -n 3
  endif


  if ($?FAIL) exit -1

# Tell how to clean up (not necessary for travis VM of course)
# if (`hostname` == "kiwi") then
set pwd = `pwd`
if (! `expr $pwd : /home/travis`) then
  set gbuild = ../../hardware/generator_z/top
  cat << eof

************************************************************************
NOTE: If you want to clean up after yourself you'll want to do this:

  ./run.csh -clean
  pushd $gbuild; ./genesis_clean.cmd; popd

************************************************************************

eof
endif
