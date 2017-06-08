# This very simple makefile is designed to be used as follows:
#
#    cd <thisdirectory>
#    make gen
#
# OR one of these
#    make gen CGRA_GEN_USE_MEM=1
#    make gen CGRA_GEN_ALL_REG=1
#    make gen CGRA_GEN_ALL_REG=1 CGRA_GEN_USE_MEM=1
# 
# It's based on Nikhil's "run.csh" which presently looks like this:
# 
# ########################################################################
# # To generate fabric with memories, do -
# # setenv CGRA_GEN_USE_MEM 1
# # 
# # @Caleb: For providing registers on all outputs of all SBs, do-
# # setenv CGRA_GEN_ALL_REG 1
# 
# Genesis2.pl -parse -generate -top top -input\
#   ../sb/sb.vp \
#   ../cb/cb.vp \
#   ../pe_tile/pe_tile.vp top.vp \
#   \
#   ../pe_new/pe/rtl/test_pe.svp \
#   ../pe_new/pe/rtl/test_mult_add.svp \
#   ../pe_new/pe/rtl/test_full_add.svp \
#   ../pe_new/pe/rtl/test_lut.svp      \
#   ../pe_new/pe/rtl/test_opt_reg.svp  \
#   ../pe_tile_new/pe_tile_new.vp \
#   \
#   ../memory_tile/memory_tile.vp \
#   ../memory_core/memory_core.vp \
#   ../memory_core/mem.vp

TOP := top

ifndef CGRA_GEN_USE_MEM
    usemem := echo not using CGRA_GEN_USE_MEM
else
    usemem := export CGRA_GEN_USE_MEM=1
endif

ifndef CGRA_GEN_ALL_REG
    allreg := echo not using CGRA_GEN_ALL_REG
else
    allreg := export CGRA_GEN_ALL_REG=1
endif

help:
	@echo '    ' make gen
	@echo '    ' make gen CGRA_GEN_USE_MEM=1
	@echo '    ' make gen CGRA_GEN_ALL_REG=1
	@echo '    ' make gen CGRA_GEN_ALL_REG=1 CGRA_GEN_USE_MEM=1


gen:
	$(usemem); \
	$(allreg); \
	./run.csh

test:
	$(usemem); $(allreg); ./test.csh

# # cgra_info.txt: 
# gen:
# 	Genesis2.pl -parse -generate -top $(TOP) -input \
# 	    ../sb/sb.vp \
# 	    ../cb/cb.vp \
# 	    ../pe_tile/pe_tile.vp \
# 	    \
# 	    ../pe_new/pe/rtl/test_pe.svp \
# 	    ../pe_new/pe/rtl/test_mult_add.svp \
# 	    ../pe_new/pe/rtl/test_full_add.svp \
# 	    ../pe_new/pe/rtl/test_lut.svp      \
# 	    ../pe_new/pe/rtl/test_opt_reg.svp  \
# 	    ../pe_tile_new/pe_tile_new.vp \
# 	    \
# 	    ../memory_tile/memory_tile.vp \
# 	    ../memory_core/memory_core.vp \
# 	    ../memory_core/mem.vp \
# 	    \
# 	    top.vp
# 




# See Makefile.fancy for fancier stuff.
