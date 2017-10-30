#!/usr/bin/python

'''
To do this RIGHT...need to...
look in cgra_info for something like
    <sb feature_address='5' bus='BUS16'>
        <sel_width>2</sel_width>
        <mux snk='out_BUS16_S0_T0' reg='1' configh='1' configl='0' configr='40'>
          <src sel='0'>in_BUS16_S1_T0</src>
          <src sel='1'>in_BUS16_S2_T0</src>
          <src sel='2'>in_BUS16_S3_T0</src>
          <src sel='3'>pe_out_res</src>
        </mux>
...
decode_r0 would look for configbits between 0 and 31 
decode_r0 would look for configbits between 32 and 63
build a data structure maybe

  sb_connections_r0["0x3,3"] = ('out_BUS16_S0_T0','in_BUS16_S1_T0')
  sb_registers_r1["0x100"] = ('out_BUS16_S0_T0')


use the data structure like this sorta

  for (c in sb_connections_r0):
      parse = regexp("(.*),(.*)", c)
      mask = parse.group(1); val = parse.group(2)

'''
import re
import sys

# def sb_decode_cgra(bitstream_line):
#     '''
#     # Given a bitstream line e.g. "00050008 00000003",
#     # return FALSE if element is not a switchbox;
#     # otherwise return a connection dict and a reg list e.g.
#     #   connect["out_BUS16_S0_T0"] = "pe_out_res"
#     #   regs = ("out_BUS16_S0_T0", "out_BUS16_S1_T1")
#     '''
# 
#     regs = []
#     connections = {}
# 
#     # Address RREETTTT
#     f = re.search("(..)(..)(....) (........)", bitstream_line);
#     if (not f): return False;
# 
#     RR = f.group(1);       # register
#     EE = f.group(2);       # element
#     TTTT = f.group(3);     # tile
#     DDDDDDDD = f.group(4); # data
# 
# #     sb = get_switchbox(EE,TTTT)
# #     if (sb == False):
# #         # print "FOO not a switchbox"
# #         return (False,False)
# 
#     e = get_element(EE, TTTT)
#     if (e == False):      return (False, False)
#     elif (e.tag != 'sb'): return (False, False)
#     sb = e

# def build_mask(bith,bitl):
def extract_field(dword, bith, bitl):
    '''
    Given a (32-bit) data word "dword" extract the value
    in the field bounded by bits bith and bitl inclusive.
    E.g. extract_field(0x0000C000, 15,14) = 3
    '''
    DBG = 0
    field_width = bith - bitl + 1
    field_mask  = 2**field_width - 1
    mask = field_mask << bitl
    if DBG: print("    mux mask 0x%x = (0x%x << %d)" \
                  % (mask, field_mask, bitl))
    # return mask
    rval = (dword & mask) >> bitl
    if DBG: print "    val 0x%08x >> %d = %d" % (dword & mask, bitl, rval)
    return rval

