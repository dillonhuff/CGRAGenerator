[![linux build status][1]][2]
[1]: https://travis-ci.org/StanfordAHA/CGRAGenerator.svg?branch=master
[2]: https://travis-ci.org/StanfordAHA/CGRAGenerator

# CGRA Coarse-Grain Reconfigurable Architecture Generator

See doc/srnotes.txt for Steve's notes on organization and such
(still TBD as of this writing).

Quick guide to repository contents as of 03/2017:
* doc/ => documentation (still TBD as of this writing)
* Genesis2Tools => for building the project and running it with e.g. travis
* hardware/generator_z => latest instantiation of the generator
* hardware/generator_z/to => go here to run the generator
* verilator => verilator experiments


TODO
* should replace Genesis2Tools with a build from within the travis script maybe


OBSOLETE: I think maybe these are obsolete?
* hardware/pe => Artem's PE generator (right?)
* hardware/sb => Ankita's switchbox generator (yes?)
* sr-proposal/ => Steve's proposal for a unified framework for the generators

