##############################################################################
# This makefile lets you run the generator from any remote directory,
# e.g. if the generator lives in
#
#   /nobackup/steveri/github/CGRA/hardware/generator_z/top/
#
# You can do this:
#
#    % mkdir /tmp/cgra; cd /tmp/cgra
#    % make gen -f /nobackup/steveri/github/CGRA/hardware/generator_z/top/Makefile
#    % ls /tmp/cgra
#        genesis_clean.cmd*  genesis_synth/         genesis_vlog.verif.vf
#        genesis.log         genesis_verif/         genesis_vlog.vf
#        genesis_raw/        genesis_vlog.synth.vf  genesis_work/

##############################################################################
# Basically, makefile does this:
#   set DESIGN_HOME = /nobackup/steveri/github/CGRA/hardware/generator_z/top
#   Genesis2.pl -parse -generate -top top -input <input files>

# Set DESIGN_HOME = directory where makefile lives
MAKEFILE_PATH:=$(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
DESIGN_HOME:=$(shell cd $(dir $(MAKEFILE_PATH)); pwd -P)
$(info $(DESIGN_HOME)/Makefile)

# Run the generator
gen:
	Genesis2.pl -parse -generate -top top -input \
	    $DESIGN_HOME/../sb/sb.vp \
	    $DESIGN_HOME/../cb/cb.vp \
	    $DESIGN_HOME/../pe/pe.vp \
	    $DESIGN_HOME/../memory_tile/mem_tile_sb_cb.vp \
	    $DESIGN_HOME/../memory/mem_tile.vp \
	    $DESIGN_HOME/../memory/mem.vp \
	    $DESIGN_HOME/top.vp
