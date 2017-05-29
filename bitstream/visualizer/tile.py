#!/usr/bin/python
import sys
import re

# gi a.k.a. pygobjects, pygtk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk
import cairo

#TODO
# Put FU in each tile and connections to/from FU

from math import pi
PI = pi
def deg2rad(rad): return rad*180/PI

GRID_WIDTH  = 2;
GRID_HEIGHT = 2;

# tileno-to-RC conversion
def tileno2rc(tileno): return (tileno % GRID_HEIGHT, int(tileno / GRID_WIDTH))

# A really dumb way to keep track of current scale factor, for
# button-press events
SCALE_FACTOR = 0;

# Could/should derive these from "BUS:5" etc.
NTRACKS_PE_BUS_H = 5;
NTRACKS_PE_BUS_V = 5;

NTRACKS_PE_WIRE_H = 0;
NTRACKS_PE_WIRE_V = 0;

# ARROWHEAD_LENGTH = 2; ARROWHEAD_WIDTH = 4; # meh
ARROWHEAD_LENGTH = 3; ARROWHEAD_WIDTH = 2; # this is nice

# Here's a dumb way to pass information from the button-press handler to the draw-event handler
ZOOM_TO_TILE = -1;

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
    

# cleanup bookmark

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

# What's this?  What's THIS???
# >>> def opt_fun(x1, x2, *positional_parameters, **keyword_parameters):
# ...     if ('optional' in keyword_parameters):
# ...         print 'optional parameter found, it is ', keyword_parameters['optional']
# ...     else:
# ...         print 'no optional parameter, sorry'

# E.g. "drawport(cr, "in_s0t0")
# E.g. "drawport(cr, "in_s0t0", options="reg,arrowhead,box")


def drawport(cr, wirename, **keywords):
    DBG = 0;

    if (DBG): print "Drawing port for wire '%s'..." % (wirename)

    optionlist = []
    if ('options' in keywords):
        if (DBG): print 'options parameter found, it is ', keywords['options']
        optionlist = keywords['options'].split(',')
        if (DBG): print "Found the following options: "+ str(optionlist)
        # for o in options: print "  " + o
    else:
        if (DBG): print 'no options parameter, sorry'

    # x,y coords below are NW (UL) corner


    # TODO don't need w,h
    # (x,y,  w,h,  rot) = connectionpoint(wirename)

    # TODO don't need w,h,rot
    (x,y) = connectionpoint(wirename)
    # drawdot(cr,x,y, "black")
    cr.stroke()

    cr.save()

    # Translate an rotate the world...
    #         if (DBG): print "Translate to %d,%d" % (x,y),
    cr.translate(x,y)
    s = side(wirename)
    rot = s * 3.1416/2
    if (DBG): print "rotate %d degrees\n" % int(180*rot/3.1416)
    cr.rotate(rot)

    # Now origin is connection point and world is oriented to the appropriate side

#         if (s==0): y = y - PORT_WIDTH/2 
#         if (s==1): x = x + PORT_WIDTH/2
#         if (s==2): y = y + PORT_WIDTH/2 
#         if (s==3): x = x - PORT_WIDTH/2

    # if (s==2): rot = 0;

    # cr.set_source_rgb(0,0,1) # blue
    setcolor(cr, 'blue')
    cr.set_line_width(.2)

    # Should be like "if ('box' in options):"
    pwid = PORT_WIDTH; plen = PORT_HEIGHT
    # if (0): cr.rectangle(0,0,  plen,pwid)      # ULx, ULy, width, height
    if (0): cr.rectangle(0, -PORT_WIDTH/2,  plen,pwid)      # ULx, ULy, width, height

    cr.stroke()



