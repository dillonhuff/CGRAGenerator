#!/bin/csh -f

set tmp = /tmp/displaydot$$.dot

set echo
dot $1 -Tpdf > $tmp
xpdf $tmp

