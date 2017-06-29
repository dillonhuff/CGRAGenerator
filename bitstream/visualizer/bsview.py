#!/usr/bin/python
import sys
import re

# # gi a.k.a. pygobjects, pygtk
# import gi
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk,Gdk

import pygtk
pygtk.require('2.0')
import gtk
# from gtk import Gtk,Gdk
Gtk = gtk  # FIXME!

import cairo
from subprocess import call

import traceback
# sys.stdout.flush(); traceback.print_stack(); sys.stderr.flush()

import time # for time.sleep(2)

####################################################
# Some random utilities here in this random place...

def exit(): sys.exit(0)

def errmsg(m):
    sys.stdout.write("ERROR: %s\n" % (m))
    sys.exit(-1)

global PRINTED
PRINTED = [] # oh this is awful
def print_once(s):
    global PRINTED
    if (s not in PRINTED):
        PRINTED.append(s); print s

####################################################


# Want to list all the random globals here
global CUR_TILENO
global CUR_CURSOR # Currently includes 'magplus', 'magminus', 'arrow'
CUR_CURSOR = 'arrow'

# print dir(gtk.gdk.Window.props)
# sys.exit(0)

#TODO
# Put PE in each tile and connections to/from PE

from math import pi
PI = pi
def deg2rad(rad): return rad*180/PI

# width and height of PE
global PE_WIDTH;  PE_WIDTH = 30
global PE_HEIGHT; PE_HEIGHT = 12



GRID_WIDTH  = 2;
GRID_HEIGHT = 2;
NTILES = GRID_WIDTH*GRID_HEIGHT
TILE_LIST = range(0, NTILES)

# Old regime default: SWAP = False
# New regime default: SWAP = True
SWAP = True

PRINTED_CONFIG = False

# tileno-to-RC conversion
def tileno2rc(tileno):
    # Assumes a 4x4 grid of tiles numbered 0-15, laid out as shown above.
    # Given tile number tileno return the (row,column) equivalent
    #
    #    tileno                    r,c
    #  0  4   8  12      (0,0) (0,1) (0,2) (0,3)
    #  1  5   9  13      (1,0) (1,1) (1,2) (1,3)
    #  2  6  10  14      (2,0) (2,1) (2,2) (2,3)
    #  3  7  11  15      (3,0) (3,1) (3,2) (3,3)
    #
    # Unless SWAP = True, in which case...just the opposite (ugh!)
    #
    #      tileno                    r,c
    #   0   1   2   3      (0,0) (0,1) (0,2) (0,3)
    #   4   5   6   7      (1,0) (1,1) (1,2) (1,3)
    #   8   9  10  11      (2,0) (2,1) (2,2) (2,3)
    #  12  13  14  15      (3,0) (3,1) (3,2) (3,3)
    #

    # Is this smart? Ans: NO   # FIXME/TODO
    if (GRID_WIDTH >= 8):
        return tileno2rc_8x8(tileno)

    row =     tileno % GRID_HEIGHT
    col = int(tileno / GRID_WIDTH)
    
    if (not SWAP): return [row, col];
    else:          return [col, row];

def rc2tileno(row,col):

    # Is this smart? Ans: NO   # FIXME/TODO
    if (GRID_WIDTH >= 8):
        return rc2tileno_8x8(row,col)

    if (not SWAP): return GRID_HEIGHT*col + row
    else:          return GRID_WIDTH *row + col



# Oh no
cgra_tile_info = '''
  <tile type='pe_tile_new' tile_addr='0' row='0' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='1' row='0' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='2' row='0' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='3' row='0' col='3' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='4' row='0' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='5' row='0' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='6' row='0' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='7' row='0' col='7' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='8' row='1' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='9' row='1' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='10' row='1' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='11' row='1' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='12' row='1' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='13' row='1' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='14' row='2' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='15' row='2' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='16' row='2' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='17' row='2' col='3' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='18' row='2' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='19' row='2' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='20' row='2' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='21' row='2' col='7' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='22' row='3' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='23' row='3' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='24' row='3' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='25' row='3' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='26' row='3' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='27' row='3' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='28' row='4' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='29' row='4' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='30' row='4' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='31' row='4' col='3' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='32' row='4' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='33' row='4' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='34' row='4' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='35' row='4' col='7' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='36' row='5' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='37' row='5' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='38' row='5' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='39' row='5' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='40' row='5' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='41' row='5' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='42' row='6' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='43' row='6' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='44' row='6' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='45' row='6' col='3' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='46' row='6' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='47' row='6' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='48' row='6' col='6' tracks='BUS1:5 BUS16:5 '>
  <tile type='memory_tile' tile_addr='49' row='6' col='7' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='50' row='7' col='0' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='51' row='7' col='1' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='52' row='7' col='2' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='53' row='7' col='4' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='54' row='7' col='5' tracks='BUS1:5 BUS16:5 '>
  <tile type='pe_tile_new' tile_addr='55' row='7' col='6' tracks='BUS1:5 BUS16:5 '>
'''

def tiletype(tileno):
    # FIXME again, search string should probably be compiled globally, outside all loops
    
    search_pattern = "type='(\S+)'.*tile_addr='%s'" % str(tileno)
    parse = re.search(search_pattern, cgra_tile_info)
    if (not parse):
        print "ERROR could not find type for tile %d" % tileno
        sys.exit(-1)
    else:
        type = parse.group(1)
        # print "Tile %d has type '%s'" % (tileno,type)
        return type
    

def tileno2rc_8x8(tileno):
    DBG = 0
    search_string = "tile_addr='%s'.*row='(\d+)'.*col='(\d+)'" % str(tileno)
    parse = re.search(search_string, cgra_tile_info)
    if (not parse):
        global PRINTED_CONFIG
        if (DBG and not PRINTED_CONFIG):
            print 'WARNING: Using search string "%s"\n' % search_string
            print "WARNING: Could not find tile number %s in this lookup table: %s" \
                % (str(tileno), cgra_tile_info)
            PRINTED_CONFIG = True;
        elif (DBG):
            print "WARNING: Could not find tile number '%s' in the lookup table." % str(tileno)
        return False
        
    row = int(parse.group(1))
    col = int(parse.group(2))
    if (DBG): print "Found tile number '%d' => row '%d' col '%d'" % (tileno, row, col)
    return (row,col)

def test_tileno2rc_8x8():
    for i in range(0, 55):
        tileno2rc_8x8(i)
# test_tileno2rc_8x8(); sys.exit(0)


def rc2tileno_8x8(row,col):
    DBG = 1
    search_string = "tile_addr='(\d+)'.*row='%d'.*col='%d'" % (row,col)
    parse = re.search(search_string, cgra_tile_info)
    # if (not parse):
    #     msg = 'Using search string "%s"\n' % search_string
    #     msg = msg + \
    #           "ERROR: Could not find tile (r%s,c%s) in this data structure: %s" \
    #           % (str(row), str(col), cgra_tile_info)
    #     errmsg(msg)
    if (DBG and not parse):
        msg = 'WARNING: Using search string "%s"\n' % search_string
        msg = msg + \
              "WARNING: Could not find tile (r%s,c%s) in this data structure: %s" \
              % (str(row), str(col), cgra_tile_info[:-1])  # -1 chops off trailing '\n'
        print msg
        return False
        
    tileno = int(parse.group(1))
    if (DBG): print "Found tile (r%dc%d) => tileno '%d'" % (row, col, tileno)
    return tileno

def test_rc2tileno_8x8():
    for r in range(0, 7):
        for c in range (0, 7):
            t = rc2tileno_8x8(r,c)
# test_rc2tileno_8x8(); sys.exit(0);


# A really dumb way to keep track of current scale factor, for
# button-press events FIXME do something better maybe
CUR_SCALE_FACTOR = 1;
SF_ALL       = 1; # No zoom when displaying all tiles in a window # FIXME NOT USED
SF_ALL_2x2   = 2; # Zoom 2x when displaying 2x2 grid              # FIXME NOT USED
INIT_SCALE_FACTOR = 1;

def set_initial_scale_factor():
    global CUR_SCALE_FACTOR;                   # Others should know
    global INIT_SCALE_FACTOR;                  # Others should know

    INIT_SCALE_FACTOR = 1                         # Default is one
    if (GRID_WIDTH <= 2): INIT_SCALE_FACTOR = 2   # Why squint if you don't need to?
    if (GRID_WIDTH  > 4): INIT_SCALE_FACTOR = 0.5 # Let's try this
    CUR_SCALE_FACTOR = INIT_SCALE_FACTOR

# Could/should derive these from "BUS:5" etc.
NTRACKS_PE_BUS_H = 5;
NTRACKS_PE_BUS_V = 5;

NTRACKS_PE_WIRE_H = 0;
NTRACKS_PE_WIRE_V = 0;

# ARROWHEAD_LENGTH = 2; ARROWHEAD_WIDTH = 4; # meh
ARROWHEAD_LENGTH = 3; ARROWHEAD_WIDTH = 2; # this is nice

# Here's a dumb way to pass information from the button-press handler to the draw-event handler
ZOOMTILE = -1;

# Diagram below shows dimensions for PORT_WIDTH (PW) 
# PORT_HEIGHT (PH) (aka PORT_LENGTH),
# REG_WIDTH (RW) and REG_HEIGHT (RH)
#
#    <--PW-->
#
#    +------+
#    |      |  ^
#    |      |  |
#    |      |  PH
#    |      |  |
#    |      |  v
#    +------+  ^
#     |>   |   RH
#     +----+   v
#
#     <-RW->

PORT_WIDTH  = 8;
# PORT_WIDTH  = 6;

PORT_HEIGHT = 16;
PORT_LENGTH = PORT_HEIGHT # Because sometimes I forget

PORT_PAD = PORT_WIDTH/2   # Padding before and between groups of ports

REG_WIDTH  = PORT_WIDTH - 2;
REG_HEIGHT = 2;

# Edge of first tile in array (grid) view is ARRAY_PAD + PORT_HEIGHT
ARRAY_PAD = 60

# Canvas size for displaying a single tile edge-to-edge w/ no padding
#   How big is a tile canvas?  Refer to diagram in doc
#   Short answer is:
#     Canvas width  = 2*plen + 2*ntracks_v*pwid + 3*pwid
#     Canvas height = 2*plen + 2*ntracks_h*pwid + 3*pwid
#   where each port is an arrow in a box that's portlength long and portwidth wide
#   and ntracks_v = ntracks_bus_v + ntracks_wire_v etc.
# CANVAS_WIDTH  = 2*PORT_HEIGHT + 2*NTRACKS_PE_BUS_V*PORT_WIDTH + 3*PORT_PAD
# CANVAS_HEIGHT = 2*PORT_HEIGHT + 2*NTRACKS_PE_BUS_H*PORT_WIDTH + 3*PORT_PAD

CANVAS_WIDTH  = 2*PORT_HEIGHT + 3*NTRACKS_PE_BUS_V*PORT_WIDTH + 3*PORT_PAD
CANVAS_HEIGHT = 2*PORT_HEIGHT + 3*NTRACKS_PE_BUS_H*PORT_WIDTH + 3*PORT_PAD


WIN_WIDTH  = 4*CANVAS_WIDTH+2*ARRAY_PAD
WIN_HEIGHT = 4*CANVAS_HEIGHT+2*ARRAY_PAD

##############################################################################
# These could all be part of a Wire class if we wanted to...



def quickfix(wirename):
    DBG=0
    # Some quick rewrites for the new mem tiles
    # E.g. 'out_0_BUS16_3_0 should I THINK be same as out_s3t0
    # FIXME is this the right place to do this?
    # FIXME is this the right *way* to do this?

    # if DBG: print "Rewriting wire '%s'" % wirename

    # 'out_0_BUS16_3_0 should I THINK be same as out_s3t0
    decode = re.search('(in|out)_0_BUS16_(.*)_(.*)', wirename);
    if (decode):
        wnew = "%s_s%st%s" % (decode.group(1), decode.group(2), decode.group(3))
        if DBG: print "quickfix() rewrote '%s' => '%s'" % (wirename, wnew)
        wirename = wnew
    return wirename


# E.g. given "out_s1t3", rval['inout'] = "out", rval['side'] = 1 and rval['track'] = 3
def parse_wirename(wirename):
    rval = {}

    # FIXME This probably gonna bite me in the a55...
    # fix for: "WARNING PW does not understand ... 'out_1_BUS16_2_0'..."
    # pretends like e.g. 'out_1_BUS16_2_0' same as "out_s2t0"

    decode = re.search('(in|out)_1_BUS16_(.*)_(.*)', wirename);
    if (decode):
        DBG=0
        rval['inout'] = decode.group(1)
        rval['side']  = int(decode.group(2))
        rval['track'] = int(decode.group(3))
        if DBG: print "PW interprets '%-15s' => '%s_s%dt%d'" % \
           (wirename, rval['inout'], rval['side'], rval['track'])
        return rval

    decode = re.search('(in|out)_s(.*)t(.*)', wirename);
    if (decode):
        rval['inout'] = str(decode.group(1))
        rval['side']  = int(decode.group(2))
        rval['track'] = int(decode.group(3))
        return rval

    else:
        print "WARNING PW does not understand wirename '%s' (yet)" % wirename
        print "WARNING (Arbitrarily) connecting unknown wire to 'outs3t4' instead"
        # sys.stdout.flush(); traceback.print_stack(); sys.stderr.flush()
        # print ""
        # print ""
        rval['inout'] = "out"
        rval['side']  = 3
        rval['track'] = 4
        return rval

