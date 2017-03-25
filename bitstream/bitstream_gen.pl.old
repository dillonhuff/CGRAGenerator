#!/usr/bin/env perl
#use strict;
use warnings;

#################### DESIGN PARAMETERS ##############################
my $DATA_WIDTH=32;
my $TILE_ADDR_WIDTH=16;
my $FEATURE_ADDR_WIDTH=8;
my $CFG_REG_ADDR_WIDTH=2;
#####################################################################

############### PARSE INPUT FILES POINTERS ##########################
if(! (defined $ARGV[0]))
{
                die "\nInfo file from P&R not provided \n";
}

if(! (defined $ARGV[1]))
{
                die "\nOutput config.dat file not provided\n";

}

my $info_file = $ARGV[0];
open(my $fh1, "<", "$info_file");

my $config = $ARGV[1];
open(my $DAT, ">", $config.'.dat');

######################################################################

#################### VARIABLE SETUP ##################################
my $TILE_ADDR_WIDTH_HEX=$TILE_ADDR_WIDTH/4;
my $FEATURE_ADDR_WIDTH_HEX=$FEATURE_ADDR_WIDTH/4;
my @array;
my $TILE;
my $tag;
my $feature;
my $sel_wid_bin;
my $feat_addr;
my $bitstream_bin_sb;
my $bitstream_hex_sb;
my $padded_len_cb;
my $cfg_reg_sb;
my $cfg_reg_sb_hex;
my $addr;
my $addr_b;
my $CELL;
my $dir;
my $snk_addr = 0;
my $trk_ctr = 0;
my $cb_cnt = 0;
my $sb_cnt = 0;
my $pe_cnt = 0;
my $dir_ctr = 0;
my $mux_cnt = 0;
my @bitstream_arr = ();
########################################################################

################# DEBUG FILE SETUP ######################################
my $debug_file = 'DEBUG.INFO';
open(my $DEBUG, ">", "$debug_file") 
   or die "Could not open file '$debug_file' $!";


################# FILE PARSER & BIT STREAM GENERATOR ####################

