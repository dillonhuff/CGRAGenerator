[![linux build status][1]][2]

# CGRA Coarse-Grain Reconfigurable Architecture Generator


[1]: https://travis-ci.org/StanfordAHA/CGRAGenerator.svg?branch=master
[2]: https://travis-ci.org/StanfordAHA/CGRAGenerator

See doc/srnotes.txt for Steve's notes on organization and such
(still TBD as of this writing).

Quick guide to repository contents as of 01/2017:
* doc/ => documentation (still TBD as of this writing)
* hardware/pe => Artem's PE generator (right?)
* hardware/sb => Ankita's switchbox generator (yes?)
* sr-proposal/ => Steve's proposal for a unified framework for the generators

For a quick example of how Steve's proposal works, you can do this
(assumes github repository is mapped to CGRA/ and that the "make" and
"Genesis2.pl" commands are both working and available in your path):

<pre>
  % cd CGRA/sr-proposal

  % ls */test_pe.svp
    tst/test_pe.svp

  % make gen GENESIS_TOP=test_pe

  % ls */test_pe.sv
    genesis_verif/test_pe.sv

  % ./genesis_clean.cmd
</pre>

What did this do?  Well, if everything worked correctly...
* the "make" command used the information in CGRA/Makefile to find and
  process the Genesis file tst/test_pe.svp, producing the verilog file
  genesis_verif/test_pe.sv
* the "genesis_clean.cmd" cleaned everything up and put it back the
  way it was before you started the example.