def inout(wirename): return parse_wirename(wirename)['inout']
def side(wirename): return parse_wirename(wirename)['side']
def track(wirename): return parse_wirename(wirename)['track']
##############################################################################

# This could be an extension of cr's class I suppose
def draw_arrow(cr, al, ahl,ahw,fill):
    # Draw an arrow of total length al and line_width aw
    # Arrowhead on the end is a triangle of length ahl, width ahw
    # if "fill" is true, fill in the triangle.
    # Arrow starts at location (0,0);
    # use cr.translate() and rotate() to place and rotate it
    # E.g. for down arrow starting at (x,y)
    # cr.save()
    #   cr.translate(x,y); cr.rotate(-PI/2)
    #   draw_arrow(al,aw,ahl,ahw,fill)
    # cr.restore()

    cr.save()
    if (1):

        # To get exact offset I'd have to do math :( with sin and cos or sumpm
        if (not fill):
            SQ2 = 1.4142
            offset = cr.get_line_width()/SQ2
            al = al - offset
            ahw = ahw - 2*offset

        # The line
        cr.move_to(0,0)
        if (fill): cr.line_to(al-ahl,0)
        else:      cr.line_to(al,0)
        cr.stroke()

        # The arrowhead
        if (fill): cr.set_line_width(1);
        cr.move_to(al-ahl, -ahw/2)
        cr.line_to(al,     0)
        cr.line_to(al-ahl, ahw/2)
        if (fill):
            cr.close_path()
            cr.fill()

        cr.stroke()
    cr.restore()

# Big ghost arrows in background of grid view show prevailing port direction
def draw_big_ghost_arrows(cr):

    # Ghost Arrow parms, used by big_ghost_arrow(), 
    aw = 10                # line width
    ahl = 20; ahw = 3*aw   # arrowhead length, width

    # Arrow goes across two tiles, sticks out apad on one side and (apad + ahl/2) on the other
    apad = 10;
    al = 2*CANVAS_WIDTH + 2*apad + ahl/2  # length of arrow
    al = GRID_WIDTH*CANVAS_WIDTH + 2*apad + ahl/2  # length of arrow

    fill = True;  # For solid filled-in arrowhead

    # Ghost arrows are ghooooostly graaaaaay, woooooooo!
    # graylevel = 0.9; cr.set_source_rgb(graylevel,graylevel,graylevel)
    setcolor(cr, "ghostgray")

    def draw_big_ghost_arrow(cr,x,y,dir):

        cr.save()
        if (1):
            cr.translate(x,y)
            cr.set_line_width(aw);
            if (dir=='left'): cr.rotate(PI)
            if (dir=='down'): cr.rotate(PI/2)
            if (dir=='up'):   cr.rotate(3*PI/2)
            draw_arrow(cr,al,ahl,ahw,fill)
        cr.restore()

    # Right-pointing arrows start apad back from left edge of the tile
    # and ra_v_offset down from the top
    ra_start    = -apad;
    ra_v_offset = PORT_LENGTH + 2 * PORT_WIDTH

    # Left-pointing arrows start apad beyond the right edge of the tile
    # and ra_h_offset up from the bottom
    la_start    = GRID_WIDTH*CANVAS_WIDTH + apad;
    la_v_offset = CANVAS_HEIGHT - ra_v_offset

    for tilerow in range (0, GRID_HEIGHT):
        draw_big_ghost_arrow(cr, ra_start, ra_v_offset + tilerow*CANVAS_HEIGHT, 'right')
        draw_big_ghost_arrow(cr, la_start, la_v_offset + tilerow*CANVAS_HEIGHT, 'left')

    # Similar for up/down arrows
    da_start = -apad;
    da_h_offset = ra_v_offset;
    ua_start = GRID_HEIGHT*CANVAS_HEIGHT + apad;
    ua_h_offset = CANVAS_WIDTH - da_h_offset

    for tilecol in range (0, GRID_HEIGHT):
        draw_big_ghost_arrow(cr, da_h_offset + tilecol*CANVAS_WIDTH, da_start, 'down')
        draw_big_ghost_arrow(cr, ua_h_offset + tilecol*CANVAS_WIDTH, ua_start, 'up')

# This could be an extension of cr's class I suppose
def setcolor(cr, colorname):
    colordict = {}

    # Sixteen "official" HTML colors
    # https://en.wikipedia.org/wiki/Web_colors#HTML_color_names

    colordict["white"]   = ( 1.00, 1.00, 1.00)
    colordict["silver"]  = ( 0.75, 0.75, 0.75)
    colordict["gray"]    = ( 0.50, 0.50, 0.50)
    colordict["black"]   = ( 0.00, 0.00, 0.00)
    colordict["red"]     = ( 1.00, 0.00, 0.00)
    colordict["maroon"]  = ( 0.50, 0.00, 0.00)
    colordict["yellow"]  = ( 1.00, 1.00, 0.00)
    colordict["olive"]   = ( 0.50, 0.50, 0.00)
    colordict["lime"]    = ( 0.00, 1.00, 0.00)
    colordict["green"]   = ( 0.00, 0.50, 0.00)
    colordict["aqua"]    = ( 0.00, 1.00, 1.00)
    colordict["teal"]    = ( 0.00, 0.50, 0.50)
    colordict["blue"]    = ( 0.00, 0.00, 1.00)
    colordict["navy"]    = ( 0.00, 0.00, 0.50)
    colordict["fuchsia"] = ( 1.00, 0.00, 1.00)
    colordict["purple"]  = ( 0.50, 0.00, 0.50)

    # What, no orange!?
    colordict["orange"]  = ( 1.00, 0.50, 0.00)

    # My own ghostly gray
    graylevel = 0.9;
    colordict["ghostgray"] = (graylevel,graylevel,graylevel)

    # return colordict[colorname]
    (r,g,b) = colordict[colorname];
    cr.set_source_rgb(r,g,b)

# This could be an extension of cr's class I suppose NO!!!! it's a time waster
def drawdot(cr, x, y, color):

    # For debugging purposes, draw a colorful dot at location (x,y)

    dotsize = 1.0
    dotsize = 0.8

    # cr.set_line_width (10.0); # For BIG dots

    cr.save()
    if (1):
        setcolor(cr, color)
        cr.arc (x, y, dotsize, 0, 2*PI);
        cr.fill ();
        cr.stroke ();
    cr.restore()

    # Instead of cr.stroke(), could do this: "path = cr.copy_path()"
    # and then return the path for later use e.g. "cr.append_path(path); cr.stroke()"
    

def connectionpoint(wirename):

    # Given wirename e.g. "out_s0t0", return x,y coords of its connection
    # point on the edge of the tile, relative to edge of canvas.

    # FIXME rewrite this littel snippet below
    # outs1/ins3 blocks start in SE/NE and go left (neg x direction)
    # outs2/ins0 blocks start in SW/SE and go up   (neg y direction)
    # outs3/ins1 blocks start in NW/NE and go right (pos x direction)

    # FIXME
    # 1. Sometimes wirename = "in_s9t9"  This indicates a memtile cb that we don't understand yet
    # 2. Sometimes wirename = "out_s9t9"  This is bsview.py propagating the
    # "in_s9t9" problem...maybe this will mollify it i dunno
    
    hackwire = False
    if (wirename == "in_s9t9" ): hackwire = "in_s0t0"
    if (wirename == "out_s9t9"): hackwire = "out_s0t0"
    if (hackwire):
        wirename = hackwire
        if (not TILES_DRAWN_AT_LEAST_ONCE):
            print "WARNING Found wire %s indicating memtile cb" % wirename
            print "WARNING Do not yet understand memtile cb's"
            print "WARNING Will use '%s' instead" % hackwire

    # WARNING CP does not understand wirename 'out_1_BUS16_2_0' (yet)
    # FIXME hack: out_1_BUS16_2_0 is just out0_s2t0 minus tilecanvas_height.  Right?
    # Okay it might be more nuanced than this.
    # First, note that sb_wires are always side 3
    # out_1_ only shift down by pad amount;
    #  in_1_ maybe don't shift at all...?
    #
    # wire             xfudge       yfudge
    # in_0_*           0            0
    # in_1_BUS16_0     0            CH
    # in_1_BUS16_1     0            CH
    # in_1_BUS16_2     0            CH
    # in_1_BUS16_3     0            CH
    #
    # out_0_* => same as "in" maybe

    # wire             xfudge       yfudge
    # sb_wire_in_1     0            CH
    # sb_wire_out_1    0            CH

    # Problems: in_1_BUS16_2_0 did not move...?
    # Problems: 'no options parameter, sorry'

    yfudge = 0  # FIXME fudge factors for e.g. out_0_ etc.
    decode = re.search('(in|out)_1_BUS16_(.*)_(.*)', wirename);
    if (decode):
        DBG=0
        inout = decode.group(1)
        side  = decode.group(2)
        track = decode.group(3)
        wnew = "%s_s%st%s" % (inout, side, track)
        if DBG: print "CP adding fudge to '%s'" % wirename
        if DBG: print "CP rewrote '%-15s' => '%s'" % (wirename, wnew)
        wirename = wnew
#         if (inout == "in"): yfudge = PORT_HEIGHT
#         else:               yfudge = CANVAS_HEIGHT
        yfudge = CANVAS_HEIGHT


    # Problem: in_1_BUS16_2_0 connects to wrong place (should go to sb_wire_out_1_BUS16_3_0
    # data[(31, 30)] : @ tile (3, 0) connect wire 2 (in_1_BUS16_2_0) to sb_wire_out_1_BUS16_3_0

    # Need block id and track number of the target wire
    decode = re.search('(in_s.*|out_s.*)t(.*)', wirename);
    if (decode):
        b = decode.group(1);      # blockno e.g. "in_s1"
        t = int(decode.group(2)); # trackno e.g. "3"
    else:
        print "WARNING CP does not understand wirename '%s' (yet)" % wirename
        print "WARNING (Arbitrarily) connecting unknown wire to 'outs3t4' instead"
        (b,t) = ("out_s3",4)

    # ALSO need to fudge side-1 (bottom) wires on mem tiles.
    # FIXME globals are evil.  Also this evil memtile hack
    global CUR_TILENO # Didn't we do this somewhere already
    if (tiletype(CUR_TILENO) == "memory_tile"):
        DBG=0
        if DBG: print "CP found memory tile %d, wirename '%s'" % (CUR_TILENO, wirename)
        if (b == "out_s1") or (b ==  "in_s1"):
            if DBG: print "CP adding fudge b/c side 1 (bottom)"
            yfudge = CANVAS_HEIGHT
        
    # Canvas consists of a single tile padded on each side by space equal to "PORT_LENGTH"
    
    # A tile's edge is PORT_LENGTH away from the canvas edge
    # The first connection point begins "PORT_PAD + PORT_WIDTH/2" from nearest tile edge.
    # The distance from one track to the next is PORT_WIDTH.
    # So track t connects at a distance CD = PL+PP+PW/2+t*PW from edge of canvas
    CD = PORT_LENGTH + PORT_PAD + PORT_WIDTH/2 + (t * PORT_WIDTH)
    PL = PORT_HEIGHT

    # Sides (0,1,2,3) are (E,S,W,N) sides of tile respectively

    # out_s0 wires start at NE corner and go DOWN
    # in_s0 tracks start at SE corner and go UP
    if (b == "out_s0"): (x,y) = (CANVAS_WIDTH - PL,                 CD)
    if (b ==  "in_s0"): (x,y) = (CANVAS_WIDTH - PL, CANVAS_HEIGHT - CD)

    # out_s1 wires start at SE corner and go LEFT
    #  in_s1 wires start at SW corner and go RIGHT
    if (b == "out_s1"): (x,y) = (CANVAS_WIDTH - CD, CANVAS_HEIGHT - PL)
    if (b ==  "in_s1"): (x,y) = (               CD, CANVAS_HEIGHT - PL)

    # out_s2 wires start at SW corner and go UP
    #  in_s2 wires start at NW corner and go DOWN
    if (b == "out_s2"): (x,y) = (PL, CANVAS_HEIGHT - CD)
    if (b ==  "in_s2"): (x,y) = (PL,                 CD)

    # out_s3 wires start at NW corner and go RIGHT
    #  in_s3 wires start at NE corner and go LEFT
    if (b == "out_s3"): (x,y) = (               CD, PL)
    if (b ==  "in_s3"): (x,y) = (CANVAS_WIDTH - CD, PL)

    try: x
    except: print "ERROR Could not find connection point for " + wirename

    # print "yfudge is (still) %d" % yfudge
    return (x, y + yfudge);

# TODO/FIXME need at least one more pass on drawport() below!

