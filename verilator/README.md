Subdirectories:

example/
        Simple verilator example shows how to compile and run a testbench for a simple 8-bit counter.

example-remote/
        Similar to example/ except it builds a local testbench using remote verilog sources.

generator_zsb/
        My copy of generator_z where I can safely make changes without messing anyone up.

generator_zsb_tb/
        A testbench that uses the sources in generator_zsb.
        Current status: compiles verilog sources but does not yet succesfully link in a testbench.
        Also: have not yet written a testbench that I expect to work at all correctly.

