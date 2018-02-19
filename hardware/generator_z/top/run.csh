#!/bin/bash

# @Caleb: For providing registers on all outputs of all SBs, do-
# setenv CGRA_GEN_ALL_REG 1 (csh syntax)
export CGRA_GEN_ALL_REG=1


if [ -d genesis_verif ]; then
  rm -rf genesis_verif
fi

# Let's do this in run.csh instead...
# branch=`git rev-parse --abbrev-ref HEAD`
# if [[ `hostname` == "kiwi" && "$branch" == "nbdev3" ]]; then
#   echo kiwi branch nbdev3 means must use no-opt or disable luts
# fi


echo
echo HACKWARNING Swapping in 'srnew' LUTs
echo HACKWARNING Swapping in 'srnew' LUTs
echo HACKWARNING Swapping in 'srnew' LUTs
echo cp ../pe_new/pe/rtl/test_pe.svp.srnew ../pe_new/pe/rtl/test_pe.svp 
cp ../pe_new/pe/rtl/test_pe.svp.srnew ../pe_new/pe/rtl/test_pe.svp 
echo

echo
echo HACKWARNING IO pads are hardwired outputs=side0,1 inputs=2,3
echo HACKWARNING IO pads are hardwired outputs=side0,1 inputs=2,3
echo HACKWARNING IO pads are hardwired outputs=side0,1 inputs=2,3
echo

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
  ../memory_core/input_sr.vp \
  ../memory_core/output_sr.vp \
  ../memory_core/linebuffer_control.vp \
  ../memory_core/fifo_control.vp \
  ../memory_core/mem.vp \
  ../memory_core/memory_core.vp \
  \
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
echo HACKWARNING Restoring original LUT code
echo HACKWARNING Restoring original LUT code
echo HACKWARNING Restoring original LUT code
echo git checkout ../pe_new/pe/rtl/test_pe.svp
git checkout ../pe_new/pe/rtl/test_pe.svp
echo



echo
echo HACKWARNING Swapping stub in place of DW_tap
echo HACKWARNING Swapping stub in place of DW_tap
echo HACKWARNING Swapping stub in place of DW_tap
echo cp  ../jtag/Template/src/digital/DW_tap.v.stub genesis_verif/DW_tap.v
cp  ../jtag/Template/src/digital/DW_tap.v.stub genesis_verif/DW_tap.v
echo


source clean_up_cgra_inputs.csh
source remove_genesis_wires.csh

echo
echo HACKWARNING Adding IO constraints to cgra_info.txt
echo HACKWARNING Adding IO constraints to cgra_info.txt
echo HACKWARNING Adding IO constraints to cgra_info.txt
grep -v '/CGRA' cgra_info.txt > /tmp/tmp.$$
cat << eof >> /tmp/tmp.$$

  <BOARD>
    <!-- Sides 0,1,2,3 are right, bottom, left, top respectively -->
    <input >side2_group2</input>
    <input >side3_group3</input>
    <output>side0_group0</output>
    <output>side1_group1</output>
  </BOARD>

</CGRA>
eof
mv /tmp/tmp.$$ cgra_info.txt
echo

if [ `hostname` == "kiwi" ]; then
  echo Checking cgra_info for errors...
  echo xmllint --noout cgra_info.txt
  xmllint --noout cgra_info.txt |& head -n 20
fi