# E.g. 'drawport(cr, "out_s1t0")' or 'drawport(cr, wirename, options="ghost")'
def drawport(cr, wirename, **keywords):
    DBG = 0

    # Draw the port for the indicated wire in the context of the current canvas
    # Ports are labeled arrows; input ports point in to the tile and
    # output ports point out.
    # connectionpoint() will tell where to start (for outputs) or end (for inputs)
    # [Optionally] attach a register to the port inside the tile.
    # [Optionally] leave off the label

    if DBG: print "Drawing port for wire '%s'..." % (wirename)

    # Only valid option so far is "ghost", meaning draw the port in light background color
    # TODO: options for reg/noreg, label/nolabel
    
    optionlist = []
    if ('options' in keywords):
        if DBG: print 'options parameter found, it is ', keywords['options']
        optionlist = keywords['options'].split(',')
        if DBG: print "Found the following options: "+ str(optionlist)
        # for o in options: print "  " + o
    else:
        if DBG: print 'no options parameter, sorry'

    cr.save()

    if (1):
        # Translate and rotate the world...
        # if DBG: print "Translate to %d,%d" % (x,y),
        (x,y) = connectionpoint(wirename)
        cr.translate(x,y)
        drawdot(cr, 0, 0, "black") # Mark the connection point with a black dot

        # if (wirename == "sb_wire_out_1_BUS16_3_0"): print "FOO x,y is %d,%d" % (x,y)

        # Side 0,1,2,3 out-wires point E, S, W and N respectively
        s = side(wirename)
        rot = s * 3.1416/2
        if DBG: print "rotate %d degrees\n" % int(180*rot/3.1416)
        cr.rotate(rot)

        # Now origin is connection point and world is oriented to the appropriate side

        # This should be, like "if (arrow)"
        if (1):
            ########################################################################
            # Arrow

            cr.save()
            setcolor(cr, 'blue') # Blue arrows (unless ghost)
            if ('ghost' in optionlist): cr.set_source_rgb(.8,.8,1) # slightly darker ghost

            # Thick and thin arrows for buses vs. tracks
            # For demonstration purposes,
            # tracks 0-2 are buses (thick) and tracks 3,4 are wires (thin)
            # FIXME maybe should hav global parms LINEWIDTH_BUS LINEWIDTH_WIRE
            if (track(wirename) < 3): linewidth = 1.0;
            else:                     linewidth = 0.5;
            cr.set_line_width(linewidth)

            (ahl,ahw) = (ARROWHEAD_LENGTH, ARROWHEAD_WIDTH)

            margin = 2*linewidth

            # Flip the sense of the arrow for "in" wires
            flip = False;
            if (inout(wirename) == "in"): flip = (not flip);

            if (flip):
                cr.translate(PORT_HEIGHT,0)
                cr.rotate(3.1416)

            fill = False
            ahl = ahl + margin
            # FIXME shouldn't need margin...right? Should be baked in to draw_arrow...yessss?
            draw_arrow(cr, PORT_HEIGHT-margin, ahl, 2*ahw, fill)
            cr.restore()


#         if (1):
        if ('reg' in optionlist):
            ########################################################################
            # Register

#             cr.save()
#             cr.set_line_width(.2)
#             setcolor(cr, 'red')
# 
#             # From side 0 (unrotated) POV,
#             # reg corner is rh IN and rw/2 UP from connection point.
#             # Sides 1, 2, 3 rotate appropriately.
#             (ULx,ULy) = (-REG_HEIGHT, -REG_WIDTH/2)
# 
#             # Draw the register
#             cr.rectangle(ULx,ULy,  REG_HEIGHT, REG_WIDTH) # ULx, ULy, width, height
# 
#             # Draw the little triangle for the clock
#             cr.move_to(ULx,ULy);
#             cr.line_to(ULx+REG_HEIGHT/2,ULy+1);
#             cr.line_to(ULx+REG_HEIGHT,ULy)
#             cr.stroke()
# 
#             cr.restore()
# 
            cr.save()
            setcolor(cr, "red")
            cr.set_line_width(.2)
            (ULx,ULy) = (0, -REG_WIDTH/2)
            cr.translate(ULx,ULy)
            # cr.translate(ULx,ULy)

            # Drawreg default is to draw horizontal;
            # but this routine's default is oriented to side 0 (90d cw)
            cr.rotate(PI/2)

            h = REG_HEIGHT  # I know, I know
            w = REG_WIDTH
            drawreg(cr, w,h)
            cr.stroke()
            cr.restore()



        # should be "if (option[label])
        if (1):
            ########################################################################
            # Label

            cr.save() # Save early, save often

            # Label color: light gray for "ghost" text, otherwise just red
            # FIXME Areall the ghostgrays different!!?  Should they be??
            setcolor(cr, 'red')
            if ('ghost' in optionlist): cr.set_source_rgb(1,.8,.8)  # darker light gray

            # Position: one pixel in, and just high enough to clear the arrowhead
            (x,y) = (1, -ARROWHEAD_WIDTH)
            # drawdot(cr,x,y,"blue"); drawdot(cr,0,0,"red")

            # Unrotate side 2 (west) else they will be upsie-down!
            if (side(wirename)==2):
                cr.rotate(PI);
                cr.translate(-PORT_HEIGHT, 0)

            # "input" wires get moved to right to get out of the way of the arrowhead
            # Unless they're on the W side (side 2) in which case they're okay b/c unrotate above
            if (inout(wirename) == "in"):
                if (side(wirename) != 2): x = x + (ARROWHEAD_LENGTH + 1)

            # Could I think use "text_path" to e.g. right-justify labels etc.
            cr.set_font_size(2.5)
            # cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.move_to(x,y)
            cr.show_text(wirename)
            cr.stroke()
            cr.restore()

    cr.restore()

def drawreg(cr, w,h):
    # Draw a register with UL at (0,0), height h and width w
    cr.save()

    # cr.translate(ULx,ULy)

    # Draw the register
    cr.rectangle(0,0,  w, h) # ULx, ULy, width, height
    cr.stroke()
    if (1):
        cr.save()
        # TODO fund and use background color instead of white!
        setcolor(cr, 'white')
        cr.rectangle(0,0,  w, h) # ULx, ULy, width, height
        cr.fill()
        cr.stroke()
        cr.restore()


    # Draw the little triangle for the clock
    cr.move_to(0,0);
    cr.line_to(h/2,h/2)
    cr.line_to(0,h)
    cr.stroke()
    cr.fill()
    cr.restore()

# def draw_pe(cr, opname, **keywords):
def draw_pe(cr, opname, A, B):
    DBG=1

    # Use cases I want to support:
    # draw_pe(cr, "ADD") => basic PE including input and output arrows
    # draw_pe(cr, "ADD", regA="2", regB="0") => basic PE + reg(s) w/labels

    # if (self.col==0): draw_pe(cr, "ADD", "0x00002", "0x0000")
    # if (self.col==1): draw_pe(cr, "ADD", "0x00002", "wireB")
    # if (self.col==2): draw_pe(cr, "ADDYO DADDY", "wireA", "wireB")
    # if (self.col==3): draw_pe(cr, "FOO", "wireA", "regB")
    # if (self.col==3): draw_pe(cr, "I/O", "wireA", None)
    # if (self.col==3): draw_pe(cr, "I/O", None, None)

#     (regA,regB) = (None,None)
#     if ('regA' in keywords): regA = keywords['regA']
#     if ('regB' in keywords): regB = keywords['regB']

#     inputs = True;
#     if ('inputs' in keywords): inputs = keywords['inputs']

#     if DBG:
#         if (regA == None): print "No regA"
#         else:              print "Found regA = '%s'" % str(regA)

    # Draw the main functional unit

    # (pe_w,pe_h) = (30,12)
    (pe_w,pe_h) = (PE_WIDTH,PE_HEIGHT)

    pe_linewidth   = 0.5

    headwidth   = 3    # see how it looks
    headlength  = 2 #reg_height/3

    # width and height of input registers
    reg_width  = 0.4*pe_w
    reg_height = 6 # for now, say
    reg_sep    = headlength+1 # Gap b/w reg and PE

    arrowlength = reg_height+reg_sep+2
    arrowlength_out = headlength+2
    fill        = False
    # txt_linewidth = float(pe_linewidth)/2.0
    txt_linewidth = pe_linewidth

    # pe_ulx = -w/2; pe_uly = -h/2
    centerx = CANVAS_WIDTH/2
    centery = CANVAS_HEIGHT/2
    pe_ulx = centerx - pe_w/2
    pe_uly = centery - pe_h/2

    global PE_OUTX; PE_OUTX = pe_ulx+pe_w/2
    global PE_OUTY; PE_OUTY = pe_uly+pe_h+arrowlength_out


    # FIXME this is terrible; breaks if connections happen before PE draw
    # A fix would be to do a setup_pe() call that initializes globals
    # Another fix would be to set up the globals at the beginning
    global PE_AX; PE_AX = pe_ulx+pe_w/4
    global PE_AY; PE_AY = pe_uly-arrowlength

    global PE_BX; PE_BX = pe_ulx+3*pe_w/4
    global PE_BY; PE_BY = pe_uly-arrowlength

    # Egregious hack
    if (opname == "setup_only"): return

    if (1):
        cr.save()
        # Put a big PE in the middle of the tile, with A and B inputs,
        # each w/optional input registers

        # Draw the main PE
        setcolor(cr, "black")
        cr.set_line_width(pe_linewidth)

        cr.rectangle(pe_ulx,pe_uly,  pe_w, pe_h) # pe_ulx, pe_uly, width, height

        # Add a label.  Just center it, like did w/ ghost numbers

        cr.set_font_size(0.8*pe_h)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        
        # This works, don't know why
        (text_ulx, text_uly, w, h, nextx, nexty) = cr.text_extents(opname)

        # (centerx,centery)    = (CANVAS_WIDTH/2,      CANVAS_HEIGHT/2)
        (text_ulx,text_uly)    = (CANVAS_WIDTH/2 - w/2 - text_ulx, CANVAS_HEIGHT/2 + h/2)
        cr.move_to(text_ulx,text_uly)
        cr.show_text(opname)
        cr.stroke()




        # Output arrow at w/2 on bottom
        if (1):
            cr.save()
            cr.set_line_width(txt_linewidth)
            cr.translate(PE_OUTX,PE_OUTY-arrowlength_out)
            cr.rotate(PI/2) # point DOWN
            fill = False
            draw_arrow(cr, arrowlength_out, headlength, headwidth, fill)
            cr.stroke(); cr.restore()


        # Input arrows at w/4 and 3w/4 across the top
        if (A or B):
            # setcolor(cr, 'red')
            # cr.set_line_width(txt_linewidth)
            # print "FOO " + str(pe_linewidth)
            # print "BAR " + str(txt_linewidth)
            # cr.set_line_width(0.5)


            #             cr.translate(pe_ulx,pe_uly) # UL corner of PE
            #             cr.translate(pe_w/4, -arrowlength)


            if (A):
                cr.save()
                cr.set_line_width(txt_linewidth)
                cr.translate(PE_AX,PE_AY)
                cr.rotate(PI/2) # point DOWN
                fill = False
                draw_arrow(cr, arrowlength, headlength, headwidth, fill)
                cr.stroke(); cr.restore()

            if (B):
                cr.save()
                # setcolor(cr, 'red')
                # cr.set_line_width(txt_linewidth)
                # print "FOO " + str(pe_linewidth)
                # print "BAR " + str(txt_linewidth)
                cr.set_line_width(txt_linewidth)
                # cr.set_line_width(0.5)


                #             cr.translate(pe_ulx,pe_uly) # UL corner of PE
                #             cr.translate(3*pe_w/4, -arrowlength)

                cr.translate(PE_BX,PE_BY)

                cr.rotate(PI/2) # point DOWN
                fill = False
                draw_arrow(cr, arrowlength, headlength, headwidth, fill)
                cr.stroke(); cr.restore()

        cr.stroke()
        cr.restore()

    # Draw the A/B input registers

    # draw_pe_reg(A)

    # FIXME/TODO un-nest this def maybe; requires making things global or something
    def draw_pe_reg(cr, reg, a_or_b):
        # Sample usage cases:
        #    draw_pe_reg(cr, "0x0002", "A") => Build A reg w/label "2"
        #    draw_pe_reg(cr, "regB", "B")   => build B reg, no label

        # A port is centered in left half of PE
        # B port is centered in right half of PE
        if (a_or_b == "A"): reg_ulx = pe_ulx + 1*pe_w/4 - reg_width/2
        if (a_or_b == "B"): reg_ulx = pe_ulx + 3*pe_w/4 - reg_width/2

        # Both ports are at same height
        reg_uly = CANVAS_HEIGHT/2 - pe_h/2 - reg_height - reg_sep

        # Draw register
        if (1):
            cr.save()
            setcolor(cr, 'black')
            # cr.set_line_width(.2)
            cr.set_line_width(pe_linewidth)
            cr.translate(reg_ulx,reg_uly)
            drawreg(cr, reg_width,reg_height) # pretty sure this does the stroke too
            cr.restore()

        # Draw label
        if (1):
            cr.save()
            setcolor(cr, 'black')
            font_size = 0.8*reg_height
            font_size = 0.9*reg_height

            # FIXME Assumes all constants are of the form "0x0002" else breaks
            label = ''
            if (not re.search("^reg", reg)): 
                label = str(int(reg,16))  # E.g. want "0x0002" => "2"

            # Find textbox parms
            cr.set_font_size(font_size)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            # FIXME (below)
            if (label == ''):
                msg = "WARNING neva-2 crashes when label=''; "\
                      + "changing to label=' '"
                print_once(msg)
                label = ' '
            (text_ulx, text_uly, text_w, text_h, nextx, nexty) = cr.text_extents(label)
            # print "fs=%f" % font_size

            # font_size more reliable than text_extents for textbox height!
            # text_extents("2") yields height=4, text_extents("0") gives 5(!!)
            fudge = -reg_height/4.0 # HACK ALERT!
            text_h = font_size + fudge

            # Calculate x coord of LL corner of text box
            regcenter_x = reg_ulx + reg_width/2
            textbegin_llx = regcenter_x - text_w/2 - text_ulx

            # Caclulate y coord of LL corner of text box
            regcenter_y = reg_uly + reg_height/2
            textbegin_lly = regcenter_y + text_h/2 # + text_h + text_uly/2

            # drawdot(cr, textbegin_llx, textbegin_lly, 'blue')

            cr.move_to(textbegin_llx, textbegin_lly)
            cr.show_text(label)
            cr.stroke();
            cr.restore()

    if (A and re.search("^[0-9r]",A)): draw_pe_reg(cr, A, "A")
    if (B and re.search("^[0-9r]",B)): draw_pe_reg(cr, B, "B")

