#!/usr/bin/python
import sys
import re

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import cairo

PI = 3.1416
def deg2rad(rad): return rad*180/PI



# TODO Need tileno-to-RC conversion

GRID_WIDTH  = 2;
GRID_HEIGHT = 2;

# Could/should derive these from "BUS!^:5" etc.
NTRACKS_PE_BUS_H = 5;
NTRACKS_PE_BUS_V = 5;

NTRACKS_PE_WIRE_H = 0;
NTRACKS_PE_WIRE_V = 0;

# ARROWHEAD_LENGTH = 2; ARROWHEAD_WIDTH = 4; # meh
ARROWHEAD_LENGTH = 3; ARROWHEAD_WIDTH = 2; # this is nice

ARRAY_PAD = 60

# Should be something like:
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

# FIXME: LENGTH? or HEIGHT?
PORT_WIDTH  = 8;
PORT_HEIGHT = 16;
PORT_LENGTH = PORT_HEIGHT # Because sometimes I forget


# PORT_PAD = PORT_WIDTH/2
PORT_PAD = PORT_WIDTH/2

REG_WIDTH  = PORT_WIDTH - 2;
REG_HEIGHT = 2;

# Canvas size for displaying a single tile edge-to-edge w/ no padding
#   How big is a tile canvas?  Refer to diagram in doc
#   Short answer is:
#     Canvas width  = 2*plen + 2*ntracks_v*pwid + 3*pwid
#     Canvas height = 2*plen + 2*ntracks_h*pwid + 3*pwid
#   where each port is an arrow in a box that's portlength long and portwidth wide
#   and ntracks_v = ntracks_bus_v + ntracks_wire_v etc.
CANVAS_WIDTH  = 2*PORT_HEIGHT + 2*NTRACKS_PE_BUS_V*PORT_WIDTH + 3*PORT_PAD
CANVAS_HEIGHT = 2*PORT_HEIGHT + 2*NTRACKS_PE_BUS_H*PORT_WIDTH + 3*PORT_PAD

def draw_rectilinear_arrow(cr, al, ahl,ahw,fill):
    # Draw an arrow of total length al and line_width aw
    # Arrowhead on the end is a triangle of length ahl, width ahw
    # if "fill" is true, fill in the triangle.
    # Arrow starts at location (0,0); use cr.translate() to place it to (x,y)
    # E.g.
    # cr.save()
    #   cr.translate(x,y)
    #   draw_rectilinear_arrow(al,aw,ahl,ahw,fill)
    # cr.restore()
    PI = 3.1416

    cr.save()

    # Uses aw,al,ahw,ahl

    # The line
    cr.move_to(0,0)
    cr.line_to(al-ahl,0)
    cr.stroke()

    # The arrowhead
    if (fill): cr.set_line_width(1);
    cr.move_to(al-ahl,     -ahw/2)
    cr.line_to(al, 0)
    cr.line_to(al-ahl,     ahw/2)
    if (fill):
        cr.close_path()
        cr.fill()

    cr.stroke()
    cr.restore()

def draw_big_ghost_arrows(cr):

    # Ghost Arrow parms, used by big_ghost_arrow(), 
    apad = 10; # how far arrow sticks outon each side
    ahl = 20 # length of arrowhead
    al = 2*CANVAS_WIDTH + 2*apad + ahl/2  # length of line
    # aw = 30 # width of line
    aw = 10 # width of line
    # ahw = 2*aw # width of arrowhead
    ahw = 3*aw # width of arrowhead

    def draw_big_ghost_arrow(cr,x,y,dir):

        fill = True;
        cr.save()
        cr.translate(x,y)
        cr.set_line_width(aw);
        if (dir=='left'): cr.rotate(PI)
        if (dir=='down'): cr.rotate(PI/2)
        if (dir=='up'):   cr.rotate(3*PI/2)
        draw_rectilinear_arrow(cr,al,ahl,ahw,fill)
        cr.restore()

    # Ghost arrow begins at (-20,CANVAS_HEIGHT-offset-aw/2) and points LEFT
    # self.big_ghost_arrow(cr, -20, CANVAS_HEIGHT-offset-aw/2, 'left')