def mem_decode(e,DDDDDDDD):
    '''
    # When we see this:
    #   00080011 00000204
    # 
    # We call this function with a pointer to the xml (below)
    # and the data (DDDDDDDD = "00000204")
    # 
    # We use this:
    # <mem feature_address='8' data_bus='BUS16' control_bus='BUS1'>
    #    <mode bith='1' bitl='0'>00</mode>
    #    <tile_en bit='2'>0</tile_en>
    #    <fifo_depth bith='15' bitl='3'>0</fifo_depth>
    #    <almost_full_count bith='18' bitl='16'>0</almost_full_count>
    #    <chain_enable bit='19'>0</chain_enable>
    # </mem>
    #
    # To print this:
    #    # data[(1, 0)] : mode = linebuffer      
    #    # data[(2, 2)] : tile_en = 1            
    #    # data[(15, 3)] : fifo_depth = 64       
    #    # data[(18, 16)] : almost_full_count = 0
    #    # data[(19, 19)] : chain_enable = 0     
    '''

    # for se in e: print se

    for se in e:
        if se.tag == 'mode':
            # mode: 00=LB 01=FIFO 10=SRAM 11=reserved
            mode = range(4)
            mode[0] = "linebuffer"
            mode[1] = "fifo"
            mode[2] = "sram"
            mode[3] = "INVALID MODE 3"
            data = int(DDDDDDDD,16)
            bith = int(se.attrib['bith'])
            bitl = int(se.attrib['bitl'])
            val = extract_field(data, bith, bitl)
            print "# data[(%d, %d)] : mode = %s" % (bith, bitl, mode[val])

        elif se.tag == 'tile_en':
            data = int(DDDDDDDD,16)
            bith = int(se.attrib['bit'])
            bitl = int(se.attrib['bit'])
            val = extract_field(data, bith, bitl)
            print "# data[(%d, %d)] : tile_en = %d" % (bith, bitl, val)

        elif se.tag == 'almost_full_count':
            # IN: <almost_full_count bith='18' bitl='16'>0</almost_full_count>            
            # OUT: # data[(18, 16)] : almost_full_count = 0
            data = int(DDDDDDDD,16)
            bith = int(se.attrib['bith'])
            bitl = int(se.attrib['bitl'])
            val = extract_field(data, bith, bitl)
            print "# data[(%d, %d)] : almost_full_count = %d" % (bith, bitl, val)

        elif se.tag == 'chain_enable':
            data = int(DDDDDDDD,16)
            bith = int(se.attrib['bit'])
            bitl = int(se.attrib['bit'])
            val = extract_field(data, bith, bitl)
            print "# data[(%d, %d)] : chain_enable = %d" % (bith, bitl, val)

        elif se.tag == 'fifo_depth':
            data = int(DDDDDDDD,16)
            bith = int(se.attrib['bith'])
            bitl = int(se.attrib['bitl'])
            val = extract_field(data, bith, bitl)
            print "# data[(%d, %d)] : fifo_depth = %d" % (bith, bitl, val)

def cb_decode(cb,tileno,DDDDDDDD):
    # IN:
    # 00040011 00000005
    # <cb feature_address='4' bus='BUS1'>
    #     <sel_width>4</sel_width>
    #     <mux snk='d'>
    #       <src sel='0'>in_BUS1_S0_T0</src>
    #       <src sel='1'>in_BUS1_S0_T1</src>
    #       <src sel='2'>in_BUS1_S0_T2</src>
    #       <src sel='3'>in_BUS1_S0_T3</src>
    #       <src sel='4'>in_BUS1_S0_T4</src>
    #       <src sel='5'>in_BUS1_S2_T0</src>
    #       <src sel='6'>in_BUS1_S2_T1</src>
    #       <src sel='7'>in_BUS1_S2_T2</src>
    #       <src sel='8'>in_BUS1_S2_T3</src>
    #       <src sel='9'>in_BUS1_S2_T4</src>
    # OUT:
    # data[(3, 0)] : @ tile (3, 2) connect wire 5 (in_0_BUS16_2_0) to din
    DBG=0
    if DBG: print "Found %s %s" % (cb.tag, str(cb.attrib))

    # FIXME every 'iter' should instead probably be a 'findall'!
    for sw in cb.iter('sel_width'):

        # HACK/WRONG/FIXME?
        configl = 0
        sel_width = int(sw.text)
        configh = sel_width - 1

    # FIXME every 'iter' should instead probably be a 'findall'!
    for mux in cb.iter('mux'):
        outwire = mux.attrib['snk']

        # HACK/FIXEM/WHY??
        if (outwire == 'd'): outwire = 'din'

        if DBG: print "  Found %s %s w/outwire %s" % (mux.tag, str(mux.attrib), outwire)
        for src in mux.iter('src'):
            if DBG: print "    Found %s %s" % (src.tag, str(src.attrib))
            data = int(DDDDDDDD,16)
            sel  = int(src.attrib['sel'])
            wireno = sel
            if (data == sel):
                inwire = src.text
                [r,c] = tileno2rc(tileno); rc = "(%d, %d)" % (r,c);