def drawtileno(cr, tileno):

    cr.save()
    # stoopid keywords ghost number ghost-number ghost_number
    # Put a big ghost number in top-left corner of tile
    # See https://www.cairographics.org/manual/cairo-text.html#cairo-text-extents

    # Needs to be a string.
    tileno = str(tileno)

    # Ghost color= light gray
    # setcolor(cr, 'ghostgray')

    graylevel = 0.5; cr.set_source_rgb(graylevel,graylevel,graylevel)

    cr.set_font_size(20)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    # E.g. cr.text_extents("100") => (3, -15, 38, 15, 42, 0) => (UL(x,y), w, h, begin_next(x,y)
    # print cr.text_extents(tileno)
    (text_ulx, text_uly, text_w, text_h, nextx, nexty) = cr.text_extents(tileno)

#     # For centered text
#     centerx = CANVAS_WIDTH/2
#     centery = CANVAS_HEIGHT/2
# 
#     x = centerx - text_w/2 - text_ulx
#     y = centery + text_h/2

    # For left-justified
    x = PORT_LENGTH + 0.5*text_h; y = PORT_LENGTH + 1.5*text_h


    # cr.set_source_rgb(1,0,0); drawdot(cr, centerx, centery, 'red'
    # cr.set_source_rgb(0,0,1); drawdot(cr, x+text_ulx, y+text_uly, 'blue')
    # cr.set_source_rgb(1,0,1); drawdot(cr, x, y, 'purple')

    cr.move_to(x,y)
    cr.show_text(tileno)
    cr.stroke()

    # Also useful to print out (r,c)
    cr.set_font_size(12)
    cr.move_to(x,y+15)
    cr.show_text("%d,%d" % tileno2rc(tileno))
    cr.stroke()

    cr.restore()

# Draw tile outline
def drawtile(cr):
    cr.save()
    setcolor(cr,'black')
    cr.set_line_width(.5)
    w = CANVAS_WIDTH  - 2*PORT_HEIGHT
    h = CANVAS_HEIGHT - 2*PORT_HEIGHT
    (ULx,ULy) = (PORT_HEIGHT,PORT_HEIGHT)
    cr.rectangle(ULx,ULy,  w, h) # ULx, ULy, width, height
    cr.stroke()
    cr.restore()

# Draw memtile outline
def drawmemtile(cr):
    cr.save()
    setcolor(cr,'black')
    cr.set_line_width(.5)
    (ULx,ULy) = (PORT_HEIGHT,PORT_HEIGHT)
    w = CANVAS_WIDTH  - 2*PORT_HEIGHT
    h = 2*CANVAS_HEIGHT - 2*PORT_HEIGHT
    cr.rectangle(ULx,ULy,  w, h) # ULx, ULy, width, height
    cr.stroke()
    cr.restore()

# E.g. ab_connect(cr, "in_s3t0", "wireA")
def ab_connect(cr, inport, PE_input):
    DBG=1;
    if (TILES_DRAWN_AT_LEAST_ONCE): DBG=0

    if DBG: print "AB connecting wire '%s' to pe_in wire '%s'" % (inport, PE_input)
    (x1,y1) = connectionpoint(inport)

    if (PE_input == "wireA"): (x2,y2) = (PE_AX,PE_AY)
    else:                     (x2,y2) = (PE_BX,PE_BY)

    drawport(cr, inport)

    # FIXME/TODO:
    # Parms (blue, .5 etc.) should be global and shared w/ manhattan_connect etc. below
    if (1):
        cr.save()
        setcolor(cr,'blue')
        cr.set_line_width(.5)
        drawdot(cr,x2,y2,'blue')
        cr.move_to(x1,y1)
        cr.line_to(x2,y2)
        cr.stroke()
        cr.restore()

def pe_out_connect(cr, outport):
    (x1,y1) = (PE_OUTX,PE_OUTY)
    (x2,y2) = connectionpoint(outport)

    drawport(cr, outport, options='reg');

    # FIX<E/TODO should be shared w/other connect routines!
    if (1):
        cr.save()
        setcolor(cr,'blue')
        cr.set_line_width(.5)
        drawdot(cr,x2,y2,'blue')
        cr.move_to(x1,y1)
        cr.line_to(x2,y2)
        cr.stroke()
        cr.restore()


# def manhattan_connect(cr, xy1, xy2):
def manhattan_connect(cr, outport, inport):


    # BACKWARDS: outport="out_s2t0" inport="in_s3t0"


#     cr.save()
#     (x,y) = connectionpoint("out_s2t0")
#     drawdot(cr,x,y,'red')
#     cr.stroke(); cr.restore()


    # Given two points (x1,y1) and (x2,y2) on tile edge, draw
    # a manhattan connection through the interior of the tile.
    # Put a dot at the corner when the wire turns (you'll thank me later)

#     x1 = xy1[0]; y1 = xy1[1]
#     x2 = xy2[0]; y2 = xy2[1]

    (x1,y1) = connectionpoint(outport)
    (x2,y2) = connectionpoint(inport)

    # Only draw non-ghost ports if connections exist.
    drawport(cr, outport, options='reg');    drawport(cr, inport)

    # drawdot(cr,x1,y1,'red'); drawdot(cr,x2,y2,'red')

    # Find internal join point
    # x1 == +/- PORT_HEIGHT means x1 is an edge and x2 is interior
    if   (x1 ==  PORT_HEIGHT): interior = (x2,y1)
    elif (x1 == -PORT_HEIGHT): interior = (x2,y1)
    else:                      interior = (x1,y2)

    # if (outport == "sb_wire_out_1_BUS16_3_0"): print "FOO1 interior = %s" % str(interior)

    # Maybe it works better if join point goes a little bit in toward the
    # two respective incoming sides
    
    k=2
    sx1 = k*x1/abs(x1) # sign(x1)
    sx2 = k*x2/abs(x2) # sign(x2)

    sy1 = k*y1/(y1) # sign(y1)
    sy2 = k*y2/(y2) # sign(y2)

    if   (abs(x1) ==  PORT_HEIGHT): interior = (x2-sx1,y1+sy2)
    else:                           interior = (x1-sx2,y2-sy1)

    (join_x,join_y) = (0,0)

    k=PORT_WIDTH/3.0
    l_edge = PORT_HEIGHT
    r_edge = CANVAS_WIDTH-PORT_HEIGHT
    t_edge = PORT_HEIGHT
    b_edge = CANVAS_HEIGHT-PORT_HEIGHT
    if   (x1 == x2):     join_x = x1
    elif (x1 == l_edge): join_x = x2-k
    elif (x1 == r_edge): join_x = x2+k
    elif (x2 == l_edge): join_x = x1-k
    elif (x2 == r_edge): join_x = x1+k

    if   (y1 == y2):     join_y = y1
    elif (y1 == t_edge): join_y = y2-k
    elif (y1 == b_edge): join_y = y2+k
    elif (y2 == t_edge): join_y = y1-k
    elif (y2 == b_edge): join_y = y1+k

    interior = (join_x,join_y)

    # if (outport == "sb_wire_out_1_BUS16_3_0"): print "FOO2 interior = %s" % str(interior)
    # if (outport == "sb_wire_out_1_BUS16_3_0"):
    #     print "begin here: %s" % str((x1,y1))
    #     print "then  here: %s" % str(interior)
    #     print "end   here: %s" % str((x2,y2))

    # FIXME hackity hack hack hack FIXME
    # hack for when a lower wire connects to an upper wire in a memory tile
    # omg i'm losing it
    # if (interior[1] == 0): interior[1] = CANVAS_HEIGHT
    # FIXME "TypeError: object does not support item assignment" on neva-2!!?
    interior_x = interior[0]; interior_y = interior[1]
    if (interior_y == 0):
        # print "interor y = zero means a mem-sb1 connection"
        # print "inport '%s' => outport '%s' in tile %d" % (inport, outport, CUR_TILENO)

        (y1_prev,y2_prev) = (y1,y2)
        if re.search("^sb_wire_in_1_", outport):
            y1 -= PORT_HEIGHT
            # print "subtracting from y1 was %d now %d" % (y1_prev,y1)
        elif re.search("^sb_wire_out_1_", inport):
            y2 -= PORT_HEIGHT
            # print "subtracting from y2 was %d now %d" % (y2_prev,y2)

        # FIXME this could be better
        (interior_x,interior_y) = (x1,y1)
        # print ""

    # Okay now connect the dots!  With a blue line.
    # Put a blue dot at the corner.  You'll thank me later.
    # TODO if (isbus): linewidth = 1 etc.
    if (1):
        cr.save()
        setcolor(cr,'blue')
        cr.set_line_width(.5)
        # drawdot(cr,interior[0],interior[1],'blue')
        cr.move_to(x1,y1)
        cr.line_to(interior_x,interior_y)
        cr.line_to(x2,y2)
        cr.stroke()
        cr.restore()

def get_connection_type(c):
    # connection type will be one of "port" "pe_in" "pe_out" "const"

    # Okay right order matters, this one should go before pe_in search obviously
    # ?? What idiot is writing these comments!!???  Oh wait it's me

    # if re.search(",",c): return "pe"
    # if re.search("^[oi],*",c): return "port"
    # if re.search("wire.|reg.",c): return "pe_in"

    # For connections of the form "MUL(wireA,regB)" or "MUL(wireA,0x0002)"
    # parse = re.search("^(.*).(wire.|reg.|[0-9].*),(wire.|reg.|[0-9].*)", connection)
    type = "unknown"
    if   (c == "pe_out"):           type = "pe_out"
    elif re.search(",",c):          type = "pe"
    elif re.search("^[oi],*",c):    type = "port"
    elif re.search("^sb_wire_[oi],*",c):    type = "port"
    elif re.search("wire.|reg.",c): type = "pe_in"
    elif re.search("^0x",c):        type = "const"

    # FIXME/hack map din == pe_in for now, but it be UUUUGLYYYY etc.
    elif (c == "din"):
        type = "pe_in"
        print_once( "\nWARNING MEMHACK modeling '%s' as '%s'" % (c, type) )
    elif (c == "mem_out"):
        type = "pe_out"
        print_once( "\nWARNING MEMHACK modeling '%s' as '%s'" % (c, type) )
    else:
        print "ERROR Unknown type for connection '%s'" % c
        # I'll probably regret this...
        sys.exit(-1)

    DBG=0
    if DBG: print "GCT connection '%s' = type '%s'" % (c, type)
    return type


def connectwires(cr, connection):

    # Draw a manhattan blue line connecting the two indicated ports inside a tile
    # I've given a lot of leeway as to how connections are specified.
    # E.g. these should all work for connection parm:
    #     "in_s3t0 => out_s2t3"
    #     "in_s3t0 out_s2t3"
    #     "in_s3t0 connects to out_s2t3"
    #     "  in_s3t0 connects to out_s2t3  "
    #     "wireA <= in_s3t0"
    #     "pe_out <= MUL(wireA,wireB)"
    #     "pe_out <= ADD(0x0002,0x0000)"


    DBG = 0;

    # Find the names of the two wires to connect.
    # parse = re.search( "([A-z_0-9]+).*[^A-z_0-9]([A-z_0-9]+)[^A-z_0-9]*$", connection)

    # A better way?
    connection = connection.strip() # Eliminate leading/trailing space

    # parse = re.search("^(o[^ ]*) .* (i[^ ]*)$", connection)
    parse = re.search("^([^ ]*) .* ([^ ]*)$", connection)
    pto = parse.group(1); pfrom = parse.group(2)

    # Some quick rewrites for the new mem tiles
    # E.g. 'out_0_BUS16_3_0 should I THINK be same as out_s3t0
    pto   = quickfix(pto)
    pfrom = quickfix(pfrom)

    # connection type will be one of "port" "pe_in" "pe_out" "const" (more?)

    to_type   = get_connection_type(pto)
    from_type = get_connection_type(pfrom)
        
    if DBG: print "CONNECT to '%s' from '%s'" % (pto,pfrom)