#         cr.set_source_rgb(0,1,0)

    graylevel = 0.9
    cr.set_source_rgb(graylevel,graylevel,graylevel)

    # Right-pointing arrows start apad back from left edge of the tile,
    # and h_offset down from the top
    ra_start    = -apad;
    ra_v_offset = PORT_LENGTH + 2 * PORT_WIDTH

    # Left-pointing arrows start apad beyond the right edge of the tile,
    # and v_offset up from the bottom
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

def parse_wirename(wirename):
    rval = {}
    decode = re.search('(in|out)_s(.*)t(.*)', wirename);
    rval['inout'] = str(decode.group(1))
    rval['side']  = int(decode.group(2))
    rval['track'] = int(decode.group(3))
    return rval
    

def side(wirename):
#     decode = re.search('(in|out)_s(.*)t(.*)', wirename);
#     inout = str(decode.group(1))
#     side  = int(decode.group(2))
#     track = int(decode.group(3))
    return parse_wirename(wirename)['side']

def track(wirename):
    dict = parse_wirename(wirename)
    return dict['track']

def inout(wirename):
    decode = re.search('(in|out)_s(.*)t(.*)', wirename);
    inout = str(decode.group(1))
    side  = int(decode.group(2))
    track = int(decode.group(3))
    return inout;


# def build_dot(cr,x,y):
def drawdot(cr,x,y):
    dotsize = 1.0
    dotsize = 0.8
    # cr.set_line_width (10.0);
    cr.save()
    cr.arc (x, y, dotsize, 0, 2*PI);
    cr.fill ();
    cr.stroke ();

    # path = cr.copy_path()
    cr.restore()
    # return path
    

def errmsg(m):
    sys.stdout.write("ERROR: %s\n" % (m))
    sys.exit(-1)

class CGRATilePE:

    # Depends on having access to globals GRID_WIDTH, GRID_HEIGHT etc.

    def __init__(self, tileno):
        self.tileno = tileno

#     def connectionpoint(self, wirename):
#         print "Find wirename connection point"





    # FIXME this should return connection point, not stupid UL whatever thingycrap
    def connectionpoint(self, wirename):

        # FIXME comment below is wrong wrong wrong
        # Given wirename e.g. "out_s0t0", return x,y coords of UL (NW) corner)

        # Return (x,y) coord of box corner adjoining tile and closes to the "out" side
        # (see diagram in documentation I guess)
        # Box will be drawn translated to that corner and rotated according
        # to side (0,1,2,3) is (0,90,180,270) degrees respectively

        ntracks_v = NTRACKS_PE_BUS_V + NTRACKS_PE_WIRE_V
        ntracks_h = NTRACKS_PE_BUS_H + NTRACKS_PE_WIRE_H

        # pwid = PORT_WIDTH; plen = PORT_HEIGHT
        # canvas_width  = 2*plen + 2*ntracks_v*pwid + 3*pwid
        # canvas_height = 2*plen + 2*ntracks_h*pwid + 3*pwid
        canvas_width  = CANVAS_WIDTH
        canvas_height = CANVAS_HEIGHT

        decode = re.search('(in_s.*|out_s.*)t(.*)', wirename);
        b = decode.group(1);      # blockno
        t = int(decode.group(2)); # trackno

        pwid = PORT_WIDTH; plen = PORT_HEIGHT
        PL     = PORT_HEIGHT
        # PLPW   = plen + pwid
        # PLPWPW = plen + pwid + pwid
        # PLPW   = plen + pwid/2
        # PLPWPW = plen + pwid/2 + pwid
        PLPW   = plen + pwid
        PLPWPW = plen + pwid

        # 'corner' = Distance from edge of canvas to edge of tile
        # 'pad'    = Distance from edge of tile to first port
        # '2*pad'  = Distance between last outport and first inport

        # corner = PORT_HEIGHT
        # pad    = PORT_PAD

        # side 0: no rotate
        #   out = (cw-pl, pl+t*pw)
        #   in  = (cw-pl, ch-pl-2pw-t*pw)
        if (b == "out_s0"): (x,y) = (canvas_width - PL,                 PLPW   + t*pwid)
        if (b ==  "in_s0"): (x,y) = (canvas_width - PL, canvas_height - PLPWPW - t*pwid)

        # side 1: rotate 90
        #   out = (cw-pl-2pw, ch-pl)
        #   in  = (pl+2pw, ch-pl)
        if (b == "out_s1"): (x,y) = (canvas_width - PLPW   - t*pwid, canvas_height - PL)
        if (b ==  "in_s1"): (x,y) = (               PLPWPW + t*pwid, canvas_height - PL)

        # side 2: no rotate
        #   out = (0, ch-pl-tpw)
        #   in  = (0, pl+2pw+tpw)
        if (b == "out_s2"): (x,y) = (PL, canvas_height - PLPWPW - t*pwid)
        if (b ==  "in_s2"): (x,y) = (PL,                 PLPW   + t*pwid)

        # side 3: rotate 270
        #   out = (pl+2pw+tpw,pl)
        #   in  = (cw-pl-pw-tpw,pl)
        if (b == "out_s3"): (x,y) = (               PLPW   + t*pwid, PL)
        if (b ==  "in_s3"): (x,y) = (canvas_width - PLPWPW - t*pwid, PL)

        # outs1/ins3 blocks start in SE/NE and go left (neg x direction)

        # outs2/ins0 blocks start in SW/SE and go up   (neg y direction)

        # outs3/ins1 blocks start in NW/NE and go right (pos x direction)

        (w,h,rot) = (-12,-12,-12)
