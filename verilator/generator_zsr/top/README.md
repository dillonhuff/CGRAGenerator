To run the generator:

    ./run.csh

To clean up after running the generator, use the "genesis_clean"
script, which is created every time you execute "run.csh":

    ./genesis_clean.cmd

The optional makefile lets you run the generator from any remote
directory without messing up the generator sources.  For example,
if the generator lives in

   /nobackup/steveri/github/CGRA/hardware/generator_z/top

you can do this:

   % mkdir /tmp/cgra; cd /tmp/cgra
   % make gen -f /nobackup/steveri/github/CGRA/hardware/generator_z/top/Makefile
   % ls /tmp/cgra
       genesis_clean.cmd*  genesis_synth/         genesis_vlog.verif.vf
       genesis.log         genesis_verif/         genesis_vlog.vf
       genesis_raw/        genesis_vlog.synth.vf  genesis_work/