#     if (pfrom == 'mem_out'):
#         print "FOO okay found FROM 'mem_out' type '%s' in tile %d" % (from_type,CUR_TILENO)
#         print "FOO connects TO '%s' type '%s'" % (pto, to_type)

    DBG=0
    if (DBG>1): print "FOO1 %s - %s" % (to_type, from_type)
    # For connections of the form "out_s0t0 <= in_s1t0"
    if (to_type == "port" and from_type == "port"):
        w1 = pto; w2 = pfrom
        if DBG:
            print "CW connection = " + connection
            print "CW connecting wires '%s' and '%s'\n" % (w1,w2)

        # Draw a blue rectilinear line connecting w1 and w2 ports
        manhattan_connect(cr, pto, pfrom)
        return True;

    if (DBG>1): print "FOO2 %s - %s" % (to_type, from_type)
    # For connections of the form "wireA <= in_s3t0"
    if (to_type == "pe_in" and from_type == "port"):
        DBG=0
        if DBG: print "CW found valid connection %s" % connection
        if DBG: print "CW connecting port '%s' to pe_in '%s'" % (pfrom,pto)
        ab_connect(cr, pfrom, pto)
        return True;

    if (DBG>1): print "FOO3 %s - %s" % (to_type, from_type)
    # For connections of the form "out_s1t0 <= pe_out"
    if (to_type == "port" and from_type == "pe_out"):
        DBG = 0;
        if DBG: print "CW/pe_out found valid connection %s" % connection
        pe_out_connect(cr, pto)
        return True;

    if (DBG>1): print "FOO4 %s - %s" % (to_type, from_type)
    # For connections of the form "pe_out <= MUL(wireA,regB)" or "pe_out <= MUL(wireA,0x0002)"
    # parse = re.search("^(pe_out) .* (.*).(wire.|reg.|[0-9].*),(wire.|reg.|[0-9].*)", connection)
    if (from_type == "pe"):
        DBG = 1;
        if (TILES_DRAWN_AT_LEAST_ONCE): DBG=0
        if DBG: print "CW/pe found valid connection %s" % connection
        parse = re.search("^(.*)[(](wire.|reg.|[0-9].*),(wire.|reg.|[0-9].*)[)]", pfrom)
        pe_name = parse.group(1)
        pe_a    = parse.group(2)
        pe_b    = parse.group(3)
        if DBG: print "Found PE '%s' w/ inputs a='%s' b='%s'" % (pe_name,pe_a,pe_b)

        draw_pe(cr, pe_name, pe_a, pe_b)
        return True

        # TODO: draw_pe(pe_name) etc.
#             if (self.col==0): draw_pe(cr, "ADD", regA=2, regB=0)

    else:
        # print "ERROR Do not understand connection %s (yet)" % connection
        return False



# FIXME/TODO Not used presently I think.  Do we keep it?
def drawgrid(cr):

    cr.save()

    cr.set_line_width(.1)
    # cr.set_dash((1,1), 0) # on/off array, length of dashes, begin
    b = 0.8 # brightness
    # cr.set_source_rgb(b,b,0) # ghostly yellow
    # cr.set_source_rgb(0,0,0)
    setcolor(cr,'black') # black for debug

    ntracks_v = NTRACKS_PE_BUS_V + NTRACKS_PE_WIRE_V
    ntracks_h = NTRACKS_PE_BUS_H + NTRACKS_PE_WIRE_H
    pwid = PORT_WIDTH; plen = PORT_HEIGHT

    # NW corner
    print "Drawing NW corner"
    cr.rectangle(0,0,  plen,plen) # ULx, ULy, width, height
    # cr.stroke()

    # 2nh+3 port boxes
    nboxes = 3 + 2 * ntracks_h;
    print "Drawing %d port boxes" % nboxes
    print "plen = %d, pwid = %d" % (plen,pwid)
    cr.move_to(0,0)
    for i in range (0, nboxes):
        (ULx,ULy) = (0, plen + i * pwid)
        # print "Box %2d at %d,%d  %d,%d" % (i, ULx, ULy, LRx,LRy)
        cr.rectangle(ULx, ULy, plen,pwid) # ULx, ULy, width, height

    ULx = 0;  ULy = plen
    for i in range (0, nboxes):
        print "Box %2d at %d,%d" % (i, ULx, ULy)
        cr.rectangle(ULx, ULy, plen,pwid) # ULx, ULy, width, height
        ULy = ULy + pwid
    # cr.stroke()

    # SW corner
    print "Drawing NW corner"
    cr.rectangle(ULx,ULy,  plen,plen) # NW(x,y),  SE(x,y)
    cr.stroke()

    cr.restore()

def draw_all_ports(cr):
    for side in (0,1,2,3):
        for dir in ("out", "in"):
            if (side%2 == 0): ntracks = NTRACKS_PE_BUS_H + NTRACKS_PE_WIRE_H; # EW
            if (side%2 == 1): ntracks = NTRACKS_PE_BUS_V + NTRACKS_PE_WIRE_V; # NS
            for track in range(0,ntracks):
                wirename = "%s_s%dt%d" % (dir, side, track)
                drawport(cr, wirename, options="ghost")

# Invaluable cairo drawing reference:
# http://pygtk.org/articles/cairo-pygtk-widgets/cairo-pygtk-widgets.htm
# Looks good but did not use: http://zetcode.com/gui/pygtk/
# Ditto for: http://pygtk.org/pygtk2tutorial/ch-DrawingArea.html

def draw_handler(widget, cr):
    global CUR_DRAW_WIDGET; CUR_DRAW_WIDGET = widget;

    # FIXME probably don't need "cr" parm (above) anymore!
    context = widget.window.cairo_create()
    cr = context

    global ZOOMTILE; tileno = ZOOMTILE
    if (tileno == -1):   draw_all_tiles(cr);
    else:                draw_one_tile(cr, tileno);

def set_zoom_scale_factor():

    global CUR_SCALE_FACTOR;
    
    # OLD: Draw at 4x requested size; CUR_SCALE_FACTOR = 4
    # NEW:
    #   For now, unzoomed (grid) view is scaled to 2x (USF=2).
    #   And zoomed (onetile) view is 2x of that.  Ish.
    #   Except that, for no good reason, want the zoomed tile
    #   to occupy the same space as four unzoomed tiles.

    # Canvas width = tile width + length of ports on each side
    # In zoomed view, want width of one tile to match
    # (two tiles + gap) in unzoomed (2x) view
    # unzoomed_scale_factor = 2 # Scale factor for unzoomed tiles
    unzoomed_scale_factor = 1/INIT_SCALE_FACTOR # Scale factor for unzoomed tiles
    tile_width            = CANVAS_WIDTH - 2*PORT_WIDTH
    two_tiles_plus_gap_2x = (2*tile_width + 2*PORT_LENGTH)*unzoomed_scale_factor
    fudge                 = .09 # yeah I dunno whatevs OCD OKAY?
    CUR_SCALE_FACTOR = float(two_tiles_plus_gap_2x)/float(tile_width) + fudge

def draw_one_tile(cr, tileno):

    # Save
    global CUR_SCALE_FACTOR;
    save_scale_factor = CUR_SCALE_FACTOR
    cr.save()

    # scalefactor = 10 # zoom in for debugging
    # cr.scale(scalefactor,scalefactor)

    ########################################################################
    # Scale and translate


    set_zoom_scale_factor()
    cr.scale(CUR_SCALE_FACTOR,CUR_SCALE_FACTOR)

    if (0): print "Zoom scale factor %d/%d = %f." \
        % (two_tiles_plus_gap_2x, tile_width, CUR_SCALE_FACTOR)

    ########################################################################
    # OLD: cr.translate(ARRAY_PAD, ARRAY_PAD)
    # NEW: -----------------------------------------------------------------
    # Translate so that zoomed tile corners match unzoomed tile corners
    # Unzoomed corners were centered in window, and above scaling (supposedly)
    # ensures that zoomed corners are same distance apart as unzoomed,
    # so: should suffice to make sure zoomed corners are centered.

    # Things that were 40px wide in unzoomed view are now just 10px wide ish
    scaled_win_width    = WIN_WIDTH/CUR_SCALE_FACTOR
    scaled_canvas_width = CANVAS_WIDTH
    print "sww=%0.2f scw=%0.2f" % (scaled_win_width,scaled_canvas_width)
    xmargin = (scaled_win_width - scaled_canvas_width)/2
    ymargin = xmargin
    cr.translate(xmargin, ymargin)

    # Okay done with scale and translate.  Now draw!
    if (0): print "...at scale factor %f." % CUR_SCALE_FACTOR
    TILE_LIST[tileno].draw(cr)

    # Restore
    cr.restore()
    CUR_SCALE_FACTOR = save_scale_factor

global TILES_DRAWN_AT_LEAST_ONCE           # FIXME Yes this is awful
TILES_DRAWN_AT_LEAST_ONCE = False          # FIXME Yes this is awful
def draw_all_tiles(cr):
    DBG=0
    if DBG: print "Draw all tiles!"

    cr.save()
    cr.translate(ARRAY_PAD, ARRAY_PAD)     # Whitespace margin at top and left
    cr.scale(CUR_SCALE_FACTOR,CUR_SCALE_FACTOR)
    # draw_big_ghost_arrows(cr)            # Big ghost arrows in background of grid
                                           # view show general flow dir for tracks
    for tile in TILE_LIST:                 # Draw ALL the tiles
        if (tile): tile.draw(cr)           # uh...unless they don't exist :)

    global TILES_DRAWN_AT_LEAST_ONCE      # FIXME Yes this is awful
    TILES_DRAWN_AT_LEAST_ONCE = True      # FIXME Yes this is awful
    cr.restore()

def test_ports():  # Meh

    cr.save()
    cr.translate(ARRAY_PAD, ARRAY_PAD); cr.scale(2,2)
    if (0):
        drawport(cr, "in_s0t0", options="foo,bar,baz")
        drawport(cr, "out_s0t0", options="foo")

        drawport(cr, "in_s0t1")

        drawport(cr, "out_s1t0")
        drawport(cr, "in_s1t0")

        drawport(cr, "out_s2t0")
        drawport(cr, "in_s2t0")

        drawport(cr, "out_s3t0")
        drawport(cr, "in_s3t0")

    if (0):
        draw_all_ports(cr)

    tile = TILE_LIST
    tile[0].draw(cr)
    tile[1].draw(cr)
    tile[2].draw(cr)
    tile[3].draw(cr)

def get_cursor_magplus():

    xpm_data = [
        "15 15 3 1",
        "       c None",
        ".      c #000000000000",
        "X      c #FFFFFFFFFFFF",
        "               ",
        "               ",
        "               ",
        "               ",
        "      . .      ",
        "    .     .    ",
        "   .   .   .   ",
        "   .  ...  .   ",
        "   .   .   .   ",
        "    .     .    ",
        "      . . .    ",
        "           .   ",
        "            .  ",
        "             . ",
        "               "
        ]

    pixbuf = gtk.gdk.pixbuf_new_from_xpm_data (xpm_data)
    display = gtk.gdk.display_get_default()
    magplus = gtk.gdk.Cursor(display, pixbuf, 07, 7)
    global CUR_CURSOR
    CUR_CURSOR = 'magplus'
    return magplus

def get_cursor_magminus():

    xpm_data = [
        "15 15 3 1",
        "       c None",
        ".      c #000000000000",
        "X      c #FFFFFFFFFFFF",
        "               ",
        "               ",
        "               ",
        "               ",
        "      . .      ",
        "    .     .    ",
        "   .       .   ",
        "   .  ...  .   ",
        "   .       .   ",
        "    .     .    ",
        "      . . .    ",
        "           .   ",
        "            .  ",
        "             . ",
        "               "
        ]

    pixbuf = gtk.gdk.pixbuf_new_from_xpm_data (xpm_data)
    display = gtk.gdk.display_get_default()
    magminus = gtk.gdk.Cursor(display, pixbuf, 07, 7)
    global CUR_CURSOR
    CUR_CURSOR = 'magminus'
    return magminus

# TODO someday maybe
# A GdkWindow is a rectangular region on the screen. It's a low-level
#  object, used to implement high-level objects such as
# GtkWidget and GtkWindow on the GTK+ level. A GtkWindow is a toplevel
# window, the thing a user might think of as a "window" with a titlebar
# and so on; a GtkWindow may contain many GdkWindow.

# https://en.wikibooks.org/wiki/PyGTK_For_GUI_Programming/First_Steps

# The gtk.VBox object can contain and organize multiple widgets into a
# Vertical column. Similarly, the gtk.HBox object is also available,
# organizing its child widgets into a Horizontal row. To create more
# sophisticated layouts, you can nest the container objects, i.e. have a
# gtk.HBox inside a gtk.VBox.

