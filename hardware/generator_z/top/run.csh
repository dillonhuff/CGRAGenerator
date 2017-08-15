# To generate fabric with memories, do -
# setenv CGRA_GEN_USE_MEM 1
# 
# @Caleb: For providing registers on all outputs of all SBs, do-
# setenv CGRA_GEN_ALL_REG 1

Genesis2.pl -parse -generate -top top -input\
  ../sb/sb.vp \
  ../cb/cb.vp \
  ../pe_tile/pe_tile.vp top.vp \
  \
  ../pe_new/pe/rtl/test_pe.svp \
  ../pe_new/pe/rtl/test_pe_comp.svp  \
  ../pe_new/pe/rtl/test_mult_add.svp \
  ../pe_new/pe/rtl/test_full_add.svp \
  ../pe_new/pe/rtl/test_lut.svp      \
  ../pe_new/pe/rtl/test_opt_reg.svp  \
  ../pe_tile_new/pe_tile_new.vp \
  \
  ../memory_tile/memory_tile.vp \
  ../memory_core/memory_core.vp \
  ../memory_core/mem.vp