#         # FIXME maybe should instead be "side = get_side(wirename)"
#         decode = re.search('(in|out)_s(.*)t.*', wirename);
#         inout = str(decode.group(1))
#         side  = int(decode.group(2))


    ########################################################################
    # Arrow
    # FIXME side 2 wires are pointing the wrong way!!
    cr.save()


    # FIXME this should be a build_arrow subroutine that returns a path
    cr.new_path()
    # cr.set_source_rgb(0,0,1) # blue
    if ('ghost' in optionlist):
        # print "AH!  A GHOST!"
        cr.set_source_rgb(.8,.8,1) # slightly darker ghost
    else:
        # cr.set_source_rgb(0,0,1) # blue
        setcolor(cr, 'blue')

    # For demonstration purposes,
    # tracks 0-2 are buses (thick) and tracks 3,4 are wires (thin)

    # FIXME maybe should hav global parms LINEWIDTH_BUS LINEWIDTH_WIRE
    if (track(wirename) < 3): linewidth = 1.0;
    else:                     linewidth = 0.5;
    cr.set_line_width(linewidth)

    #         cr.move_to(0,           PORT_WIDTH/2)
    #         cr.line_to(PORT_HEIGHT, PORT_WIDTH/2)
    (arrlen,arrwid) = (ARROWHEAD_LENGTH, ARROWHEAD_WIDTH)

    margin = 2*linewidth

    cr.move_to(0,0)
    cr.line_to(PORT_HEIGHT-margin,0)
    # cr.line_to(PORT_HEIGHT-2, -1)
    # cr.line_to(PORT_HEIGHT-3, -1)
    cr.line_to(PORT_HEIGHT-margin-arrlen, -arrwid/2)

    cr.move_to(PORT_HEIGHT-margin,0)
    cr.line_to(PORT_HEIGHT-margin-arrlen, arrwid/2)

    path = cr.copy_path()
    cr.new_path()
    ########################################################################

    # cr.new_path()

    flip = False;

    # Flip the sense of the arrow for "in" wires
    if (inout(wirename) == "in"): flip = (not flip);

    # Flip the sense of the arrow for side==2
    # if (side(wirename) == 2): flip = (not flip);



    # Set origin to center left side of box
    # cr.translate(0, PORT_WIDTH/2)

    # Input wires start at opposite end of box and point i
    # if (inout(wirename) == "in"):

    # "flipped" arrows start at opposite end of box and point in
    if (flip):
        cr.translate(PORT_HEIGHT,0)
        cr.rotate(3.1416)

    cr.append_path(path)
    cr.stroke()
    # cr.cairo_path_destroy(path)

    cr.restore()


    ########################################################################
    # Register
    # cr.set_source_rgb(1,0,0) # red
    setcolor(cr, 'red')
    # (rx,ry) = (-REG_HEIGHT, (PORT_WIDTH-REG_WIDTH)/2)
    (rx,ry) = (-REG_HEIGHT, (-REG_WIDTH)/2)

    if (side==2): rx = PORT_HEIGHT;

    # Draw the register
    cr.rectangle(rx,ry,  REG_HEIGHT, REG_WIDTH) # ULx, ULy, width, height

    # Draw the little triangle for the clock
    cr.move_to(rx,ry); cr.line_to(rx+REG_HEIGHT/2,ry+1); cr.line_to(rx+REG_HEIGHT,ry)
    cr.stroke()


    ########################################################################
    # Label

    # Label color: light gray for "ghost" text, otherwise just red
    if ('ghost' in optionlist):
        cr.set_source_rgb(1,.8,.8)  # light gray
    else:
        cr.set_source_rgb(1,0,0)    # red

    # Position: one pixel in, and just high enough to clear the arrowhead
    # (x,y) = (1, -2.5)
    (x,y) = (1, -ARROWHEAD_WIDTH)
    # drawdot(cr,x,y,"blue")
    # drawdot(cr,0,0,"red")

    # "input" wires get moved to right ot get out of the way of the arrowhead
    if (inout(wirename) == "in"):
        # if (side(wirename) != 2): x = x + 4
        if (side(wirename) != 2): x = x + (ARROWHEAD_LENGTH + 1)

    # Ports on side 2 (W side) should not be upside-down!
    if (side(wirename)==2):
        cr.rotate(PI);
        cr.translate(-PORT_HEIGHT, 0)

    cr.set_font_size(2.5)

    # Could I think use "text_path" to e.g. right-justify labels etc.
    # cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.move_to(x,y)
    cr.show_text(wirename)
    cr.stroke()

    cr.restore()

