#!/usr/bin/python
import sys
import re

# gi a.k.a. pygobjects, pygtk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk
import cairo

from subprocess import call

#TODO
# Put FU in each tile and connections to/from FU

from math import pi
PI = pi
def deg2rad(rad): return rad*180/PI

GRID_WIDTH  = 2;
GRID_HEIGHT = 2;
NTILES = GRID_WIDTH*GRID_HEIGHT
TILE_LIST = range(0, NTILES)

# tileno-to-RC conversion
def tileno2rc(tileno): return (tileno % GRID_HEIGHT, int(tileno / GRID_WIDTH))
def rc2tileno(x,y):    return GRID_WIDTH*col + row

# A really dumb way to keep track of current scale factor, for
# button-press events
SCALE_FACTOR = 1;
SF_ALL       = 1; # No zoom when displaying all tiles in a window
SF_ALL_2x2   = 2; # Zoom 2x when displaying 2x2 grid



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
CANVAS_WIDTH  = 2*PORT_HEIGHT + 2*NTRACKS_PE_BUS_V*PORT_WIDTH + 3*PORT_PAD
CANVAS_HEIGHT = 2*PORT_HEIGHT + 2*NTRACKS_PE_BUS_H*PORT_WIDTH + 3*PORT_PAD

WIN_WIDTH  = 4*CANVAS_WIDTH+2*ARRAY_PAD
WIN_HEIGHT = 4*CANVAS_HEIGHT+2*ARRAY_PAD

def errmsg(m):
    sys.stdout.write("ERROR: %s\n" % (m))
    sys.exit(-1)

##############################################################################
# These could all be part of a Wire class if we wanted to...

# E.g. given "out_s1t3", rval['inout'] = "out", rval['side'] = 1 and rval['track'] = 3
def parse_wirename(wirename):
    rval = {}
    decode = re.search('(in|out)_s(.*)t(.*)', wirename);
    rval['inout'] = str(decode.group(1))
    rval['side']  = int(decode.group(2))
    rval['track'] = int(decode.group(3))
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

    # Need block id and track number of the target wire
    decode = re.search('(in_s.*|out_s.*)t(.*)', wirename);
    b = decode.group(1);      # blockno e.g. "in_s1"
    t = int(decode.group(2)); # trackno e.g. "3"

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

    return (x,y);

# TODO/FIXME need at least one more pass on drawport() below!

# E.g. 'drawport(cr, "out_s1t0")' or 'drawport(cr, wirename, options="ghost")'
def drawport(cr, wirename, **keywords):
    DBG = 0;

    # Draw the port for the indicated wire in the context of the current canvas
    # Ports are labeled arrows; input ports point in to the tile and
    # output ports point out.
    # connectionpoint() will tell where to start (for outputs) or end (for inputs)
    # [Optionally] attach a register to the port inside the tile.
    # [Optionally] leave off the label

    if (DBG): print "Drawing port for wire '%s'..." % (wirename)

    # Only valid option so far is "ghost", meaning draw the port in light background color
    # TODO: options for reg/noreg, label/nolabel
    
    optionlist = []
    if ('options' in keywords):
        if (DBG): print 'options parameter found, it is ', keywords['options']
        optionlist = keywords['options'].split(',')
        if (DBG): print "Found the following options: "+ str(optionlist)
        # for o in options: print "  " + o
    else:
        if (DBG): print 'no options parameter, sorry'

    cr.save()

    if (1):
        # Translate and rotate the world...
        # if (DBG): print "Translate to %d,%d" % (x,y),
        (x,y) = connectionpoint(wirename)
        cr.translate(x,y)
        drawdot(cr, 0, 0, "black") # Mark the connection point with a black dot

        # Side 0,1,2,3 out-wires point E, S, W and N respectively
        s = side(wirename)
        rot = s * 3.1416/2
        if (DBG): print "rotate %d degrees\n" % int(180*rot/3.1416)
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

        if (1):
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


