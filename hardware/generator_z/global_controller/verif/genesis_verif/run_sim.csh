#!/bin/tcsh
set RTL_FOLDER="../../top/genesis_verif"
rm -rf INCA_libs irun.*
irun -top top -timescale 1ns/1ps -l irun.log -access +rwc -notimingchecks -input cmd.tcl top.sv cfg_and_dbg_unq1.sv cfg_ifc_unq1.sv clocker_unq1.sv flop_unq1.sv flop_unq2.sv flop_unq3.sv flop_unq4.sv JTAGDriver.sv jtag_unq1.sv tap_unq1.sv template_ifc_unq1.sv test_unq1.sv global_controller.sv $SYNOPSYS/dw/sim_ver/DW_tap.v