def drawtileno(cr, tileno):

    # Put a big ghost-number in the middle of the tile
    # See https://www.cairographics.org/manual/cairo-text.html#cairo-text-extents

    tilestr = str(tileno)

    cr.save()

    # Ghost color= light gray
    # graylevel = 0.9; cr.set_source_rgb(graylevel,graylevel,graylevel)
    setcolor(cr, 'ghostgray')

    cr.set_font_size(20)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    # print cr.text_extents(tilestr)

    # E.g. cr.text_extents("100") => (3, -15, 38, 15, 42, 0) => (UL(x,y), w, h, begin_next(x,y)
    (ULx, ULy, w, h, nextx, nexty) = cr.text_extents(tilestr)

    centerx = CANVAS_WIDTH/2
    centery = CANVAS_HEIGHT/2

    x = centerx - w/2 - ULx
    y = centery + h/2

    # cr.set_source_rgb(1,0,0); drawdot(cr, centerx, centery, 'red'
    # cr.set_source_rgb(0,0,1); drawdot(cr, x+ULx, y+ULy, 'blue')
    # cr.set_source_rgb(1,0,1); drawdot(cr, x, y, 'purple')

    cr.move_to(x,y)
    cr.show_text(tilestr)
    cr.stroke()
    cr.restore()

    # sys.exit(0)

#     x = CANVAS_WIDTH/2
#     cr.move_to(x,y)
#     cr.show_text(wirename)


def drawtile(cr):
    cr.save()
    # cr.set_source_rgb(0,0,0) # black
    setcolor(cr,'black')
    cr.set_line_width(.5)
    w = CANVAS_WIDTH  - 2*PORT_HEIGHT
    h = CANVAS_HEIGHT - 2*PORT_HEIGHT
    (ULx,ULy) = (PORT_HEIGHT,PORT_HEIGHT)
    cr.rectangle(ULx,ULy,  w, h) # ULx, ULy, width, height
    cr.stroke()
    cr.restore()

def connectwires(cr, connection):

    # E.g. these should all work:
    #     connectwires(cr, "in_s3t0 => out_s2t3")
    #     connectwires(cr, "in_s3t0 out_s2t3")
    #     connectwires(cr, "in_s3t0 connects to out_s2t3")
    #     connectwires(cr, "  in_s3t0 connects to out_s2t3  ")

    parse = re.search( "([A-z_0-9]+).*[^A-z_0-9]([A-z_0-9]+)[^A-z_0-9]*$", connection)
    w1 = parse.group(1)
    w2 = parse.group(2)

    drawport(cr, w1)
    drawport(cr, w2)

    # TODO add a "if (DBG)" here maybe
    # print "connection = " + connection
    # print "Connecting wires '%s' and '%s'\n" % (w1,w2)

    # 1. Find join point of the two wires
    # 1a. Find each wires connection point at tile's edge

    ULrotpoint1 = connectionpoint(w1) # upper-left corner of enclosing box oriented to side 0
    x1 = ULrotpoint1[0]
    y1 = ULrotpoint1[1]

    ULrotpoint2 = connectionpoint(w2) # upper-left corner of enclosing box oriented to side 0
    x2 = ULrotpoint2[0]
    y2 = ULrotpoint2[1]


    # dot = drawdot(cr,x1,y1,'red')
    # drawdot(cr,x1,y1,'red')
    # drawdot(cr,x2,y2,'red')

    # Okay now connect the dots!
    cr.save()
    # TODO if (isbus): linewidth = 1 etc.
    if (x1 == PORT_HEIGHT): interior = (x2,y1)
    else:                   interior = (x1,y2)

    # cr.set_source_rgb(0,0,1) # blue
    setcolor(cr,'blue')
    cr.set_line_width(.5)
    drawdot(cr,interior[0],interior[1],'blue')
    cr.move_to(x1,y1)
    cr.line_to(interior[0],interior[1])
    cr.line_to(x2,y2)
    cr.stroke()
    cr.restore()


#         dot = build_dot(cr,x,y) # returns a path
#         cr.append_path(dot)
#         cr.stroke()



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
    # print widget; print cr

    # global DRAW_HANDLER_CR; DRAW_HANDLER_CR = cr;
    global CUR_DRAW_WIDGET; CUR_DRAW_WIDGET = widget;

    global ZOOM_TO_TILE
    tileno = ZOOM_TO_TILE
    if (tileno == -1):
        draw_all_tiles(cr);
    else:
        draw_one_tile(cr, tileno);