#                 if SWAP: (r,c) = (c,r)
                print "# data[(%d, %d)] : @ tile (%d, %d) connect wire %d (%s) to %s"\
                      % (configh,configl,r,c,wireno,inwire,outwire)
#                 if SWAP: (r,c) = (c,r)
                return inwire
                # break;
                



# def sb_decode_cgra(sb,RR,DDDDDDDD):
def sb_decode(sb,RR,DDDDDDDD):
    '''
    # Given a pointer to a switchbox element in the xml,
    # return a connection dict and a reg list e.g.
    #   connections["out_BUS16_S0_T0"] = (1, 0, 3, "pe_out_res")
    #   regs = ("out_BUS16_S0_T0", "out_BUS16_S1_T1")
    '''
    DBG=0
    regs = []
    connections = {}

    if DBG: print "Found %s %s" % (sb.tag, str(sb.attrib))
    # FIXME every 'iter' should instead probably be a 'findall'!
    for mux in sb.iter('mux'):
        if DBG: print "  Found %s %s" % (mux.tag, str(mux.attrib))

        # Process the register
        # reg     = mux.attrib['reg']
        is_registered = False;
        if 'configr' in mux.attrib:
            configr = int(mux.attrib['configr'])
            regno = configr // 32
            regbit = configr % 32
            if DBG: print "    configr bit %3d = reg %d bit %2d" % (configr, regno, regbit)

            if regno != int(RR,16):
                if DBG: print "    wrong register\n"
            else:
                mask = 1 << regbit
                data = int(DDDDDDDD, 16)
                if (mask & data) != 0:
                    snk = mux.attrib['snk']
                    if DBG: print "*** Found registered output for '%s'" % snk
                    is_registered = True;

                    # regs.append(snk)
                    regs.append( (snk, regbit) )

                    if DBG: print "*** Now regs =", ; print regs
                    

        # Process the connection
        configh = int(mux.attrib['configh'])
        configl = int(mux.attrib['configl'])
        snk     = mux.attrib['snk']

        # Check to see if this is the right register
        regno  = configh // 32
        regbit = configh  % 32
        if DBG: print "    configh bit %2d = reg %d bit %2d" % (configh, regno, regbit)

        if regno != int(RR,16):
            if DBG: print "    wrong register"
        else:
            if DBG: print("    Found mux for output '%s'" % snk)


#             mask = build_mask(configh % 32, configl % 32)
#             regbitl = (configl % 32)
# 
# #             field_width = configh - configl + 1
# #             field_mask  = 2**field_width - 1
# #             mask = field_mask << regbitl
# #             if DBG: print("    mux mask 0x%x = (0x%x << %d)" \
# #                           % (mask, field_mask, regbitl))
# 
#             data = int(DDDDDDDD, 16)
#             if DBG: print("    data & mask = 0x%08x & 0x%08x = %08x"\
#                           % (data, mask, data & mask))
#             val = (data & mask) >> regbitl 
#             if DBG: print("    val 0x%08x >> %d = %d"\
#                           % (data & mask, regbitl, val))

            data = int(DDDDDDDD, 16)
            bith= configh % 32; bitl = configl % 32;
            val = extract_field(data, bith, bitl)

            outwire = mux.attrib['snk']
            for src in mux:
                if DBG: print "      Found %s %s %s" % (src.tag, str(src.attrib), src.text)
                sel = int(src.attrib['sel'])
                if (sel == val):
                    inwire = src.text
                    if DBG: print "      ***Found inwire %s" % outwire
                    if DBG: print "      ***Found connection '%s' => '%s'" % (inwire, outwire)
                    connections[outwire] = (inwire,configh,configl,val)
                    if DBG: print "      ***Now connections =", ; print connections
                    
                    break
            if DBG: print "\n\n"
            
    return (regs, connections)


global CGRA
CGRA = False