# class CGRAWin(Gtk.Window):
class CGRAWin(gtk.Window):
    def __init__(self):
        DBG = 2

        # Set up the main window and connect to callback routine that draws everything.
        # See above for definition of globals WIN_WIDTH, WIN_HEIGHT

        title = "Tilesy" # haha LOL
        gtk.Window.__init__(self)
        self.props.title = title
        self.props.width_request = WIN_WIDTH
        self.props.height_request= min(WIN_HEIGHT,600)

        # FIXME minimum width (above) should be based on screen height,
        # not just an arbitrary 600.
        # FIXME2 currently cannot resize window below requested w,h...why?

        global ZOOMTILE; ZOOMTILE = -1 # Always start zoomed OUT

        da = Gtk.DrawingArea()
        da.props.width_request = WIN_WIDTH
        da.props.height_request= WIN_HEIGHT
        # self.add(da)

        #         def focus_in(widget, event, adj):
        #             global ADJ; adj = ADJ
        #             adj.set_value(200.0)
        #             adj.value_changed()

        # White background for better contrast / less ink wastage when printing
        MAXCOLOR = 65535
        col = gtk.gdk.Color(MAXCOLOR,MAXCOLOR,MAXCOLOR)
        # col = gtk.Color('#fff') WRONG
        # col = gtk.gdk.Color('#fff') # fails on neva2
        da.modify_bg(gtk.STATE_NORMAL, col)

        ########################################################################
        # To toolbar FIXME should be separate function maybe
        # top_toolbar = build_toolbar()
        # def build_toolbar():

        # How to add icon images to buttons
        # https://stackoverflow.com/questions/2188659/stock-icons-not-shown-on-buttons

        # BUTTON: zoom-in magnifying glass
        # button_magplus = gtk.Button("+")
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_ZOOM_IN, gtk.ICON_SIZE_SMALL_TOOLBAR)
        image.show()
        #
        button_magplus = gtk.Button()
        button_magplus.add(image)
        button_magplus.connect("clicked", self.button_magplus_action)
        button_magplus.show()
        
        # BUTTON: zoom-out magnifying glass
        # button_magminus= gtk.Button("-")
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_ZOOM_OUT, gtk.ICON_SIZE_SMALL_TOOLBAR)
        image.show()
        #
        button_magminus= gtk.Button()
        button_magminus.add(image)
        button_magminus.connect("clicked", self.button_magminus_action)
        button_magminus.show()

        # BUTTON: misc TBD
        button_arrow   = gtk.Button("no zoom")
        button_arrow.connect("clicked", self.button_arrow_action)
        button_arrow.show()

        button_hand    = gtk.Button("grabby hand")

        # BUTTON: exit
        button_exit   = gtk.Button("exit")
        button_exit.connect("clicked", self.button_exit_action)
        button_exit.show()


        # Pack buttons into a toolbar on top
        expand = False; fill = False;
        top_toolbar = gtk.HBox()
        # neva-2 wants height 30; kiwi is happy with 25 FIXME
        top_toolbar.props.height_request = 30
        top_toolbar.pack_start(button_magplus,  expand, fill)
        top_toolbar.pack_start(button_magminus, expand, fill)
        top_toolbar.pack_start(button_arrow,    expand, fill)
        top_toolbar.pack_start(button_hand,     expand, fill)
        top_toolbar.pack_start(button_exit,     expand, fill)
        # print dir(top_toolbar.props)
        ########################################################################

        # Create a new scrolled window.
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolled_window.add_with_viewport(da)
        scrolled_window.show() # FIXME What does this do??  Is it necessary?
        da.show()              # FIXME What does this do??  Is it necessary?
        
        vbox = gtk.VBox()
        vbox.pack_start(top_toolbar, expand, fill)
        vbox.pack_start(scrolled_window, True, True, 0)
        self.add(vbox)

        global SW
        SW = scrolled_window
        # scrolled_window = gtk.ScrolledWindow()
        adj = scrolled_window.get_vadjustment()
        # ... create child widget
        # da.connect('focus_in_event', focus_in, adj)
        # self.connect('focus_in_event', focus_in, adj)



        self.show()

        #       if (0):
        #           # Cannot set cursor until after show()!!
        #           # Change the cursor to a awful watch thing
        #           watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
        #           self.window.set_cursor(watch)
        #           sys.stdout.flush(); traceback.print_stack(); sys.stderr.flush()

        # A dumb way to keep track of the current window and drawing area widget
        # global CUR_WINDOW;      CUR_WINDOW = win;
        global CUR_DRAW_WIDGET; CUR_DRAW_WIDGET = da;
        
        # Some/all of this maybe doesn't belong in win init,
        # but oh well here it is for now anyway

        # win = self

        # "draw" event results in drawing everything on drawing area 'da'
        # draw_handler_id = da.connect("draw", draw_handler)
        draw_handler_id = da.connect("expose-event", draw_handler)

        # https://stackoverflow.com/questions/23946791/mouse-event-in-drawingarea-with-pygtk
        # http://www.pygtk.org/pygtk2tutorial/sec-EventHandling.html
        button_press_handler_id = da.connect("button-press-event", button_press_handler)

        # FIXME/TODO add to 0bugs and/or 0notes: gtk.gdk.BUTTON_PRESS_MASK = Gdk.EventMask.BUTTON_PRESS_MASK
        # da.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        # da.set_events(gtk.gdk.EventMask.BUTTON_PRESS_MASK)
        da.set_events(gtk.gdk.BUTTON_PRESS_MASK)

        self.connect("delete-event", Gtk.main_quit)

        # https://stackoverflow.com/questions/6718586/pygtk-hide-cursor
        # As stated in the PyGTK FAQ, you should set the cursor on the
        # realize signal. If you don't wait for the realize signal,
        # the gtk.gdk.window hasn't been created yet, so you can't
        # change the cursor.
        # 
        # self.connect("realize", self.realize_cb)
        # def realize_cb(self, widget): set_cursor()

    def button_arrow_action(widget, event):
        # Reset cursor back to normal (arrow)
        widget.window.set_cursor(None)
        global CUR_CURSOR
        CUR_CURSOR = 'arrow'

        # c = gtk.gdk.Cursor(gtk.gdk.ARROW)
        # widget.window.set_cursor(c)

    def button_magplus_action(widget, event):
        # OLD: zoom('in')
        c = get_cursor_magplus()
        widget.window.set_cursor(c)

    def button_magminus_action(widget, event):
        # OLD: zoom('out')
        c = get_cursor_magminus()
        widget.window.set_cursor(c)

    def button_exit_action(widget, event):
        Gtk.main_quit()

def adjust_scrollbar(adj, amt):
    ps = adj.page_size

    adj.set_value(amt)

    u = adj.upper; l = adj.lower; v = adj.value
    # print "AFTER  lvu = (%4d-> %4d    <-%-4d)" % (int(l), int(v), int(u))
    print "[%4d|-> %4d   <-|%-4d]" % (int(l), int(v), int(u))
    print "PAGESIZE %d" % ps
    
def recenter(x,y):
    global SW; # adj = SW.get_vadjustment()

    #     print "ALLOCX", ; print SW.get_allocation().x
    #     print "ALLOCY", ; print SW.get_allocation().y
    # 
    #     print "ALLOCX_DA", ; print CUR_DRAW_WIDGET.get_allocation().x
    #     print "ALLOCY_DA", ; print CUR_DRAW_WIDGET.get_allocation().y

    global ACTUAL_SCALE
    (hprev,w) = CUR_DRAW_WIDGET.get_size_request()
    baked_in_fudge_factor = 2 # FIXME!!!
    sf = 1.2
    csf = float(CUR_SCALE_FACTOR * sf)
    h = int(WIN_HEIGHT * csf * baked_in_fudge_factor)
    ACTUAL_SCALE = float(h)/float(hprev)

    net_scale = (CUR_SCALE_FACTOR / INIT_SCALE_FACTOR)

    print ""
    print "clicked x = ", ; print x
    print "scale factor = ", ; print CUR_SCALE_FACTOR
    print "base zoom = ", ; print INIT_SCALE_FACTOR
    print "net scale = ", ; print net_scale
    print "actual scale = ", ; print ACTUAL_SCALE
    print "final factor? = ", ; print ACTUAL_SCALE/1.2


    xadj = x

    # I think maybe the "10" comes from "scrolled_window.set_border_width(10)"
    xadj = x*1.2-10 # PERFECT!!!!  NO MUCKIN'!!!
    print "ADJUSTING BY %f (minus half pagesize)" % xadj
    page_size = SW.get_hadjustment().page_size
    adj = SW.get_hadjustment()
    adjust_scrollbar(adj, xadj - page_size/2)
    print ""
    # THIS CAUSES REDRAW even though a zoom is coming...
    # adj.value_changed()
    return

#     ZU2 = SW.get_hadjustment().upper
#     print "post-zoom hupper = " + str(ZU2)
#     print "sf = " + str(ZU2/ZU1)
#     print ""

#     xadj = x # Not quite enough...
#     xadj = x*0.8 # nope
#     xadj = x*0.5 # Nope still too much
#     xadj = x/net_scale # Nope still too much
#     xadj = 0.5*x/net_scale
#     xadj = x*1.2 # Just the tiniest bit too much
#     xadj = x*ACTUAL_SCALE  # Pretty close? but needs just a tad more...
#     xadj = (x/ACTUAL_SCALE)/1.2
#     xadj = xnew
#     xadj = x
# 
#     return
# 
#     global CUR_SCALE_FACTOR
# 
#     print "HADJUST",
#     # adjust_scrollbar(SW.get_hadjustment(), x)
#     adjust_scrollbar(SW.get_hadjustment(), x_scaled)
# 
#     print "VADJUST",
#     adjust_scrollbar(SW.get_vadjustment(), y)

def zoom(in_or_out):
    if (in_or_out == 'in' ): sf = 1.2
    if (in_or_out == 'out'): sf = 0.8

    global CUR_SCALE_FACTOR
    print "magplus! 1 scale factor now %s" % str(CUR_SCALE_FACTOR)
    # CUR_SCALE_FACTOR = round(CUR_SCALE_FACTOR * sf, 1)
    CUR_SCALE_FACTOR = float(CUR_SCALE_FACTOR * sf)
    
    (h,w) = CUR_DRAW_WIDGET.get_size_request()
    hprev = h
    global HPREV
    HPREV = h

    global ZU1
    ZU1 = SW.get_hadjustment().upper
    print "pre-zoom hupper = " + str(ZU1)


    print "FOO h=%d w=%d" % (h,w)
    print "Drawing area size(%d,%d) " % (h,w),
    baked_in_fudge_factor = 2 # FIXME!!!

    h = int(WIN_HEIGHT * CUR_SCALE_FACTOR * baked_in_fudge_factor)
    w = int(WIN_WIDTH  * CUR_SCALE_FACTOR * baked_in_fudge_factor)

#     h = float(WIN_HEIGHT * CUR_SCALE_FACTOR * baked_in_fudge_factor)
#     w = float(WIN_WIDTH  * CUR_SCALE_FACTOR * baked_in_fudge_factor)

    global HNEW
    HNEW = h

    CUR_DRAW_WIDGET.set_size_request(h, w)
    print "=> (%d,%d)" % (h,w)

    global ACTUAL_SCALE; ACTUAL_SCALE = float(h)/hprev
    print "SF " + str(ACTUAL_SCALE)

    
def zoom_to_tile(event):
    DBG = 0

    # Need to know current scale factor so we keep track of it in a global
    print ""
    print "CUR_SCALE_FACTOR %s" % CUR_SCALE_FACTOR
    print ""

    # Can't get scale factor from context matrix, it's always (1,0,0,1,0,0) why?
    if (0): print "matrix = " + str(DRAW_HANDLER_CR.get_matrix())

    # x,y coordinates of button-press
    x = event.x; y = event.y
    if DBG: print "%d %d" % (x,y)

    # Subtract off the scale-independent paddings and divide by scale factor I guess
    x = (x - ARRAY_PAD)/CUR_SCALE_FACTOR; y = (y - ARRAY_PAD)/CUR_SCALE_FACTOR;
    if DBG: print "Transformed x,y = (%d,%d)" % (x,y)
    if DBG: print "CANVAS_WIDTH = %d" % CANVAS_WIDTH

    # Find row, col of tile indicated by sclaed/translated (x,y)
    row = y/CANVAS_WIDTH; col = x/CANVAS_HEIGHT;
    row = int(row); col = int(col)

    # Find tile number indicated by (row,col)
    tileno = rc2tileno(row,col)

    print "I think this is tile %d (r%d,c%d)" % (tileno, row,col)

    # If already zoomed out (ZOOMTILE === -1), zoom in to tile indicated.
    # Otherwise, zoom out.
    global ZOOMTILE;
    if (ZOOMTILE == -1):
        if DBG: print "Zoom in to tile %s!" % str(tileno)
        ZOOMTILE = tileno;
    else:
        if DBG: print "Zoom out!"
        ZOOMTILE = -1;

    # Redraw after zoom
    # CUR_DRAW_WIDGET.queue_draw()

def button_press_handler(widget, event):
    if event.type == gtk.gdk.BUTTON_PRESS:   print " single click "
    if event.type == gtk.gdk._2BUTTON_PRESS: print " double click "

    print "CC='%s'" % CUR_CURSOR

    if (CUR_CURSOR == 'magplus'):

        global ZU1
        ZU1 = SW.get_hadjustment().upper
        # recenter(100,0)
        # recenter(event.x,event.y)

        zoom('in')

        # FIXME how many of these (redraws) are there?
        # Redraw after zoom
        # CUR_DRAW_WIDGET.queue_draw()
        # gtk.gdk.flush()

        # All this (below) will move to / replace what's in recenter()

        # print "about to adjust..."
        # sys.stdout.flush()
        # time.sleep(2)

        SW.hide()
        adj = SW.get_hadjustment()
        page_size = adj.page_size
        adjust_scrollbar(adj, (1.2*event.x-10) - page_size/2)
        SW.show()

        return

    if (CUR_CURSOR == 'magminus'):
        zoom('out')
        return

    # ZOOM TO TILE (ugh FIXME should be a separate routine)
    # Only zoom on 1) normal (arrow) cursor and 2) double-click

    if event.type != gtk.gdk._2BUTTON_PRESS: return
    if (CUR_CURSOR != 'arrow'): return

    zoom_to_tile(event)