#     if (1): draw_all_tiles(cr);
#     if (0): draw_one_tile(cr,0);

def draw_one_tile(cr, tileno):
    cr.save()

    # scalefactor = 10 # zoom in for debugging
    # cr.scale(scalefactor,scalefactor)

    ########################################################################
    # Scale and translate

    global SCALE_FACTOR;
    
    # For now, unzoomed (grid) view is scaled to 2x.
    # And zoomed (onetile) view is 2x of that.  Ish.
    # Except that, for no good reason, want the zoomed tile
    # to occupy the same space as four unzoomed tiles.

    # OLD: Draw at 4x requested size
    # SCALE_FACTOR = 4

    # New (see above):
    SCALE_FACTOR = float(4*CANVAS_WIDTH - 4*PORT_LENGTH)\
                  /float(  CANVAS_WIDTH - 2*PORT_LENGTH)

    cr.scale(SCALE_FACTOR,SCALE_FACTOR)

    ########################################################################
    # Translate, so as to
    # make a little whitespace margin at top and left

    # OLD: cr.translate(ARRAY_PAD, ARRAY_PAD)

    # NEW: Want corners to match.
    # Original window size (before scaling) was 4c+2a
    unscaled_window_size   = (4*CANVAS_WIDTH+2*ARRAY_PAD)/SCALE_FACTOR

    # New window holds a single canvas after scaling which, if we center it,
    # should match grid outlines because of carefully crafted scale factor above.
    ONETILE_PAD = (unscaled_window_size - CANVAS_WIDTH)/2

    cr.translate(ONETILE_PAD, ONETILE_PAD)


    print "Drawing tile %s!" % str(tileno)
    if (0): print "...at scale factor %d/%d = %f." \
        % ((2*CANVAS_WIDTH-2*PORT_LENGTH),(CANVAS_WIDTH-2*PORT_LENGTH), SCALE_FACTOR)
    tile[tileno].draw(cr)
    cr.restore()


def draw_all_tiles(cr):

    print "Draw all tiles!"
    cr.save()
    # Make a little whitespace margin at top and left
    # cr.translate(100,100)
 
    # Make a little whitespace margin at top and left (scale independent)
    cr.translate(ARRAY_PAD, ARRAY_PAD)

    # Draw at 4x requested size
    # cr.scale(4,4)
    # cr.scale(2,2)
    # cr.scale(1,1)
    global SCALE_FACTOR; SCALE_FACTOR = 2
    cr.scale(SCALE_FACTOR,SCALE_FACTOR)

    draw_big_ghost_arrows(cr)

    # http://pycairo.readthedocs.io/en/latest/reference/context.html?highlight=set_dash#cairo.Context.set_dash

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

    tile[0].draw(cr)
    tile[1].draw(cr)
    tile[2].draw(cr)
    tile[3].draw(cr)
    cr.restore()



def info(self):
    print "I am tile number %d;" % (tileno),
    print "I live in a grid that is %s tiles high and %s tiles wide"\
        % (GRID_WIDTH, GRID_HEIGHT)
        # % (arrwidth, arrheight);