def drawFU(cr, opname):

    # Draw the main functional unit

    # width and height of FU (should maybe be globals I dunno)
    (fu_w,fu_h) = (30,12)

    fu_linewidth   = 0.5

    headwidth   = 3    # see how it looks
    headlength  = 2 #reg_height/3

    # width and height of input registers
    reg_width  = 0.4*fu_w
    reg_height = 6 # for now, say
    reg_sep    = headlength+1 # Gap b/w reg and FU

    arrowlength = reg_height+reg_sep+1
    fill        = False
    # txt_linewidth = float(fu_linewidth)/2.0
    txt_linewidth = fu_linewidth

    if (1):
        cr.save()
        # Put a big FU in the middle of the tile, with A and B inputs,
        # each w/optional input registers

        # Draw the main FU
        setcolor(cr, "black")
        cr.set_line_width(fu_linewidth)

        # fu_ulx = -w/2; fu_uly = -h/2
        centerx = CANVAS_WIDTH/2
        centery = CANVAS_HEIGHT/2
        fu_ulx = centerx - fu_w/2
        fu_uly = centery - fu_h/2

        cr.rectangle(fu_ulx,fu_uly,  fu_w, fu_h) # fu_ulx, fu_uly, width, height

        # Add a label.  Just center it, like did w/ ghost numbers

        cr.set_font_size(0.8*fu_h)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        (txt_ulx, txt_uly, w, h, nextx, nexty) = cr.text_extents(opname)

        (centerx,centery)    = (CANVAS_WIDTH/2,      CANVAS_HEIGHT/2)
        (txt_ulx,txt_uly)    = (centerx - w/2 - txt_ulx, centery + h/2)
        cr.move_to(txt_ulx,txt_uly)
        cr.show_text(opname)
        cr.stroke()

        # Input arrows at w/4 and 3w/4 across the top
        if (1):
            
            cr.save()
            setcolor(cr, 'red')
            # cr.set_line_width(txt_linewidth)
            # print "FOO " + str(fu_linewidth)
            # print "BAR " + str(txt_linewidth)
            cr.set_line_width(txt_linewidth)
            # cr.set_line_width(0.5)
            cr.translate(fu_ulx,fu_uly) # UL corner of FU
            cr.translate(fu_w/4, -arrowlength)
            cr.rotate(PI/2) # point DOWN
            draw_arrow(cr, arrowlength, headlength, headwidth, fill)
            cr.stroke(); cr.restore()



        cr.stroke()
        cr.restore()

    # Draw the A/B input registers

    if (1):
        cr.save()
        setcolor(cr, 'black')
        cr.set_line_width(.2)
        reg_uly = centery - fu_h/2 - reg_height - reg_sep

        # aport region is left half of fu
        aport_x = (fu_ulx + fu_w/4)
        reg_ulx = aport_x - reg_width/2
        cr.save()
        cr.translate(reg_ulx,reg_uly)
        drawreg(cr, reg_width,reg_height)
        cr.restore()
    
        # b port what the heck
        bport_x = (fu_ulx + 3*fu_w/4)
        reg_ulx = bport_x - reg_width/2
        cr.save()
        cr.translate(reg_ulx,reg_uly)
        drawreg(cr, reg_width,reg_height)
        cr.stroke(); cr.restore()

    # Connection-point dot
    if (1):
        cr.save()
        setcolor(cr, 'red')
        # cr.set_line_width(txt_linewidth)
        # print "FOO " + str(fu_linewidth)
        # print "BAR " + str(txt_linewidth)
        cr.set_line_width(txt_linewidth)
        # cr.set_line_width(0.5)
        cr.translate(fu_ulx,fu_uly) # UL corner of FU
        cr.translate(fu_w/4, -arrowlength)
        # cr.rotate(PI/2) # point DOWN
        # draw_arrow(cr, arrowlength, headlength, headwidth, fill)
        drawdot(cr, 0,0, 'red')
        cr.stroke(); cr.restore()

    # TODO: is there an output reg?  Artem says "NO"

    cr.stroke()
    cr.restore()