class Tile:
    # id = -1;
    # (row,col) = (-1,-1)
    # self.connectionlist = []

    def __init__(self, tileno):
        self.label  = "" # E.g. "ADD", "MUL", "I/O"
        self.tileno = tileno
        # self.row = int(tileno % GRID_HEIGHT)
        # self.col = int(tileno / GRID_WIDTH)
        (self.row,self.col) = tileno2rc(tileno)
        self.connectionlist = []

    def connect(self,connection):
        self.connectionlist.append(connection)

    def printprops(self):
        print "Tile %d (r%d,c%d)" % (self.tileno, self.row, self.col)
        indent = "                "
        print indent + ("\n"+indent).join(self.connectionlist)

    # Todo: maybe two separate routines,
    # one for draw-in-grid and one for draw-standalone etc

    def draw(self, cr):
        cr.save()

        if (ZOOMTILE == -1):
            cr.translate(self.col*CANVAS_WIDTH, self.row*CANVAS_HEIGHT)

        # note draw_pe MUST HAPPEN BEFORE CALLING connectwires()
        # draw_pe() sets up join points for PE inputs

        draw_pe(cr, "setup_only", None, None)

        drawtileno(cr, self.tileno)
        # draw_pe(cr, "ADD", regA=2)
        if   (self.label == "OUT"): draw_pe(cr, "OUT", "wireA", None)
        elif (self.label == "MEM"): draw_pe(cr, "MEM", None, "wireB")
        elif (self.label != ""):    draw_pe(cr, self.label, None, None)
        # else:
        #     # if (self.col==0): draw_pe(cr, "ADD", "0x00002", "0x0000")
        #     # if (self.col==1): draw_pe(cr, "ADD", "0x00002", "wireB")
        #     if (self.col==2): draw_pe(cr, "ADDYO DADDY", "wireA", "wireB")
        #     if (self.col==3): draw_pe(cr, "FOO", "wireA", "regB")

        # FIXME globals are evil?
        global CUR_TILENO # Didn't we do this somewhere already
        CUR_TILENO = self.tileno

        draw_all_ports(cr)
        for c in self.connectionlist:
            if (not connectwires(cr, c) and self.tileno == 0):
                print "ERROR Do not understand connection %s in tile %d (yet);" % (c, self.tileno)
                print "ERROR Removing '%s' from Tile %d connection list" % (c, self.tileno)
                # print "BEFORE: %s" % str(self.connectionlist)
                self.connectionlist.remove(c)
                # print "AFTER: %s\n\n\n" % str(self.connectionlist)

        if (tiletype(self.tileno) == "memory_tile"):
            drawmemtile(cr)
        else: drawtile(cr)

        cr.restore()

    # Not currently used I think
    def info(self):
        print "I am tile number %d;" % (self.tileno),
        print "I live in a grid that is %s tiles high and %s tiles wide"\
            % (GRID_WIDTH, GRID_HEIGHT)


def build_default_connection(tileno, out_wire):
    '''
    Output wire "out_wire" in tile "tileno" has not been explicitly
    connected, so we will show the default (zero) connection.
    '''
    # Should be easy.  Default connections for "out_s[123]t<T>" is "in_s0t<T>"
    # Default connection for "out_s0tT" is "in_s1tT"
    parse = re.search("out_s(\d+)t(\d+)", out_wire)
    if parse:
        out_side  = int(parse.group(1))
        out_track = int(parse.group(2))

        if (out_side == 0): in_side = 1
        else:               in_side = 0
        in_track = out_track;
        in_wire = "in_s%dt%d" % (in_side, in_track)

        if (0): print "Connecting out_wire %s to in_wire %s" % (out_wire, in_wire)
        newconnection = "%s => %s" % (in_wire, out_wire)
        print "Tile %d add missing connection %s" % (tileno,newconnection)
        TILE_LIST[tileno].connect(newconnection)

# def connect_missing_wires():
#     DBG=1;
#     # Each input connection must have matching output and maybe that will suffice
#     if DBG: print "------------------------------------------------------------------------------"
#     if DBG: print "CONNECT MISSING WIRES"
#     for T in TILE_LIST:
#         if (not T): continue
#         for c in T.connectionlist:
#             if DBG: print "found connection '%s' in tile %d" % (c,T.tileno)
#             parse = re.search("(in_s\d+t\d+)", c)
#             if (parse):
#                 w = parse.group(1)
#                 if DBG: print "connects to input wire '%s'" % w
#                 (mT,mw) = find_matching_wire(T.tileno, w)
# 
#                 # print range (0, NTILES)
#                 if mT not in range (0, NTILES):
#                     print "WARNING Ignoring edge wire %s on tile %d" % (w, T.tileno)
#                     return()
# 
#                 # print mT
#                 # print TILE_LIST[mT].connectionlist
#                 found_matching_connection = False
#                 for mc in TILE_LIST[mT].connectionlist:
#                     if DBG: print "  looking for %s in %s" % (mw, mc)
#                     if (re.search(mw,mc)):
#                         found_matching_connection = True
#                         if DBG: print "Found a match for %s in tile %d (I think)" % (mw, mT)
#                 if (not found_matching_connection):
#                     # build_default_connection(mT,mw)
#                     # Under new regime, should be no missing conections...right?
#                     print "ERROR wire '%s' was supposed to connect to '%s' in tile %d" % (w,mw,mT)
#                     print "ERROR found no connection for '%s'" % mw
#                     sys.exit(-1)
#     if DBG: print "------------------------------------------------------------------------------"


# Set up the main window and connect to callback routine that draws everything.
def build_and_launch_main_window(title):

    # Not supposed to need this no more under new regime...
    # # At this point all connections have been made; now we can go through
    # # and add missing defaults
    # connect_missing_wires()

    DBG=1;
    print "------------------------------------------------------------------------"
    print title
    print "------------------------------------------------------------------------"
    win = CGRAWin();
    win.props.title = title
    if DBG: win.move(0,0) # put window at top left corner of screen
    if (DBG>=2): print dir(win.props)
    win.show_all()
    Gtk.main()
    print "------------------------------------------------------------------------"

def demo_connections_2x2():

    # Connections make sense for a 2x2 grid

    tile = TILE_LIST; # A convenient handle

    tile[0].connect("in_s3t1 => out_s2t1")
    tile[0].connect("in_s3t1 connects to out_s1t1")
    tile[0].connect("in_s3t0 => out_s0t0")
    tile[0].printprops()

    tile[1].connect("in_s3t1 => out_s2t1")
    tile[1].connect("in_s3t1 => out_s1t1")
    tile[1].connect("in_s3t1 => out_s0t1")
    tile[1].printprops()

    tile[2].connect("in_s2t0 => out_s0t0")
    tile[2].connect("in_s1t1 => out_s0t1")
    tile[2].printprops()

    tile[3].connect("in_s2t1 => out_s3t1")
    tile[3].printprops()

def demo_connections_4x4():

    # Connections make sense for a 4x4 grid
    # Note same as 2x2 except tiles numbered differently

    tile = TILE_LIST; # A convenient handle

    tile[0].connect("in_s3t1 => out_s2t1")
    tile[0].connect("in_s3t1 connects to out_s1t1")
    tile[0].connect("in_s3t0 => out_s0t0")
    tile[0].printprops()

    tile[1].connect("in_s3t1 => out_s2t1")
    tile[1].connect("in_s3t1 => out_s1t1")
    tile[1].connect("in_s3t1 => out_s0t1")
    tile[1].printprops()

    tile[4].connect("in_s2t0 => out_s0t0")
    tile[4].connect("in_s1t1 => out_s0t1")
    tile[4].printprops()

    tile[5].connect("in_s2t1 => out_s3t1")
    tile[5].printprops()

def initialize_tile_list(w, h):

    global GRID_WIDTH
    global GRID_HEIGHT
    global NTILES     
    global TILE_LIST  

    GRID_WIDTH  = w
    GRID_HEIGHT = h
    NTILES      = w * h
    TILE_LIST   = range(0, NTILES)
    
    set_initial_scale_factor()

    DBG=1
    # for i in TILE_LIST: TILE_LIST[i] = Tile(i)
    if (DBG): print "Initializing tiles"
    for i in TILE_LIST:
        rc = tileno2rc(i)
        if (not rc):
            TILE_LIST[i] = False
        else:
            if (DBG): print "%2s" % i,
            if (DBG and (i%16 == 15)): print ""
            TILE_LIST[i] = Tile(i)
    if (DBG): print ""



# NO LONGER USED reads old format from my decoder
# def process_decoded_bitstream_old(bs):
#     DBG=1
#     # initialize_tile_list(4,4)
#     global REQUESTED_SIZE
#     (nrows,ncols) = REQUESTED_SIZE
#     initialize_tile_list(nrows, ncols)
#     tile = TILE_LIST; # A convenient handle
# 
# #     (r,c) = (6,1)
# #     t = rc2tileno(r,c)
# #     print "Row %d col %d = tileno %s" % (r, c, t)
# #     print 
# #     sys.exit(0)
# 
# 
#     tileno = 43;
#     (r,c) = tileno2rc(tileno)
#     print "Tile %d = row %d col %d" % (tileno, r, c)
#     print "Row %d col %d = tileno %d" % (r, c, rc2tileno(r,c))
#     print ""
# 
#     tileno = 51;
#     (r,c) = tileno2rc(tileno)
#     print "Tile %d = row %d col %d" % (tileno, r, c)
#     print "Row %d col %d = tileno %d" % (r, c, rc2tileno(r,c))
#     print ""
# 
# #     tileno = 57;
# #     (r,c) = tileno2rc(tileno)
# #     print "Tile %d = row %d col %d" % (tileno, r, c)
# #     sys.exit(0)
# 
#     for line in bs:
#         if (DBG>1): print line.rstrip()
#         # Search each line for connections
# 
#         if (re.search("CGRA OUTPUT", line)):
#             tile[tileno].label = "OUT"
#             continue
#         elif (re.search("CGRA INPUT", line)):
#             tile[tileno].label = "IN"
#             continue
# 
#         # foundtileno = re.search("^TILE *([0-9]*)", line)
#         # I guess python uses '\A' instead of '^' :(
#         foundtileno = re.search("^\s*TILE\s*([0-9]+)", line)
#         if (foundtileno):
#             tileno = int(foundtileno.group(1))
#             if (DBG>1): print "*** Found tile %d" % tileno
#             continue
# 
#         teststring = line
#         while True:
#             # Want to find all connections of the form "out_s0t0 <= in_s1t0"
#             # BUT NOT e.g. "regB <= 0x0000" 'out_s1t0 <= pe_out' 'out <= MUL(wireA,wireB)'
#             # x = re.search("(o[^ ]* *<= *i[^ ]*)(.*)", teststring)
# 
#             # NO list all connections and let GOD sort 'em out...
#             x = re.search("([^ ]* *<= *[^ ]*)(.*)", teststring)
# 
#             # OR: x = re.search("(\S*\s*<=\s*\S*)(.*)", teststring)
#             if (x):
#                 connection = x.group(1).strip()
#                 print "Tile %d found connection '%s'" % (tileno,connection)
#                 teststring = x.group(2).strip()
#                 tile[tileno].connect(connection)
#             else:
#                 break;

def process_decoded_bitstream(bs):

    DBG=0

    # initialize_tile_list(4,4)
    global REQUESTED_SIZE
    (nrows,ncols) = REQUESTED_SIZE
    initialize_tile_list(nrows, ncols)
    tile = TILE_LIST; # A convenient handle

    # (r,c) = (6,1)
    # t = rc2tileno(r,c); print "Row %d col %d = tileno %s\n" % (r, c, t); sys.exit(0)

    # tileno = 43;
    # (r,c) = tileno2rc(tileno)
    # print "Tile %d = row %d col %d" % (tileno, r, c)
    # print "Row %d col %d = tileno %d\n" % (r, c, rc2tileno(r,c))

    reg = {}
    (reg['A'], reg['B']) = ("regA", "regB") # defaults

    operand = {} # operand['a'], operand['b']

    if DBG: print ""
    for line in bs:
        if (DBG>1): print line.rstrip()
        line = line.strip() # why not

        # Need to know current tile
        # Every non-comment line is a bitstream ADDR/DATA pair;
        # Last four hex digits of 8-digit ADDR is tile number
        parse = re.search('^[0-9A-Fa-f]...(....)', line)
        if (parse):
            tileno = int(parse.group(1), 16)
            if DBG: print "%s => tile number %d" % (line, tileno)
            continue

        if DBG: print ""
        if DBG: print "BEFORE: " + line

        # Find inputs and outputs
        # Note this must happen BEFORE finding other op names :(
        if   re.search("op = input",  line): tile[tileno].label = "IN"
        elif re.search("op = output", line): tile[tileno].label = "OUT"
        elif re.search("mem_out",     line): tile[tileno].label = "MEM"

        # Transformations
        # < "# data[(1, 0)] : connect wire 3 (pe_out_res) to out_BUS16_S0_T0"
        # > "out_s1t0 <= in_s0t0"

        # mild FIXME/TODO b/c in a loop regex's should probably be compiled first
        # 'pe_out_res' => 'pe_out'
        line = re.sub("pe_out_res", "pe_out", line)

        # "to a" => "to wireA", "to b" => "to wireB"
        # FIXME so egregious!!!
        line = re.sub("to a", "to wireA", line)
        line = re.sub("to b", "to wireB", line)


        # 'out_BUS16_S0_T0' => 'out_s0t0'
        line = re.sub(r'(in|out)_BUS16_S(\S+)_T(\S+)', r"\1_s\2t\3", line)
        # print "AFTER:  " + line

        # 'data[(1, 0)] : connect wire 3 (X) to Y'
        # => 'Y <= X'
        line = re.sub(
            r'.*connect wire \S+ \(([^)]+)\) to (\S+)',
            r'\2 <= \1',
            line)

        # Transformations
        # < "# data[(15, 0)] : load `b` reg with const: 1
        # > "regB <= 0x0001"
        parse = re.search('.*load `(.)` reg with const: (\S+)', line)
        parse = re.search('.*load `(.)` reg with const: (\S+)', line)
        if (parse):
            AB = (parse.group(1)).upper()
            k = "0x%04x" % int(parse.group(2))
            line = "reg%s <= %s" % (AB,k)
            reg[AB] = k
            if DBG: print "reg['%s'] = %s" % (AB, reg[AB])

        # Transformations
        # < "# data[14] : load `a` reg with wire"
        # > regA <= wireA

        parse = re.search("load `(.)` reg with wire", line)
        if (parse):
            AB = parse.group(1).upper()
            line = "reg%s <= wire%s" % (AB,AB)


        # Transformations
        # < "# data[15] : read from reg `a`"
        # < "# data[13] : read from reg `b`"
        # < "# data[(4, 0)] : op = mul"
        #
        # > pe_out <= MUL(regA,0x0001)

        # < "# data[15] : read from wire `a`"
        # < "# data[13] : read from wire `b`"
        # < "# data[(4, 0)] : op = add"
        #
        # > "wireA <= in_s1t0"
        # > "wireB <= in_s2t0"
        # > "pe_out <= ADD(wireA,wireB)"