def read_cgra_info(filename, grid='8x8', verbose=False):
    # https://docs.python.org/3/library/xml.etree.elementtree.html

    # Default config file is e.g. 'cgra_info_8x8.txt' in this directory
    import os
    mydir = os.path.dirname(os.path.realpath(__file__))
    default_filename = mydir + "/cgra_info_" + grid + ".txt"
    if (filename == ''):
        filename = default_filename
        sys.stderr.write("WARNING using default cgra_info file\n  '%s'\n\n" % filename)

    # If cannot open indicated config file (or if config file is blank), try default file
    global CGRA
    import xml.etree.ElementTree
    try:
        if verbose: sys.stderr.write("Using config file '%s'\n\n" % filename)
        CGRA = xml.etree.ElementTree.parse(filename).getroot()
        return
    except:
        sys.stderr.write("WARNING could not open cgra_info file '%s'\n" % filename)
        filename = default_filename
        sys.stderr.write("WARNING will try using default '%s'\n" % filename)
        CGRA = xml.etree.ElementTree.parse(filename).getroot()
        sys.stderr.write("WARNING loaded default '%s'\n\n" % filename)

def tileno2rc(tileno):
    '''
    Search CGRA xml data structure with tile info e.g.
    <tile type='pe_tile_new' tile_addr='0' row='0' col='0' tracks='BUS1:5 BUS16:5 '>
    and return (row,col) corresponding to the given tile number.

    E.g. a 4x4 grid of tiles is numbered 0-15, laid out as shown:

                   tileno                    r,c
                0   1   2   3      (0,0) (0,1) (0,2) (0,3)
                4   5   6   7      (1,0) (1,1) (1,2) (1,3)
                8   9  10  11      (2,0) (2,1) (2,2) (2,3)
               12  13  14  15      (3,0) (3,1) (3,2) (3,3)

    '''
    for tile in CGRA.findall('tile'):
        t = int(tile.attrib['tile_addr'])
        r = int(tile.attrib['row'])
        c = int(tile.attrib['col'])
        if t == int(tileno): return (r,c)
    print "WARNING Cannot find tile '%s' in cgra_info" % str(tileno)
    return (-1,-1)


def rc2tileno(row,col):
    '''
    Search CGRA xml data structure with tile info e.g.
    <tile type='pe_tile_new' tile_addr='0' row='0' col='0' tracks='BUS1:5 BUS16:5 '>
    and return tile number corresponding to given (row,col)
    '''
    DBG = 0
    # DBG = (row==1 and col==3)
    for tile in CGRA.findall('tile'):
        t = int(tile.attrib['tile_addr'])
        r = int(tile.attrib['row'])
        c = int(tile.attrib['col'])
        if DBG: print (r,c,row/2,col)
        if (r,c) == (row,col):
            return t

        # r might be bottom half of a memtile
        elif tile.attrib['type'] == 'memory_tile' and (r,c) == (row-row%2, col):
            if DBG: print "WARNING Specified r,c is bottom half of a memory tile"
            return t

    print "ERROR Cannot find tile corresponding to row %d col %d in cgra_info" \
          % (row,col)

def tiletype(tileno):
    # print "Looking for type of tile %d" % tileno
    for tile in CGRA.findall('tile'):
        t = int(tile.attrib['tile_addr'])
        if (t == tileno):
            return tile.attrib['type']

    print "ERROR Cannot find tile %d in cgra_info" % tileno
    print "ERROR Could not find type for tile %d" % tileno
    sys.exit(-1)


def tile_exists(tileno):
    for tile in CGRA.findall('tile'):
        t = int(tile.attrib['tile_addr'])
        if (t == tileno):
            return True
    return False


