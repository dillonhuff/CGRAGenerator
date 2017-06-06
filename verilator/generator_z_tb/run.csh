#!/bin/csh -f

# Travis flow (CGRAFlow/.travis.yml)
#  travis script calls "travis-test" to do the initial generate
#  travis script calls PNR to build map, io info from generated cgra_info.txt
#  builds the full parrot

# Travis flow (CGRAGenerator/.travis.yml)
#  travis script calls "travis-test" to do the initial generate
#  travis script calls run.csh using pre-built bitstream w/embedded io info
#  builds small parrot

# Local flow (test):
#  run.csh calls travis-test to do the initial generate
#  run.csh uses pre-built io, map files in bitstream/example3 to build config file
# builds small parrot

# DEFAULTS
set testbench = top_tb.cpp
set GENERATE  = "-gen"
# set config    = ../../bitstream/examples/calebscript.bs
# set config    = ../../bitstream/examples/cd.bs

# New memtile regime swaps r,c tile addresses HA
set config    = ../../bitstream/examples/cd-swizzled.bs
set input     = io/gray_small.png
set output    = /tmp/output.raw
set nclocks   = "1M"
unset tracefile

if ($#argv == 1) then
  if ($argv[1] == '--help') then
    echo "Usage:"
    echo "    $0 <textbench.cpp> [-gen]"
    echo "        -config     <config_filename>"
    echo "        -input      <input_filename>"
    echo "        -output     <output_filename>"
    echo "       [-buildtrace <trace_filename>]"
    echo "        -nclocks <max_ncycles e.g. '100K' or '5M' or '3576602'>"
    echo
    echo "Defaults:"
    echo "    $0 top_tb.cpp \"
    echo "       $GENERATE         \"
    echo "       -config   $config \"
    echo "       -input    $input  \"
    echo "       -output   $output \"
    if ($?tracefile) then
      echo "       -buildtrace $tracefile \"
    endif
    echo "       -nclocks  $nclocks                                          \"
    echo
    exit 0
  endif
endif


# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...(?)

# CLEANUP
foreach f (obj_dir counter.cvd tile_config.dat)
  if (-e $f) rm -rf $f
end

while ($#argv)
  # echo "Found switch '$1'"
  switch ("$1")

    case '-clean':
      exit 0;

    case '-gen':
      set GENERATE = '-gen'; breaksw;

    case '-nogen':
      # echo "'nogen' is the default already"; breaksw;
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

    case -buildtrace:
      set tracefile = "$2"; shift; breaksw

    case -nclocks:
      # will accept e.g. "1,000,031" or "41K" or "3M"
      set nclocks = $2;
      shift; breaksw

    default:
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

unset embedded_io
grep "FFFFFFFF" $config > /dev/null && set embedded_io
if (! $?embedded_io) then
  echo "Bitstream appears NOT to have embedded I/O information."
  echo "We don't support that no more."
  exit -1
endif

echo; echo "Bitstream appears to have embedded i/o information (as it should).  Decoded:"

set decoded = /tmp/{$config:t}.decoded
# ../../bitstream/decoder/decode.py $config > $decoded
# New memtile regime swaps r,c tile addresses HA
# ../../bitstream/decoder/decode.py -newmem $config > $decoded



# Show IO info derived from bitstream
echo; sed -n '/O Summary/,$p' $decoded; echo

# Clean bitstream (strip out hacked-in IO info)
set newbs = /tmp/bs.txt
echo "Will strip out IO hack from '$config'"
echo "to create clean bitstream '$newbs'"
echo
grep -v HACK $decoded | sed -n '/TILE/,$p' | awk '/^[0-9A-F]/{print $1 " " $2}' > $newbs
diff $config $newbs | grep -v d
set config = $newbs
echo

# Backslashes line up better when printed...
echo "Running with the following switches:"
echo "$0 top_tb.cpp \"
echo "   $GENERATE                    \"
echo "   -config   $config   \"
#echo "   -io       $iofile   \"
echo "   -input    $input  \"
echo "   -output   $output    \"
if ($?tracefile) then
  echo "   -buildtrace $tracefile \"
endif
echo "   -nclocks  $nclocks                 \"

# Turn nclocks into an integer.
set nclocks = `echo $nclocks | sed 's/,//g' | sed 's/K/000/' | sed 's/M/000000/'`
set nclocks = "-nclocks $nclocks"


which verilator


# By default, we assume generate has already been done.
# Otherwise, user must set "-gen" to make it happen here.

echo
# if (! $?GENERATE) then
if ("$GENERATE" == "-nogen") then
  echo "No generate!"

else
  # Build CGRA 
  echo "Building CGRA because you asked for it with '-gen'..."
  pushd ../..
    ./travis-test.csh
  popd

endif

# If config files has an xml extension, use Ankita's perl script
# to turn it into a .dat/.txt configuration bitstream

echo ""
if ("$config:e" == "xml") then
  echo "Generating config bitstream 'tmpconfig.dat' from xml file '$config'..."
  perl ../../bitstream/example3/gen_bitstream.pl $config tmpconfig
  set config = tmpconfig.dat
else
  echo "Use existing config bitstream '$config'..."
  echo
endif

echo "BITSTREAM:"
cat $config


echo ""
echo '------------------------------------------------------------------------'
echo "BEGIN find input and output wires"
echo ""

    echo "  USING I/O WIRE NAMES DERIVED FROM BITSTREAM"
    echo ""

    # This is what we're looking for:
    #     "# INPUT  tile  0 (0,0) / out_s1t0 / wire_0_0_BUS16_S1_T0"
    #     "# INPUT  tile  0 (0,0) / out_s1t0 / wire_0_0_BUS16_S1_T1"
    #     "# OUTPUT tile  2 (2,0) /  in_s3t0 / wire_1_0_BUS16_S1_T0"
   
    set inwires = `egrep '^# INPUT' $decoded | awk '{print $NF}'`
    echo "  IN  $inwires"

    set outwires = `egrep '^# OUTPUT' $decoded | awk '{print $NF}'`
    echo "  OUT $outwires"

    echo
    echo "  inwires  = $inwires"
    echo "  outwires = $outwires"
    echo

echo "END find input and output wires"

echo ""
echo '------------------------------------------------------------------------'
echo ""

set vdir = ../../hardware/generator_z/top/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe build it by doing something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

echo "BEGIN top.v manipulation (won't be needed after we figure out io pads)..."
    echo
    echo "Inserting wirenames into verilog top module '$vdir/top.v'..."
    echo
    ./run-wirehack.csh \
        -inwires "$inwires" \
        -outwires "$outwires" \
        -vtop "$vdir/top.v"

echo END top.v manipulation

echo ''
echo '------------------------------------------------------------------------'
echo ''
echo "Building the verilator simulator executable..."

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

  # Run verilator to build the simulator.

  echo
  echo verilator -Wall $myswitches --cc --exe $testbench -y $vdir $vfiles --top-module $top \
    | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
  echo

  verilator $myswitches -Wall $myswitches --cc --exe $testbench -y $vdir $vfiles --top-module $top \
    >& /tmp/verilator.out

  set verilator_exit_status = $status

  echo "%Warning1 Ignoring warnings about unoptimizable circularities in switchbox wires (see SR for explainer)."
  echo '%Warning2 To get the flavor of all the warnings, just showing first 40 lines of output.'
  echo '%Warning3 See /tmp/verilator.out for full log.'
  echo
  cat /tmp/verilator.out \
    | awk -f ./run-verilator-warning-filter.awk \
    | head -n 40 

  if ($verilator_exit_status != 0) exit -1

echo ''
echo '------------------------------------------------------------------------'
echo ''
echo "Build the simulator..."

  # build C++ project

  echo
  echo "# Build testbench"

  echo
  echo "make \"
  echo "  VM_USER_CFLAGS='-DINWIRE=top->$inwires -DOUTWIRE=top->$outwires' \"
  echo "  -j -C obj_dir/ -f V$top.mk V$top"
  echo
  echo "TODO/FIXME this only works if there is exactly ONE each INWIRE and OUTWIRE\!\!"
  echo
  make \
    VM_USER_CFLAGS="-DINWIRE='top->$inwires' -DOUTWIRE='top->$outwires'" \
    -j -C obj_dir/ -f V$top.mk V$top || exit -1

echo ''
echo '------------------------------------------------------------------------'
echo ''
echo "Run the simulator..."
echo ''
echo '  First prepare input and output files...'

  # Prepare an input file
  #   if no input file requested => use random numbers generated internally
  #   if input file has extension ".png" => convert to raw
  #   if input file has extension ".raw" => use input file as is

  if (! $?input) then
    echo No input\; testbench will use random numbers for its check (i think)
    set in = ''

  else if ("$input:e" == "png") then
    # Convert to raw format
    echo "  Converting input file '$input' to '.raw'..."
    echo "  io/myconvert.csh $input /tmp/input.raw"
    echo
    echo -n "  "
    io/myconvert.csh $input /tmp/input.raw
    set in = "-input /tmp/input.raw"

  else if ("$input:e" == "raw") then
    echo "Using raw input from '$input'..."
    echo cp $input /tmp/input.raw
    cp $input /tmp/input.raw
    set in = "-input /tmp/input.raw"

  else
    echo "ERROR Input file '$input' has invalid extension"
    exit -1

  endif

  # echo "First few lines of input file for comparison..."
  # od -t x1 /tmp/input.raw | head

  # If no output requested, simulator will not create an output file.
  set out = ''
  if ($?output) then
      set out = "-output $output"
  endif

  # If no trace requested, simulator will not create a waveform file.
  set trace = ''
  if ($?tracefile) then
    set trace = "-buildtrace $tracefile"
  endif

  echo
  echo "# Run executable simulation"

  set echo
    obj_dir/V$top \
      -config $config \
      $in \
      $out \
      $trace \
      $nclocks \
      | tee /tmp/run.log.$$ \
      || exit -1
  unset echo >& /dev/null

  grep FAIL /tmp/run.log.$$ && exit -1


  echo
  echo "# Show output vs. input; output should be 2x input for most common testbench"

  if ($?input) then
    echo
    set cmd = "od -t x1 /tmp/input.raw"
    set cmd = "od -t u1 /tmp/input.raw"
    echo $cmd; $cmd | head

    echo
    set cmd = "od -t u1 $output"
    echo $cmd; $cmd | head
  endif


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
