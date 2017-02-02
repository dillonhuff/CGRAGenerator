Genesis2.pl -parse -generate -top mem_tile_sb_cb -input ../memory/mem.vp ../memory/mem_tile.vp ../sb/sb.vp ../sb/tb_sb.vp ../cb/cb.vp mem_tile_sb_cb.vp mem_tile_sb_cb_pnr.tclp 

grep -v "^//\|^module\|^endmodule" genesis_verif/mem_tile_pnr.tcl > genesis_synth/pnr.tcl