def get_element(EE, TTTT):
    '''
    Retrieve the feature associated with element EE in tile TTTT.
    E.g. if EE="05" and TTTT="000C" returns f such that
    f.tag = "sb" etc.
    <sb feature_address='5' bus='BUS16'>
        <sel_width>2</sel_width>
        <mux snk='out_BUS16_S0_T0' reg='1' configh='1' configl='0' configr='40'>
          <src sel='0'>in_BUS16_S1_T0</src>
          <src sel='1'>in_BUS16_S2_T0</src>
    '''
    DBG=0
    global CGRA
    # if (CGRA == False): CGRA = read_cgra_info()
    if (CGRA == False):
        print "ERROR No CGRA data structure.  Did you call read_cgra_info()?"
        sys.exit(-1)

    tileno = int(TTTT,16)
    elemno = int(  EE,16)
    if DBG: print "Looking up tile %d element %d" % (tileno, elemno)
    for tile in CGRA.findall('tile'):
        t = int(tile.attrib['tile_addr'])
        r = int(tile.attrib['row'])
        c = int(tile.attrib['col'])
        if DBG: print "Found tile %2s (r%s c%s)" % (t, r, c)
        if (t == tileno):
            for feature in tile:
                if DBG: print "  Found feature %s" % feature.tag, ; print feature.attrib
                fa = int(feature.attrib['feature_address'])
                if (fa == elemno): return feature
    return False

# def get_switchbox(EE,TTTT):
#     '''
#     Given element EE (e.g. EE="05") in tile TTTT (e.g. TTTT="000C",
#     return False if element is not a switchbox;
#     else return the switchbox.
#     '''
#     e = get_element(EE, TTTT)
#     if e == False: return False;
#     else:          return e


# def get_switchbox(EE,TTTT):
#     '''
#     Given element EE (e.g. EE="05") in tile TTTT (e.g. TTTT="000C",
#     return False if element is not a switchbox;
#     else return the switchbox.
#     '''
#     DBG=0
#     global CGRA
#     if (CGRA == False): CGRA = read_cgra_info()
#     tileno = int(TTTT,16)
#     elemno = int(  EE,16)
#     print "FOO looking up tile %d element %d" % (tileno, elemno)
#     for tile in CGRA.findall('tile'):
#         t = int(tile.attrib['tile_addr'])
#         r = int(tile.attrib['row'])
#         c = int(tile.attrib['col'])
#         if DBG: print "Found tile %2s (r%s c%s)" % (t, r, c)
#         if (t == tileno):
#             for feature in tile:
#                 if DBG: print "  Found feature %s" % feature.tag, ; print feature.attrib
#                 fa = int(feature.attrib['feature_address'])
#                 if (fa == elemno):
#                     if (feature.tag == "sb"): return feature
#                     else: return False;
#     return False

def test():
#     # get_switchbox() test
#     sb = get_switchbox("05","0000")
#     if (sb != False):
#         print "Found switchbox %s %s" % (sb.tag, str(sb.attrib))

    # sb_decode() test
    sb_decode_cgra("00050008 00000003")

    # Should find a register here
    sb_decode_cgra("0105000E 00002000")

    # Maybe this will find two or three registers?  Looks like yes.
    sb_decode_cgra("0105000E 00007000")


    sys.exit(0)

# def read_cgra_info(filename):
#     DBG=9
#     # call(["ls", "-l", "examples"]) # exec/run/shell
#     if DBG: print "Using", filename, "as input";
# 
#     try:
#         inputstream = open(filename);
#     except IOError:
#         # TODO/FIXME yeah these were copies from somewhere else obviously
#         print ""
#         print "ERROR Cannot find processor bitstream file '%s'" % filename
#         print main.__doc__
#         sys.exit(-1);
# 
# 
#     # process_decoded_bitstream_old(inputstream)
#     for line in inputstream:
#         if (DBG>1): print line.rstrip()
#         line = line.strip() # why not
# 
# 
# 
# 
#     inputstream.close()
# 
# # read_cgra_info("examples/cgra_info.txt")
# 
#

# for configr in range(0,128):
#             regno = configr // 32
#             regbit = configr % 32
#             print "configr bit %3d = reg %d bit %2d" % (configr, regno, regbit)
#             if regbit == 31: print ""
#     # print "bit %d is in reg %d" % (b, b // 32)
# sys.exit(0)