def main():

    # Set up the main window and connect to callback routine that draws everything.

    print "This is where I build a canvas of width %d and height %d" \
          % (CANVAS_WIDTH, CANVAS_HEIGHT)

    # Big enough to draw 2x2 grid at double-scale, plus 100 margin all around
    # (w,h) = (4*CANVAS_WIDTH+200,4*CANVAS_HEIGHT+200)
    (w,h) = (4*CANVAS_WIDTH+2*ARRAY_PAD,4*CANVAS_HEIGHT+2*ARRAY_PAD)
    win = Gtk.Window(height_request=h, width_request=w)

    win.move(0,0) # put window at top left corner of screen
    win.set_title("Tilesy")
    # win.props.height_request=canvas_height
    # win.props.width_request =canvas_width
    # print dir(win.props)

    # This should all be in __init__ maybe

    win.da = Gtk.DrawingArea(height_request=h, width_request=w)
    win.add(win.da)
    # print dir(win.da.props)

    # An dumb way to keep track of the current window and drawing area widget
    # global CUR_WINDOW;      CUR_WINDOW = win;
    global CUR_DRAW_WIDGET; CUR_DRAW_WIDGET = win.da;

    # "draw" event results in drawing everything on drawing area da
    draw_handler_id = win.da.connect("draw", draw_handler)

    # https://stackoverflow.com/questions/23946791/mouse-event-in-drawingarea-with-pygtk
    # http://www.pygtk.org/pygtk2tutorial/sec-EventHandling.html
    button_press_handler_id = win.da.connect("button-press-event", button_press_handler)

    # FIXME/TODO add to 0bugs and/or 0notes: gtk.gdk.BUTTON_PRESS_MASK = Gdk.EventMask.BUTTON_PRESS_MASK
    win.da.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

    win.connect("delete-event", Gtk.main_quit)

    win.show_all()
    Gtk.main()

def button_press_handler(widget, event):
    DBG = 0

    print ""
    # if (0): print "matrix = " + str(DRAW_HANDLER_CR.get_matrix()) # it's always (1,0,0,1,0,0)
    print "SCALE_FACTOR %s" % SCALE_FACTOR
    print ""

    # print event.x, ' ', event.y
    x = event.x; y = event.y

    # Subtract off the scale-independent paddings and
    # divide by scale factor I guess
    x = (x - ARRAY_PAD)/SCALE_FACTOR; y = (y - ARRAY_PAD)/SCALE_FACTOR;
    # print "Transformed x,y = (%d,%d)" % (x,y)
    # print "CANVAS_WIDTH = %d" % CANVAS_WIDTH

    row = y/CANVAS_WIDTH; col = x/CANVAS_HEIGHT;
    row = int(row); col = int(col)

    tileno = GRID_WIDTH*col + row
    print "I think this is tile %d (r%d,c%d)" % (tileno, row,col)

    global ZOOM_TO_TILE;
    if (ZOOM_TO_TILE == -1):
        if (DBG): print "Zoom in to tile %s!" % str(tileno)
        ZOOM_TO_TILE = tileno;
        # draw_one_tile(DRAW_HANDLER_CR, tileno)
    else:
        if (DBG): print "Zoom out!"
        ZOOM_TO_TILE = -1;
        # draw_all_tiles(DRAW_HANDLER_CR)

    # Redraw (after every button push?) (yes, for now)
    CUR_DRAW_WIDGET.queue_draw()

class Tile:
#     id = -1;
#     (row,col) = (-1,-1)
#     self.connectionlist = []

    def __init__(self, id):
        self.id = id
        # self.row = id % GRID_HEIGHT
        # self.col = int(id / GRID_WIDTH)
        (self.row,self.col) = tileno2rc(id)
        self.connectionlist = []

    def connect(self,connection):  self.connectionlist.append(connection)

    def printprops(self):
        print "Tile %d (r%d,c%d)" % (self.id, self.row, self.col)
        indent = "                "
        print indent + ("\n"+indent).join(self.connectionlist)

    # Todo: maybe two separate routines, one for draw-in-grid and one for draw-standalone etc
    def draw(self, cr):
        
        cr.save()

        if (ZOOM_TO_TILE == -1):
            cr.translate(self.col*CANVAS_WIDTH, self.row*CANVAS_HEIGHT)

        drawtileno(cr, self.id)
        draw_all_ports(cr)
        for c in self.connectionlist: connectwires(cr, c)
        drawtile(cr)
        cr.restore()


def example1():

    # This will be "example1"
    # Enable these commands maybe:

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



def build_tile_array(w,h):
    tile = range(0, w*h)
    for i in tile: tile[i] = Tile(i)
    return tile

# This has to be global (for now at least)
tile = build_tile_array(GRID_WIDTH,GRID_HEIGHT)

# Set up the tiles, make the connections
example1()

# Set up the main window and connect to callback routine that draws everything.
main()



# # Zoom in on a single tile
# def draw_tile(i):
    # tile[i].zoom_# # # # # # # # # # in();