#     cr.set_font_size(20)
#     cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
# 
#     # E.g. cr.text_extents("100") => (3, -15, 38, 15, 42, 0) => (UL(x,y), w, h, begin_next(x,y)
#     # print cr.text_extents(opname)
#     (ULx, ULy, w, h, nextx, nexty) = cr.text_extents(opname)
# 
#     centerx = CANVAS_WIDTH/2
#     centery = CANVAS_HEIGHT/2
# 
#     x = centerx - w/2 - ULx
#     y = centery + h/2
# 
#     # cr.set_source_rgb(1,0,0); drawdot(cr, centerx, centery, 'red'
#     # cr.set_source_rgb(0,0,1); drawdot(cr, x+ULx, y+ULy, 'blue')
#     # cr.set_source_rgb(1,0,1); drawdot(cr, x, y, 'purple')
# 
#     cr.move_to(x,y)
#     cr.show_text(opname)
#     cr.stroke()
#     cr.restore()


def drawtileno(cr, tileno):

    cr.save()
    # Put a big ghost-number in the middle of the tile
    # See https://www.cairographics.org/manual/cairo-text.html#cairo-text-extents

    # Needs to be a string.
    tileno = str(tileno)

    # Ghost color= light gray
    # graylevel = 0.9; cr.set_source_rgb(graylevel,graylevel,graylevel)
    setcolor(cr, 'ghostgray')

    cr.set_font_size(20)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    # E.g. cr.text_extents("100") => (3, -15, 38, 15, 42, 0) => (UL(x,y), w, h, begin_next(x,y)
    # print cr.text_extents(tileno)
    (ULx, ULy, w, h, nextx, nexty) = cr.text_extents(tileno)

    centerx = CANVAS_WIDTH/2
    centery = CANVAS_HEIGHT/2

    x = centerx - w/2 - ULx
    y = centery + h/2

    # cr.set_source_rgb(1,0,0); drawdot(cr, centerx, centery, 'red'
    # cr.set_source_rgb(0,0,1); drawdot(cr, x+ULx, y+ULy, 'blue')
    # cr.set_source_rgb(1,0,1); drawdot(cr, x, y, 'purple')

    cr.move_to(x,y)
    cr.show_text(tileno)
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

def connectwires(cr, connection):

    # Draw a manhattan blue line connecting the two indicated ports inside a tile
    # I've given a lot of leeway as to how connections are specified.
    # E.g. these should all work:
    #     connectwires(cr, "in_s3t0 => out_s2t3")
    #     connectwires(cr, "in_s3t0 out_s2t3")
    #     connectwires(cr, "in_s3t0 connects to out_s2t3")
    #     connectwires(cr, "  in_s3t0 connects to out_s2t3  ")

    DBG = 0;

    # Find the names of the two wires to connect.
    # parse = re.search( "([A-z_0-9]+).*[^A-z_0-9]([A-z_0-9]+)[^A-z_0-9]*$", connection)

    # A better way?
    connection = connection.strip() # Eliminate leading/trailing space

    # For now connections must be of the form "out_s0t0 <= in_s1t0"
    # BUT NOT e.g. "regB <= 0x0000" 'out_s1t0 <= pe_out' 'out <= MUL(wireA,wireB)'
    parse = re.search("^(o[^ ]*) .* (i[^ ]*)$", connection)
    if (not parse):
        print "ERROR Do not understand connection %s (yet)" % connection
        return;


    w1 = parse.group(1); w2 = parse.group(2)

    # Only draw non-ghost ports if connections exist.
    drawport(cr, w1);    drawport(cr, w2)

    # TODO add a "if (DBG)" here maybe
    if (DBG):
        print "connection = " + connection
        print "Connecting wires '%s' and '%s'\n" % (w1,w2)

    # 1. Find internal join point of the two wires w1 and w2
    # 1a. Find each wires connection point at tile's edge

    ULrotpoint1 = connectionpoint(w1) # upper-left corner of enclosing box oriented to side 0
    x1 = ULrotpoint1[0]; y1 = ULrotpoint1[1]

    ULrotpoint2 = connectionpoint(w2) # upper-left corner of enclosing box oriented to side 0
    x2 = ULrotpoint2[0]; y2 = ULrotpoint2[1]

    # drawdot(cr,x1,y1,'red'); drawdot(cr,x2,y2,'red')

    # x1 == +/- PORT_HEIGHT means x1 is an edge and x2 is interior
    if   (x1 ==  PORT_HEIGHT): interior = (x2,y1)
    elif (x1 == -PORT_HEIGHT): interior = (x2,y1)
    else:                      interior = (x1,y2)

    # Okay now connect the dots!  With a blue line.
    # Put a blue dot at the corner.  You'll thank me later.
    # TODO if (isbus): linewidth = 1 etc.
    if (1):
        cr.save()
        setcolor(cr,'blue')
        cr.set_line_width(.5)
        drawdot(cr,interior[0],interior[1],'blue')
        cr.move_to(x1,y1)
        cr.line_to(interior[0],interior[1])
        cr.line_to(x2,y2)
        cr.stroke()
        cr.restore()

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