# Tile 10
# GOT:    'pe_out <= ADD(regA,0x0000)'
# WANTED: 'pe_out <= ADD(wireA,0x0000)'


        parse = re.search("read from (reg|wire) `(.)`", line)
        if (parse):
            AB = parse.group(2).upper()
            operand[AB] = parse.group(1)

        parse = re.search(" op = (\S+)", line)
        if (parse):
            opname = parse.group(1).upper()
            if (operand['A'] == 'wire'): reg['A'] = 'wireA' # Confusing enough?
            if (operand['B'] == 'wire'): reg['B'] = 'wireB'
            line = 'pe_out <= %s(%s,%s)' % (opname, reg['A'], reg['B'])

            (reg['A'], reg['B']) = ("regA", "regB") # defaults


        if DBG: print "AFTER:  " + line
#         continue

#         # Search each line for connections
# 
#         if (re.search("CGRA OUTPUT", line)):
#             tile[tileno].label = "OUT"
#             continue
#         elif (re.search("CGRA INPUT", line)):
#             tile[tileno].label = "IN"
#             continue
# 
#         # foundtileno = re.search("^TILE *([0-9]*)", line)
#         # I guess python uses '\A' instead of '^' :(
#         foundtileno = re.search("^\s*TILE\s*([0-9]+)", line)
#         if (foundtileno):
#             tileno = int(foundtileno.group(1))
#             if (DBG>1): print "*** Found tile %d" % tileno
#             continue

        teststring = line
        while True:
            # Want to find all connections of the form "out_s0t0 <= in_s1t0"
            # BUT NOT e.g. "regB <= 0x0000" 'out_s1t0 <= pe_out' 'out <= MUL(wireA,wireB)'
            # x = re.search("(o[^ ]* *<= *i[^ ]*)(.*)", teststring)

            # NO list all connections and let GOD sort 'em out...
            x = re.search("([^ ]* *<= *[^ ]*)(.*)", teststring)

            # OR: x = re.search("(\S*\s*<=\s*\S*)(.*)", teststring)
            if (x):
                connection = x.group(1).strip()
                print "Tile %2d found connection '%s'" % (tileno,connection)
                teststring = x.group(2).strip()
                tile[tileno].connect(connection)
            else:
                break;


##############################################################################
# Actual runcode starts here!  (FINALLY)

def display_decoded_bitstream_file(filename):
    DBG=1
    # call(["ls", "-l", "examples"]) # exec/run/shell

    if DBG: print "Using", filename, "as input";

    # Let's make the title a bit more attractive
    # e.g. "debugconv.bsa" instead of "../examples/debugconv.bsa"
    title = re.sub(r'.*/([^/]+)$', r'\1', "/"+filename)
    if DBG: print "Using", title, "as window title";

    try:
        inputstream = open(filename);
        # process_decoded_bitstream_old(inputstream)
        process_decoded_bitstream(inputstream)
        inputstream.close()
        # build_and_launch_main_window(filename)
        build_and_launch_main_window(title)
    except IOError:
        # TODO/FIXME yeah these were copies from somewhere else obviously
        print ""
        print "ERROR Cannot find processor bitstream file '%s'" % filename
        print main.__doc__
        sys.exit(-1);

def demo_sb_2x2():
    # Simple 2x2 array with a few switchbox connections

    # Initialize a 2x2 tile array
    initialize_tile_list(2,2)

    # Demo 1 assumes a 2x2 grid and makes some connections
    demo_connections_2x2()

    # Set up the main window and connect to callback routine that draws everything.
    # Currently builds a window such that 2x2 grid fits in window at 2x scale
    title = func_name(); 
    build_and_launch_main_window(title)

def demo_sb_4x4():
    # Simple 4x4 array with a few switchbox connections

    # TBD: demo_sb_4x4 builds sample connections for a 4x4 grid at 1x scale (demo_sb_2x2 was 2x)

    initialize_tile_list(4,4)    # Initialize 4x4 tile array

    # Demo 2 makes same connections as 2x2 except in a 4x4 grid now
    demo_connections_4x4()

    # Set up the main window and connect to callback routine that draws everything.
    # Currently builds a window such that 2x2 grid fits in window at 2x scale
    title = func_name(); 
    build_and_launch_main_window(title)

def demo_sb_8x8():
    initialize_tile_list(8,8)    # Initialize 8x8 tile array
    demo_connections_4x4()       # For now let's use the 4x4 connections, see what happens
    title = func_name(); 
    build_and_launch_main_window(title)


def func_name():
    import traceback
    return traceback.extract_stack(None, 2)[0][2]

def demo_cd_jimmied():
    DBG=0

    # print func_name(); sys.exit(0)

    initialize_tile_list(4,4)  # Initialize 4x4 tile array
    example = '''
                        TILE 0 (0,0)
00050000 00000C00 [sb1] out_s1t0 <= pe_out
F0000000 FFFFFFFF [pe ] IO HACK: regA <= 0xFFFF
F1000000 FFFFFFFF [pe ] IO HACK: regB <= 0xFFFF
FF000000 000000F0 [pe ] IO HACK: pe_out is CGRA INPUT 

                        TILE 1 (1,0)
00020001 00000005 [cb1] wireA <= in_s3t0
00030001 00000000 [cb2] wireB <= in_s0t0
00050001 00000C00 [sb1] out_s1t0 <= pe_out
FF000001 0000A00B [pe ] pe_out <= MUL(wireA,wireB) 

                        TILE 2 (2,0)
00020002 00000005 [cb1] wireA <= in_s3t0
F1000002 FFFFFFFF [pe ] IO HACK: regB <= 0xFFFF
FF000002 000000FF [pe ] IO HACK: pe_in_a (wireA) is CGRA OUTPUT 

                        TILE 5 (1,1)
00050005 00300000 [sb1] out_s2t0 <= pe_out 
F0000005 00000002 [pe ] regA <= 0x0002
F1000005 00000000 [pe ] regB <= 0x0000
FF000005 00000000 [pe ] pe_out <= ADD(0x0002,0x0000) 
'''
    if DBG: print example
    example = example.split('\n')
    process_decoded_bitstream(example)
    title = func_name(); 
    build_and_launch_main_window(title)


def demo_an2_jimmied():
    DBG=0

    # print func_name(); sys.exit(0)

    initialize_tile_list(4,4)  # Initialize 4x4 tile array
    example = '''
                        TILE 4 (0,1)
00020004 00000000 [cb1] wireA <= in_s1t0
FF000004 00000000 [pe ] pe_out <= ADD(regA,regB)

                        TILE 5 (1,1)
00050005 00000000 [sb1] out_s3t0 <= in_s0t0

                        TILE 8 (0,2)
00020008 00000000 [cb1] wireA <= in_s1t0
00030008 00000000 [cb2] wireB <= in_s0t0
FF000008 0000F00B [pe ] pe_out <= MUL(wireA,wireB)
00050008 00000C00 [sb1] out_s1t0 <= pe_out

                        TILE 9 (1,2)
FF000009 00000000 [pe ] pe_out <= ADD(0x0002,0x0000)
F0000009 00000002 [pe ] regA <= 0x0002
F1000009 00000000 [pe ] regB <= 0x0000
00050009 00200003 [sb1] out_s0t0 <= pe_out     out_s3t0 <= in_s0t0
                        out_s2t0 <= in_s3t0

                        TILE 12 (0,3)
0005000C 00100C00 [sb1] out_s1t0 <= pe_out     out_s2t0 <= in_s1t0
FF00000C 00000000 [pe ] pe_out <= ADD(regA,regB)

                        TILE 13 (1,3)
0005000D 80200000 [sb1] out_s2t0 <= in_s3t0    out_s3t0 <= in_s2t0
'''
    if DBG: print example
    example = example.split('\n')
    process_decoded_bitstream(example)
    title = func_name(); 
    build_and_launch_main_window(title)

def do_demos():
    # return
    global SWAP
    global REQUESTED_SIZE
    if (1):
        REQUESTED_SIZE = (8,8)
        # display_decoded_bitstream_file("../decoder/examples/cd387-newmem-8x8.bs-decoded")
        display_decoded_bitstream_file("../decoder/examples/cd387-newmem-8x8-nodefaults.bsd")

    REQUESTED_SIZE = (4,4)
    SWAP = False # Demos were all written under old regime
    demo_cd_jimmied()
    demo_an2_jimmied()
    demo_sb_4x4()
    demo_sb_2x2()
    if (1):
        # Open a channel to the example decoded bitstream
        # filename = sys.argv[1];
        # filename = args[0];
        # filename = "./examples/an2.bs-decoded"
        # filename = "./examples/cd.bs-decoded"
        SWAP = False # old regime
        display_decoded_bitstream_file("./examples/cd-jimmied.bs-decoded")
        display_decoded_bitstream_file("./examples/an2-jimmied.bs-decoded")
        # SWAP = False # This should fail
        # display_decoded_bitstream_file("../decoder/examples/cd387-decoded-nodefaults-newmem.bs")
        SWAP = True  # newmem / new regime
        # display_decoded_bitstream_file("../decoder/examples/cd387-decoded-nodefaults-newmem.bs")
        display_decoded_bitstream_file("cd387-newmem-nodefaults.bsd")

    demo_sb_8x8()
    return


def main():
    '''
    Usage:
        bsview.py <b1.bs-decoded> <b2.bs-decoded> ...   # Displays decoded bitstreams b1, b2, ...
        bsview.py -swaprc <b1.bsv1-decoded> ...         # Swap RC on indicated bitstream
        bsview.py -newmem <b1.bsv1-decoded> ...         # Do the right thing for newmem regime
        bsview.py -oldmem <b1.bsv1-decoded> ...         # Do the right thing for oldmem regime
        bsview.py -demo                                 # Runs through a couple built-in demos
        bsview.py --help                                # Displays this help message
    ''' 
    print sys.argv
    args = sys.argv[1:]  # argv[0] is command name

    # FIXME yes this is bad
    global REQUESTED_SIZE
    global SWAP

    # Defaults for old regime
    # REQUESTED_SIZE = (4,4) # default
    # SWAP           = False

    # Defaults for new regime
    REQUESTED_SIZE = (8,8) # default
    SWAP           = True

    if    (len(args) == 0): do_demos() # no args
    # if    (len(args) == 0): demo_sb_8x8() # no args
    while (len(args)  > 0):            # args
        print "arg0 = %s, SWAP=%s" % (args[0], SWAP)
        if   (args[0] ==  "-demo"):  do_demos()
        elif (args[0] == "--help"):  print main.__doc__
        elif (args[0] == '-swaprc'): SWAP = True
        elif (args[0] == '-newmem'): SWAP = True
        elif (args[0] == '-oldmem'): SWAP = False
        elif (args[0] == '-8x8'): REQUESTED_SIZE = (8,8)
        else:      display_decoded_bitstream_file(args[0])
        args = args[1:]
    return


# def find_matching_wire(tileno, w):
#     DBG=1
#     # find_matching_wire(4,"in_s1t1") => (5, "out_s3t1")
#     parse = re.search("(in|out)_s([0-9]+)t([0-9]+)", w)
#     if (parse == None):
#         print "Invalid wire name '%s'" % w
#         return
#     in_or_out = parse.group(1)
#     side      = int(parse.group(2))
#     track     = int(parse.group(3))
# 
#     if (in_or_out=="out"): in_or_out="in"
#     else:            in_or_out="out"
# 
#     (r,c) = tileno2rc(tileno)
#     #   print (r,c,side)
# 
#     if   (side==0): (r,c,side) = (r,c+1,side+2)
#     elif (side==1): (r,c,side) = (r+1,c,side+2)
#     elif (side==2): (r,c,side) = (r,c-1,side-2)
#     elif (side==3): (r,c,side) = (r-1,c,side-2)
# 
#     #   print (r,c,side)
# 
#     adj_tileno = rc2tileno(r,c)
#     adj_wire = "%s_s%dt%d" % (in_or_out, side, track)
#     if DBG: print "\n%s on tile %d matches %s on tile %d" % (w, tileno, adj_wire, adj_tileno)
#     return (adj_tileno, adj_wire)

main()


#################################################################
# Notes
# 
# http://pycairo.readthedocs.io/en/latest/reference/context.html?
# highlight=set_dash#cairo.Context.set_dash
# 
#################################################################
