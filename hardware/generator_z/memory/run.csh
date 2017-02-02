Genesis2.pl -parse -generate -top mem_tile -input mem.vp ../sb/sb.vp ../cb/cb.vp mem_tile.vp mem_tile_pnr.tclp 

grep -v "^//\|^module\|^endmodule" genesis_verif/mem_tile_pnr.tcl > genesis_synth/pnr.tcl
