#!/bin/bash
# To generate fabric with memories, do -
# setenv CGRA_GEN_USE_MEM 1
# 
# @Caleb: For providing registers on all outputs of all SBs, do-
# setenv CGRA_GEN_ALL_REG 1

export CGRA_GEN_ALL_REG=1

# Genesis2.pl -parse -generate -top top -input\

if [ -d genesis_verif ]; then
  rm -rf genesis_verif
fi

# Let's do this in run.csh instead...
# branch=`git rev-parse --abbrev-ref HEAD`
# if [[ `hostname` == "kiwi" && "$branch" == "nbdev3" ]]; then
#   echo kiwi branch nbdev3 means must use no-opt or disable luts
# fi



Genesis2.pl -parse -generate -top top -hierarchy top.xml -input\
  top.vp \
  \
  ../sb/sb.vp \
  ../cb/cb.vp \
  \
  ../pe_new/pe/rtl/test_pe_red.svp \
  ../pe_new/pe/rtl/test_pe_dual.vpf \
  ../pe_new/pe/rtl/test_pe_comp.svp \
  ../pe_new/pe/rtl/test_pe_comp_dual.svp \
  ../pe_new/pe/rtl/test_cmpr.svp \
  ../pe_new/pe/rtl/test_pe.svp \
  ../pe_new/pe/rtl/test_mult_add.svp \
  ../pe_new/pe/rtl/test_full_add.svp \
  ../pe_new/pe/rtl/test_lut.svp      \
  ../pe_new/pe/rtl/test_opt_reg.svp  \
  ../pe_new/pe/rtl/test_simple_shift.svp \
  ../pe_new/pe/rtl/test_shifter.svp  \
  ../pe_new/pe/rtl/test_debug_reg.svp  \
  \
  ../pe_tile_new/pe_tile_new.vp \
  \
  ../empty/empty.vp \
  ../io1bit/io1bit.vp \
  ../io16bit/io16bit.vp \
  ../global_signal_tile/global_signal_tile.vp \
  \
  ../memory_tile/memory_tile.vp \
  ../memory_core/memory_core.vp \
  ../memory_core/mem.vp \
  ../global_controller/global_controller.vp \
  \
  ../jtag/jtag.svp \
  ../jtag/Template/src/digital/template_ifc.svp \
  ../jtag/Template/src/digital/cfg_ifc.svp \
  ../jtag/Template/src/digital/flop.svp \
  ../jtag/Template/src/digital/tap.svp \
  ../jtag/Template/src/digital/reg_file.svp \
  ../jtag/Template/src/digital/cfg_and_dbg.svp


echo
echo HACKWARNING Swapping stub in place of DW_tap
echo HACKWARNING Swapping stub in place of DW_tap
echo HACKWARNING Swapping stub in place of DW_tap
echo cp  ../jtag/Template/src/digital/DW_tap.v.stub genesis_verif/DW_tap.v
cp  ../jtag/Template/src/digital/DW_tap.v.stub genesis_verif/DW_tap.v
echo

source clean_up_cgra_inputs.csh
source remove_genesis_wires.csh

if [ `hostname` == "kiwi" ]; then
  echo Checking cgra_info for errors...
  echo xmllint --noout cgra_info.txt
  xmllint --noout cgra_info.txt |& head -n 20
fi