def draw_handler(widget, cr):
    global CUR_DRAW_WIDGET; CUR_DRAW_WIDGET = widget;

    global ZOOMTILE; tileno = ZOOMTILE
    if (tileno == -1):   draw_all_tiles(cr);
    else:                draw_one_tile(cr, tileno);

def draw_one_tile(cr, tileno):
    cr.save()

    # scalefactor = 10 # zoom in for debugging
    # cr.scale(scalefactor,scalefactor)

    ########################################################################
    # Scale and translate

    global SCALE_FACTOR;
    
    # OLD: Draw at 4x requested size; SCALE_FACTOR = 4
    # NEW:
    #   For now, unzoomed (grid) view is scaled to 2x (USF=2).
    #   And zoomed (onetile) view is 2x of that.  Ish.
    #   Except that, for no good reason, want the zoomed tile
    #   to occupy the same space as four unzoomed tiles.

    # Canvas width = tile width + length of ports on each side
    # In zoomed view, want width of one tile to match
    # (two tiles + gap) in unzoomed (2x) view
    USF = 2 # Scale factor for unzoomed tiles
    tile_width            = CANVAS_WIDTH - 2*PORT_WIDTH
    two_tiles_plus_gap_2x = (2*tile_width + 2*PORT_LENGTH)*USF
    fudge                 = .09 # yeah I dunno whatevs OCD OKAY?
    SCALE_FACTOR = float(two_tiles_plus_gap_2x)/float(tile_width) + fudge
    cr.scale(SCALE_FACTOR,SCALE_FACTOR)

    if (0): print "Zoom scale factor %d/%d = %f." \
        % (two_tiles_plus_gap_2x, tile_width, SCALE_FACTOR)

    ########################################################################
    # OLD: cr.translate(ARRAY_PAD, ARRAY_PAD)
    # NEW: -----------------------------------------------------------------
    # Translate so that zoomed tile corners match unzoomed tile corners
    # Unzoomed corners were centered in window, and above scaling (supposedly)
    # ensures that zoomed corners are same distance apart as unzoomed,
    # so: should suffice to make sure zoomed corners are centered.

    # Things that were 40px wide in unzoomed view are now just 10px wide ish
    scaled_win_width    = WIN_WIDTH/SCALE_FACTOR
    scaled_canvas_width = CANVAS_WIDTH
    print "sww=%0.2f scw=%0.2f" % (scaled_win_width,scaled_canvas_width)
    xmargin = (scaled_win_width - scaled_canvas_width)/2
    ymargin = xmargin
    cr.translate(xmargin, ymargin)

    # Okay done with scale and translate.  Now draw!
    print "Drawing tile %s!" % str(tileno)
    if (0): print "...at scale factor %f." % SCALE_FACTOR
    TILE_LIST[tileno].draw(cr)
    cr.restore()

def draw_all_tiles(cr):

    global SCALE_FACTOR;                   # Others should know

    SCALE_FACTOR = 1
    if (GRID_WIDTH <= 2): SCALE_FACTOR = 2 # Why squint if you don't need to?

    print "Draw all tiles!"
    cr.save()
    cr.translate(ARRAY_PAD, ARRAY_PAD)    # Whitespace margin at top and left
    cr.scale(SCALE_FACTOR,SCALE_FACTOR)
    draw_big_ghost_arrows(cr)             # Big ghost arrows in background of grid
                                          # view show general flow dir for tracks
    for tile in TILE_LIST: tile.draw(cr)  # Draw ALL the tiles
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