#         decode = re.search('(in|out)_s(.*)t.*', wirename);
#         s = int(decode.group(2))
#         if ((s%2)==0): (w,h) = (plen,pwid)
#         if ((s%2)==1): (w,h) = (pwid,plen)


#         rot = s * 3.1416/2
#         if (s==2): rot = 0;

        return (x,y,w,h, rot);

# >>> def opt_fun(x1, x2, *positional_parameters, **keyword_parameters):
# ...     if ('optional' in keyword_parameters):
# ...         print 'optional parameter found, it is ', keyword_parameters['optional']
# ...     else:
# ...         print 'no optional parameter, sorry'

    # E.g. "drawport(cr, "in_s0t0")
    # E.g. "drawport(cr, "in_s0t0", options="reg,arrowhead,box")
    def drawport(self, cr, wirename, **keywords):
        DBG = 0;

        if (DBG): print "Drawing port for wire '%s'..." % (wirename)

        options = []
        if ('options' in keywords):
            if (DBG): print 'options parameter found, it is ', keywords['options']
            options = keywords['options'].split(',')
            if (DBG): print "Found the following options: "+ str(options)
            # for o in options: print "  " + o
        else:
            if (DBG): print 'no options parameter, sorry'

        # x,y coords below are NW (UL) corner


        # TODO don't need w,h
        # (x,y,  w,h,  rot) = self.connectionpoint(wirename)

        # TODO don't need w,h,rot
        (x,y,  w,h,  rot) = self.connectionpoint(wirename)
        # drawdot(cr,x,y)
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

        cr.set_source_rgb(0,0,1) # blue
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
        if ('ghost' in options):
            # print "AH!  A GHOST!"
            cr.set_source_rgb(.8,.8,1) # blue
        else:
            cr.set_source_rgb(0,0,1) # blue



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
        cr.set_source_rgb(1,0,0) # red
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


        # cr.set_source_rgb(1,0,0) # red
        if ('ghost' in options):
            cr.set_source_rgb(1,.8,.8)
        else:
            cr.set_source_rgb(1,0,0)


        # Could I think use "text_path" to e.g. right-justify labels etc.
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        # cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        fs = 2.5
        cr.set_font_size(fs)

        (x,y) = (1, -2.5)
        (x,y) = (1, -ARROWHEAD_WIDTH)
        # drawdot(cr,x,y)
        # drawdot(cr,0,0)


        if (inout(wirename) == "in"):
            if (side(wirename) != 2): x = x + 4

        if (side(wirename)==2):
            cr.rotate(PI);
            cr.translate(-PORT_HEIGHT, 0)

        cr.move_to(x,y)
        cr.show_text(wirename)
        cr.stroke()

        cr.restore()

    def drawtile(self, cr):
        cr.save()
        cr.set_source_rgb(0,0,0) # black
        cr.set_line_width(.5)
        w = CANVAS_WIDTH  - 2*PORT_HEIGHT
        h = CANVAS_HEIGHT - 2*PORT_HEIGHT
        (ULx,ULy) = (PORT_HEIGHT,PORT_HEIGHT)
        cr.rectangle(ULx,ULy,  w, h) # ULx, ULy, width, height
        cr.stroke()
        cr.restore()

    def connectwires(self, cr, connection):

        # E.g. these should all work:
        #     self.connectwires(cr, "in_s3t0 => out_s2t3")
        #     self.connectwires(cr, "in_s3t0 out_s2t3")
        #     self.connectwires(cr, "in_s3t0 connects to out_s2t3")
        #     self.connectwires(cr, "  in_s3t0 connects to out_s2t3  ")

        parse = re.search( "([A-z_0-9]+).*[^A-z_0-9]([A-z_0-9]+)[^A-z_0-9]*$", connection)
        w1 = parse.group(1)
        w2 = parse.group(2)

        self.drawport(cr, w1)
        self.drawport(cr, w2)


        print "connection = " + connection
        print "Connecting wires '%s' and '%s'\n" % (w1,w2)

        # 1. Find join point of the two wires
        # 1a. Find each wires connection point at tile's edge
        
        ULrotpoint1 = self.connectionpoint(w1) # upper-left corner of enclosing box oriented to side 0
        x1 = ULrotpoint1[0]
        y1 = ULrotpoint1[1]

        ULrotpoint2 = self.connectionpoint(w2) # upper-left corner of enclosing box oriented to side 0
        x2 = ULrotpoint2[0]
        y2 = ULrotpoint2[1]


        # dot = drawdot(cr,x1,y1)
        # drawdot(cr,x1,y1)
        # drawdot(cr,x2,y2)

        # Okay now connect the dots!
        cr.save()
        # TODO if (isbus): linewidth = 1 etc.
        if (x1 == PORT_HEIGHT): interior = (x2,y1)
        else:                   interior = (x1,y2)

        cr.set_source_rgb(0,0,1) # blue
        cr.set_line_width(.5)
        drawdot(cr,interior[0],interior[1])
        cr.move_to(x1,y1)
        cr.line_to(interior[0],interior[1])
        cr.line_to(x2,y2)
        cr.stroke()
        cr.restore()


