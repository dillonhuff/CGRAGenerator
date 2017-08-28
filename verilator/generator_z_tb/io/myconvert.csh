#!/bin/csh -f

# http://stackoverflow.com/questions/29120768/imagemagick-convert-png-16-bit-to-raw

# Usage: myconvert gray.png gray.raw

set input = $1
set output = $2

# You so stoopid
set tmpdir = /tmp/myconvert.$$; mkdir $tmpdir
set tmp = $tmpdir/tmp.pgm

convert $input -depth 8 pgm:$tmp
# head -2 $tmp | tail -1

set nbytes = `head -2 $tmp | tail -1 | awk '{print $1 * $2}'`
# echo $nbytes

tail -c $nbytes $tmp > $output

# To check the result
(head -3 $tmp; cat $output) > $tmpdir/verify.pgm

echo "Converted $input to $output...to verify result, do:"
echo "  gwenview $tmpdir/verify.pgm"