# Is this better?
class CGRAWin(Gtk.Window):
    def __init__(self):
        DBG = 2

        # Set up the main window and connect to callback routine that draws everything.
        # See above for definition of globals WIN_WIDTH, WIN_HEIGHT

        title = "Tilesy" # haha LOL
        Gtk.Window.__init__(
            self, \
            title         = title,      \
            width_request = WIN_WIDTH,  \
            height_request= WIN_HEIGHT  \
        )            

        self.da = Gtk.DrawingArea()
        self.add(self.da)
        # A dumb way to keep track of the current window and drawing area widget
        # global CUR_WINDOW;      CUR_WINDOW = win;
        global CUR_DRAW_WIDGET; CUR_DRAW_WIDGET = self.da;
        
        # Some/all of this maybe doesn't belong in win init,
        # but oh well here it is for now anyway

        win = self
        # "draw" event results in drawing everything on drawing area 'da'
        draw_handler_id = win.da.connect("draw", draw_handler)

        # https://stackoverflow.com/questions/23946791/mouse-event-in-drawingarea-with-pygtk
        # http://www.pygtk.org/pygtk2tutorial/sec-EventHandling.html
        button_press_handler_id = win.da.connect("button-press-event", button_press_handler)

        # FIXME/TODO add to 0bugs and/or 0notes: gtk.gdk.BUTTON_PRESS_MASK = Gdk.EventMask.BUTTON_PRESS_MASK
        win.da.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        win.connect("delete-event", Gtk.main_quit)

def button_press_handler(widget, event):
    DBG = 0

    # Need to know current scale factor so we keep track of it in a global
    print ""
    print "SCALE_FACTOR %s" % SCALE_FACTOR
    print ""

    # Can't get scale factor from context matrix, it's always (1,0,0,1,0,0) why?
    if (0): print "matrix = " + str(DRAW_HANDLER_CR.get_matrix())

    # x,y coordinates of button-press
    x = event.x; y = event.y
    if (DBG): print "%d %d" % (x,y)

    # Subtract off the scale-independent paddings and divide by scale factor I guess
    x = (x - ARRAY_PAD)/SCALE_FACTOR; y = (y - ARRAY_PAD)/SCALE_FACTOR;
    if (DBG): print "Transformed x,y = (%d,%d)" % (x,y)
    if (DBG): print "CANVAS_WIDTH = %d" % CANVAS_WIDTH

    # Find row, col of tile indicated by sclaed/translated (x,y)
    row = y/CANVAS_WIDTH; col = x/CANVAS_HEIGHT;
    row = int(row); col = int(col)

    # Find tile number indicated by (row,col)
    # (Supposed to use a function to do this I guess): (tileno =  rc2tileno(row,col)
    tileno = GRID_WIDTH*col + row
    print "I think this is tile %d (r%d,c%d)" % (tileno, row,col)

    # If already zoomed out (ZOOMTILE === -1), zoom in to tile indicated.
    # Otherwise, zoom out.
    global ZOOMTILE;
    if (ZOOMTILE == -1):
        if (DBG): print "Zoom in to tile %s!" % str(tileno)
        ZOOMTILE = tileno;
    else:
        if (DBG): print "Zoom out!"
        ZOOMTILE = -1;

    # Redraw after zoom
    CUR_DRAW_WIDGET.queue_draw()

class Tile:
#     id = -1;
#     (row,col) = (-1,-1)
#     self.connectionlist = []

    def __init__(self, tileno):
        self.tileno = tileno
        # self.row = int(tileno % GRID_HEIGHT)
        # self.col = int(tileno / GRID_WIDTH)
        (self.row,self.col) = tileno2rc(tileno)
        self.connectionlist = []

    def connect(self,connection):  self.connectionlist.append(connection)

    def printprops(self):
        print "Tile %d (r%d,c%d)" % (self.tileno, self.row, self.col)
        indent = "                "
        print indent + ("\n"+indent).join(self.connectionlist)

    # Todo: maybe two separate routines, one for draw-in-grid and one for draw-standalone etc
    def draw(self, cr):
        
        cr.save()

        if (ZOOMTILE == -1):
            cr.translate(self.col*CANVAS_WIDTH, self.row*CANVAS_HEIGHT)

        drawtileno(cr, self.tileno)
        drawFU(cr, "ADD")

        draw_all_ports(cr)
        for c in self.connectionlist: connectwires(cr, c)
        drawtile(cr)
        cr.restore()

    # Not currently used I think
    def info(self):
        print "I am tile number %d;" % (self.tileno),
        print "I live in a grid that is %s tiles high and %s tiles wide"\
            % (GRID_WIDTH, GRID_HEIGHT)