#         dot = build_dot(cr,x,y) # returns a path
#         cr.append_path(dot)
#         cr.stroke()



    def drawgrid(self, cr):

        cr.save()

        cr.set_line_width(.1)
        # cr.set_dash((1,1), 0) # on/off array, length of dashes, begin
        b = 0.8 # brightness
        cr.set_source_rgb(b,b,0) # yellow
        cr.set_source_rgb(0,0,0) # black (for debug)


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

    def draw_all_ports(self,cr):
        for side in (0,1,2,3):
            for dir in ("out", "in"):
                if (side%2 == 0): ntracks = NTRACKS_PE_BUS_H + NTRACKS_PE_WIRE_H; # EW
                if (side%2 == 1): ntracks = NTRACKS_PE_BUS_V + NTRACKS_PE_WIRE_V; # NS
                for track in range(0,ntracks):
                    wirename = "%s_s%dt%d" % (dir, side, track)
                    self.drawport(cr, wirename, options="ghost")

    def callback(self, widget, cr):
        print widget
        print cr

        # cr.translate(100,100)
        cr.translate(ARRAY_PAD, ARRAY_PAD)

        # Draw at 4x requested size
        # cr.scale(4,4)
        # cr.scale(1,1)
        cr.scale(2,2)


        ########################################################################
        # Big ghost arrow(s)
        
        ########################################################################
        # Big ghost arrow(s)
        
        draw_big_ghost_arrows(cr)

        cr.save()

        # http://pycairo.readthedocs.io/en/latest/reference/context.html?highlight=set_dash#cairo.Context.set_dash


        # self.drawgrid(cr)

        if (0):
            self.drawport(cr, "in_s0t0", options="foo,bar,baz")
            self.drawport(cr, "out_s0t0", options="foo")

            self.drawport(cr, "in_s0t1")

            self.drawport(cr, "out_s1t0")
            self.drawport(cr, "in_s1t0")

            self.drawport(cr, "out_s2t0")
            self.drawport(cr, "in_s2t0")

            self.drawport(cr, "out_s3t0")
            self.drawport(cr, "in_s3t0")

        if (1):
            self.draw_all_ports(cr)