while (<$fh1>) {
        
        #<tile tile_addr='0' row='0' col='0' tracks='BUS1:5 BUS16:6 '>
        if($_ =~ m/^\s*<tile\s*tile_addr\s*=\s*'(\S+)'\s*\S+/)
               {
                    $TILE = "tile_${1}";
                    $DS{$TILE}{tile_addr}= sprintf("%0${TILE_ADDR_WIDTH_HEX}X",$1);
               }           
        
        #<cb feature_address='2' bus='BUS16'>
        elsif($_ =~ m/^\s*<(\S+)\s*feature_address\s*=\s*'(\S+)'\s*\S+/)
               {
                    $tag = $1;
                    $feat_addr = $2;
                    if ($tag =~ m/cb/) 
                        {
                            $feature = "${tag}_${cb_cnt}";
                        }
                    elsif ($tag =~ m/sb/)
                        {
                            $feature = "${tag}_${sb_cnt}";
                        }
                    elsif ($tag =~ m/pe/)
                       {   
                            $feature = "${tag}_${pe_cnt}";
                       }
                   $DS{$TILE}{$feature}{feature_addr}= sprintf("%0${FEATURE_ADDR_WIDTH_HEX}X",$feat_addr);    

               }
       
       #<sel_width>5</sel_width>
       elsif($_ =~ m/^\s*<sel_width>\s*(\S+)\s*<\/sel_width>/)
               {
                   $DS{$TILE}{$feature}{sel_width}=$1;
                   $sel_wid_bin = $1;
               }
       
       #<src sel='0'>in_BUS1_S0_T0</src>
       elsif($_ =~ m/^\s*<src sel=\s*'(\S+)'>\s*\S*/)
               {
                   $sel_int = $1;
                   $DS{$TILE}{$feature}{sel} = sprintf ("%0${sel_wid_bin}b", $sel_int);
                   if ($tag =~ m/cb/) 
                        {
                            $DS{$TILE}{$feature}{sel} = sprintf ("%0${sel_wid_bin}b", $sel_int);
                            $cfg_reg_cb = 0;
                            $cfg_reg_cb_hex = (sprintf "%0${CFG_REG_ADDR_WIDTH}x", $cfg_reg_cb);
                            $padded_len_cb = $DATA_WIDTH - $sel_wid_bin;
                            $padded_cfg_data_cb = (sprintf "%0${padded_len_cb}b",0);
                            $bitstream_bin_cb = "${padded_cfg_data_cb}${DS{$TILE}{$feature}{sel}}";
                            $bitstream_hex_cb = sprintf('%08X', oct("0b$bitstream_bin_cb"));
                            $DS{$TILE}{$feature}{bitstream} = $bitstream_hex_cb;
                            print $DEBUG "CB DEBUG: TILE : $TILE | FEAT_ID = $feature | SEL_WID: $DS{$TILE}{$feature}{sel_width} | SEL: $DS{$TILE}{$feature}{sel} \n";
                            print $DEBUG "CB DEBUG: Bitstream for $TILE : $feature $bitstream_bin_cb \n\n"; 
                            print $DAT "${cfg_reg_cb_hex}${DS{$TILE}{$feature}{feature_addr}}${DS{$TILE}{tile_addr}} $bitstream_hex_cb\n"
                        }    
                   elsif ($tag =~ m/sb/)
                        {  
                            $DS{$TILE}{$feature}{$mux_idx}{sel} = sprintf ("%0${sel_wid_bin}b", $sel_int);
                            $j = 1;
                            for (my $i=$cfgl; $i <=$cfgh; $i++)
                                {
                                    $int = substr($DS{$TILE}{$feature}{$mux_idx}{sel}, -$j, 1);
                                    $bitstream_arr[$i] = $int;
                                    $j++;
                                }
                            $bitstream_arr[$cfgr] = $DS{$TILE}{$feature}{$mux_idx}{reg_sel};    
                        print $DEBUG "SB DEBUG: TILE : $TILE | FEAT_ID = $feature | MUX_ID = $mux_idx | SNK: $DS{$TILE}{$feature}{$mux_idx}{snk} | SEL: $DS{$TILE}{$feature}{$mux_idx}{sel} \n";
                        }

               }
       
       #<mux snk='out_BUS16_S0_T0' reg='1' configh='1' configl='0' configr='40'>
       elsif ($_ =~ m/^\s*<mux\s*snk='(\S+)'\s*reg='(\S+)'\s*configh='(\S+)'\s*configl='(\S+)'\s*configr='(\S+)'>/)
              {
                   $mux_idx = "mux_${mux_cnt}" ;
                   $DS{$TILE}{$feature}{$mux_idx}{snk} = $1;
                   $DS{$TILE}{$feature}{$mux_idx}{reg_sel} = $2;
                   $cfgh = $3;
                   $cfgl = $4;
                   $cfgr = $5;
                   $mux_cnt++;
              }   
       
       elsif ($_ =~m/<\/cb>/)
              {
                   $cb_cnt = $cb_cnt + 1;
              }
       
       elsif ($_ =~m/<\/pe>/)
              {
                   $pe_cnt = $pe_cnt + 1;
              }
       
       elsif ($_ =~m/<\/sb>/)
              {
                   $sb_cnt = $sb_cnt + 1;
                   $mux_cnt = 0;
                   @bitstream_arr_rev = (reverse @bitstream_arr);  
                   my $complete_bitstream_sb = join("", @bitstream_arr_rev);
                   $DS{$TILE}{$feature}{bitstream} = $complete_bitstream_sb;
                   print $DEBUG "SB DEBUG: Bitstream for $TILE $feature : $DS{$TILE}{$feature}{bitstream}\n\n";
                   @bitstream_arr = ();
                   $len_bs = scalar @bitstream_arr_rev;
                   $cfg_reg_sb = 0;
                   $cfg_reg_sb_hex = (sprintf "%0${CFG_REG_ADDR_WIDTH}x", $cfg_reg_sb);
                   while ($len_bs > $DATA_WIDTH)
                        {
                             $right_ind = $len_bs - 1;
                             $left_ind = $len_bs - $DATA_WIDTH;
                             my $partial_bs_arr = join("", @bitstream_arr_rev[$left_ind..$right_ind]);
                             $bitstream_hex_sb = sprintf('%08X', oct("0b$partial_bs_arr"));
                             print $DAT "${cfg_reg_sb_hex}${DS{$TILE}{$feature}{feature_addr}}${DS{$TILE}{tile_addr}} $bitstream_hex_sb\n";
                             $len_bs = $len_bs - $DATA_WIDTH;
                             $cfg_reg_sb = $cfg_reg_sb + 1;
                             $cfg_reg_sb_hex = (sprintf "%0${CFG_REG_ADDR_WIDTH}x", $cfg_reg_sb);
                        }    
                   $padded_len = $DATA_WIDTH - $len_bs;
                   $padded_cfg_data_sb = (sprintf "%0${padded_len}b",0);
                   $right_ind = $len_bs - 1;
                   my $partial_bs_arr = join("", @bitstream_arr_rev[0..$right_ind]);
                   $bitstream_bin_sb = "${padded_cfg_data_sb}${partial_bs_arr}";
                   $bitstream_hex_sb = sprintf('%08X', oct("0b$bitstream_bin_sb"));
                   print $DAT "${cfg_reg_sb_hex}${DS{$TILE}{$feature}{feature_addr}}${DS{$TILE}{tile_addr}} $bitstream_hex_sb  \n";

           }

         elsif ($_ =~m/<\/tile>/)
           {
                   $pe_cnt = 0;
                   $sb_cnt = 0;
                   $cb_cnt = 0;
            }

}

close $DAT;
close $DEBUG;
       
#################################################################################################################### 