# Set up the main window and connect to callback routine that draws everything.
def build_and_launch_main_window():
    DBG=1;
    win = CGRAWin();
    if (DBG): win.move(0,0) # put window at top left corner of screen
    if (DBG>=2): print dir(win.props)
    win.show_all()
    Gtk.main()

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
    
    for i in TILE_LIST: TILE_LIST[i] = Tile(i)
    # return TILE_LIST

##############################################################################
# Actual runcode starts here!  (FINALLY)

scenario = "demo2"

if (1):
    DBG=1

    initialize_tile_list(4,4)

    scriptname = sys.argv[0];
    args = sys.argv[1:];

    # Open a channel to the example decoded bitstream
    # filename = sys.argv[1];
    # filename = args[0];
    filename = "./examples/calebscript.bs-decoded"

    # call(["ls", "-l", "examples"]) # exec/run/shell

    if DBG: print "Using", filename, "as input";
    try:
        # filename = sys.argv[1];
        inputstream = open(filename);
    except IOError:
        # TODO/FIXME yeah these were copies from somewhere else obviously
        print ""
        print "Cannot find processor bitstream file '%s'.  Usage:" % filename;
        print "  ", scriptname, "[-debug] <procfile.csv.in> > <procfile.csv.out>"
        print "\nExample:"
        print "  alias dbcheck", scriptname;
        print "  set pfile = /nobackup/steveri/github/cpu-db/data/processors.csv"
        # print "  dbcheck $pfile > /tmp/processors.csv.%d" % +os.getpid()
        sys.exit(-1);

    tile = TILE_LIST; # A convenient handle

    for line in inputstream:
        if (DBG>1): print line.rstrip()
        # Search each line for connections

        # Ignore hacks for now at least
        if (re.search("HACK", line)): continue

        # foundtileno = re.search("^TILE *([0-9]*)", line)
        # I guess python uses '\A' instead of '^' :(
        foundtileno = re.search("^\s*TILE\s*([0-9]+)", line)
        if (foundtileno):
            tileno = int(foundtileno.group(1))
            if (DBG>1): print "*** Found tile %d" % tileno
            continue

        teststring = line
        while True:
            # Want to find all connections of the form "out_s0t0 <= in_s1t0"
            # BUT NOT e.g. "regB <= 0x0000" 'out_s1t0 <= pe_out' 'out <= MUL(wireA,wireB)'
            # x = re.search("(o[^ ]* *<= *i[^ ]*)(.*)", teststring)

            # NO list all connections and let GOD sort 'em out...
            x = re.search("([^ ]* *<= *[^ ]*)(.*)", teststring)

            # OR: x = re.search("(\S*\s*<=\s*\S*)(.*)", teststring)
            if (x):
                connection = x.group(1)
                print "Tile %d found connection '%s'" % (tileno,connection)
                teststring = x.group(2)
                tile[tileno].connect(connection)
            else:
                break;

    inputstream.close()

    build_and_launch_main_window()
    sys.exit(0)


if (scenario == "demo1"):

    # Initialize a 2x2 tile array
    initialize_tile_list(2,2)

    # Demo 1 assumes a 2x2 grid and makes some connections
    demo_connections_2x2()

    # Set up the main window and connect to callback routine that draws everything.
    # Currently builds a window such that 2x2 grid fits in window at 2x scale
    build_and_launch_main_window()


    # TBD: demo2 builds sample connections for a 4x4 grid at 1x scale (demo1 was 2x)


if (scenario == "demo2"):

    # Initialize 4x4 tile array
    initialize_tile_list(4,4)

    # Demo 2 makes same connections as 2x2 except in a 4x4 grid now
    demo_connections_4x4()

    # Set up the main window and connect to callback routine that draws everything.
    # Currently builds a window such that 2x2 grid fits in window at 2x scale
    build_and_launch_main_window()



##############################################################################
# Notes

# http://pycairo.readthedocs.io/en/latest/reference/context.html?
# highlight=set_dash#cairo.Context.set_dash