#         self.drawport(cr, "in_s3t0")
#         self.drawport(cr, "in_s3t1")
#         self.drawport(cr, "out_s0t0")
#         self.drawport(cr, "out_s1t1")
#         self.drawport(cr, "out_s2t1")

#         # self.connectwires(cr, "in_s3t0", "out_s2t3")
#         self.connectwires(cr, "in_s3t0 => out_s2t3")
#         self.connectwires(cr, "in_s3t0 out_s2t3")
#         self.connectwires(cr, "in_s3t0 connects to out_s2t3")
#         self.connectwires(cr, "  in_s3t0 connects to out_s2t3  ")
        # sys.exit(0)
        self.connectwires(cr, "in_s3t1 => out_s2t1")
        self.connectwires(cr, "in_s3t1 connects to out_s1t1")
        self.connectwires(cr, "in_s3t0 => out_s0t0")

        self.drawtile(cr);
        cr.restore()

        ########################################################################
        # TILE1 SW corner
        cr.save()
        cr.translate(0,CANVAS_HEIGHT)

        self.draw_all_ports(cr)

        self.connectwires(cr, "in_s3t1 => out_s2t1")
        self.connectwires(cr, "in_s3t1 => out_s1t1")
        self.connectwires(cr, "in_s3t1 => out_s0t1")

        self.drawtile(cr);
        cr.restore()

        ########################################################################
        # TILE2 NE corner
        cr.save()
        cr.translate(CANVAS_WIDTH, 0)

        self.draw_all_ports(cr)

        self.connectwires(cr, "in_s2t0 => out_s0t0")
        self.connectwires(cr, "in_s1t1 => out_s0t1")

        self.drawtile(cr);
        cr.restore()

        ########################################################################
        # TILE3 SE corner
        cr.save()
        cr.translate(CANVAS_WIDTH, CANVAS_HEIGHT)

        self.draw_all_ports(cr)

        self.connectwires(cr, "in_s2t1 => out_s3t1")

        self.drawtile(cr);
        cr.restore()


    def drawme_standalone(self):

        print "This is where I build a canvas of width %d and height %d" \
              % (CANVAS_WIDTH, CANVAS_HEIGHT)

        win = Gtk.Window()
        win.move(0,0) # put window at top left corner of screen
        win.set_title("Tilesy")
        # win.props.height_request=canvas_height
        # win.props.width_request =canvas_width
        print dir(win.props)

        # This should all be in __init__ maybe

        # Big enough to draw 2x2 grid at double-scale, plus 100 margin all around
        # (w,h) = (4*CANVAS_WIDTH+200,4*CANVAS_HEIGHT+200)
        (w,h) = (4*CANVAS_WIDTH+2*ARRAY_PAD,4*CANVAS_HEIGHT+2*ARRAY_PAD)
        win.da = Gtk.DrawingArea(height_request=h, width_request=w)
        win.add(win.da)
        print dir(win.da.props)

        handler_id = win.da.connect("draw", self.callback)

        win.connect("delete-event", Gtk.main_quit)

        win.show_all()
        Gtk.main()


        
    def info(self):
        print "I am tile number %d;" % (self.tileno),
        print "I live in a grid that is %s tiles high and %s tiles wide"\
            % (GRID_WIDTH, GRID_HEIGHT)
            # % (self.arrwidth, self.arrheight);


# ntiles = GRID_WIDTH * GRID_HEIGHT;
# 
# tile = range(0,ntiles)
# for i in range (0,ntiles):
#     tile[i] = CGRATilePE(i)
# 
# for i in range (0,ntiles):
#     tile[i] = CGRATilePE(i)
# 
# for i in range (0,ntiles):
#     tile[i].info();
# 
# tile[i].drawme_standalone()
# 
# sys.exit(0)
# 

# tile = CGRATilePE(0)
# tile.drawme_standalone()

CGRATilePE(0).drawme_standalone()


# tile[0].connect("in_s0t0", "out_s1t0")
# ...



# def draw_array():
    # for i in range (0,NTILES):
        # tile[i].zoom_out();


# # Zoom in on a single tile
# def draw_tile(i):
    # tile[i].zoom_# # # # # # # # # # in();


