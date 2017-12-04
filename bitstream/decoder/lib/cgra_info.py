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

# Index:
# def extract_field(dword, bith, bitl):
# def mem_decode(e,DDDDDDDD):
# def cb_decode(cb,tileno,DDDDDDDD):
# def sb_decode(sb,RR,DDDDDDDD):
# def read_cgra_info(filename, grid='8x8', verbose=False):
# def ntiles():
# def tileno2rc(tileno):
# def rc2tileno(row,col):
# def tiletype(tileno):
# def mem_or_pe(tileno):
# def tile_exists(tileno):
# def get_element(EE, TTTT):
# def reachable(rsrc, tileno=0, DBG=0):
# def test():


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

    if bith < bitl:
        print "# ERROR cgra_info.py: bith (%d) is less than bitl (%d) :(" % (bith,bitl)
        print "# ERROR guess we crossed a register boundary!?"
        print "# ERROR will try to recover gracefully ish"
        return 0

    field_width = bith - bitl + 1
    field_mask  = 2**field_width - 1


#     print ""
#     print "fw",; print field_width
#     print "fm",;print field_mask
#     print "bh",;print bith
#     print "bl",;print bitl



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

CGRA_FILENAME_TOP = "CGRAGenerator/hardware/generator_z/top/cgra_info.txt"
def get_generated_cgra_info_filename():
    import os
    mydir = os.path.dirname(os.path.realpath(__file__))
    # print mydir
    parse = re.search('^(.*/)CGRAGenerator', mydir)
    if not parse:
        return ''
    else:
        gendir = parse.group(1)
        return gendir + CGRA_FILENAME_TOP

CGRA_FILENAME_LOCAL = "cgra_info_8x8.txt"
def get_local_cgra_info_filename():
    import os
    mydir = os.path.dirname(os.path.realpath(__file__))
    return mydir + "/" + CGRA_FILENAME_LOCAL

def get_default_cgra_info_filename():
    f = get_generated_cgra_info_filename()
    if f == '':
        f = get_local_cgra_info_filename()
    return f

def read_cgra_info(filename='', grid='8x8', verbose=False):
    # https://docs.python.org/3/library/xml.etree.elementtree.html
    # Default config file is e.g. 'cgra_info_8x8.txt' in this directory
    import os
    mydir = os.path.dirname(os.path.realpath(__file__))

#     default_filename = get_default_cgra_info_filename()

    if (filename == ''):
        sys.stdout.flush()
        sys.stderr.write("WARNING No cgra_info file was specified\n")
        sys.stderr.write("WARNING Looking for generated cgra_info.txt %s\n")
        sys.stdout.flush()
        filename = get_generated_cgra_info_filename()
        if filename != '':
            sys.stderr.write("WARNING Found '%s'" % filename)
        else:
            sys.stderr.write("WARNING Could not find generated info; will default to local copy")
        sys.stderr.flush()

    # If cannot open indicated config file (or if config file is blank), try default file
    global CGRA
    import xml.etree.ElementTree
    try:
        if verbose: sys.stdout.write("Using config file '%s'\n\n" % filename)
        CGRA = xml.etree.ElementTree.parse(filename).getroot()
        return
    except:
        sys.stderr.write("WARNING Could not open cgra_info file '%s'\n" % filename)
        filename = get_local_cgra_info_filename()
        sys.stderr.write("WARNING Will try using local copy '%s'\n" % filename)
        CGRA = xml.etree.ElementTree.parse(filename).getroot()
        sys.stderr.write("WARNING Loaded local copy '%s'\n\n" % filename)

def load_check():
    # if not CGRA:
    # FutureWarning: The behavior of this method will change in future
    # versions.  Use specific 'len(elem)' or 'elem is not None' test instead.
    if CGRA is False:
        print "ERROR cgra_info file not loaded.  Did you do a read_cgra_info()?"
        print ""
        assert False, "\nERROR cgra_info file not loaded.  Did you do a read_cgra_info()?"

def ntiles():
    '''How many tiles?'''
    load_check()
    return len(CGRA.findall('tile')) # length = number of items in list

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

    load_check()

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
        t = tile.attrib['tile_addr']
        if (t == str(tileno)):
            return tile.attrib['type']

    err = ("\n\nERROR Cannot find tile %d in cgra_info\n" % tileno)\
          + ("ERROR Could not find type for tile %d" % tileno)
    assert False, err


def mem_or_pe(tileno):
    type = tiletype(tileno)

    # if   re.search("^mem", type): return 'mem'
    # elif re.search("^pe",  type): return 'pe'

    if   type[0] == 'm': return 'mem'
    elif type[0] == 'p': return 'pe'
    else:
        assert False, 'unknown tile type'
        return 'unknown'

def is_mem(tileno): return (mem_or_pe(tileno)=='mem')

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

def fan_out(rsrc, tileno, DBG=0):
    DBG = max(0,DBG)

    # list all resources in tile that 'rsrc' can reach
    # 'rsrc' can be one of: in*, pe_out_res, wdata, mem_out

    # Rewrites:
    if rsrc == 'mem_out': rsrc = 'rdata'
    if rsrc == 'mem_in':  rsrc = 'wdata'

    if DBG: print 'who can be reached by', rsrc, 'in tile', tileno, '?'
    rlist = find_connectables('fan_out', rsrc, tileno, DBG)

    if DBG: print "         %s can reach %s" % (rsrc,rlist)
    if DBG: print ''

    return rlist


def fan_in(rdst, tileno, DBG=0):
    # list all resources in tile that can reach 'rdst'

    # # Rewrites:
    # if rsrc == 'mem_out': rsrc = 'rdata'
    # if rsrc == 'mem_in':  rsrc = 'wdata'

    if DBG: print 'who can reach', rdst, 'in tile', tileno, '?'
    rlist = find_connectables('fan_in', rdst, tileno, DBG)

    if DBG: print "         %s can be reached by %s" % (rdst, rlist)
    if DBG: print ''

    return rlist


def find_connectables(fan_dir, port, tileno, DBG=0):
    # list all resources in tile that are reachable from 'port'
    # either as source or sink depending on whether 'fan_dir'
    # is 'fan_in' or 'fan_out'

    tile = get_tile(tileno)
    assert tile != -1, '404 tile not found'
    # if DBG: print 'found tile', tileno

    # in_0_BUS16_S2_T0 can connect to ['raddr', 'waddr', 'wdata']

    # in_0_BUS16_S2_T0 can connect to ['raddr', 'waddr', 'wdata']
    # Sometimes e.g. 'in_0_BUS16_1_2' is called 'in_0_BUS16_S1_T2' and
    # vice versa UGH yes it's a bug.  oneworld() "fixes" it
    port = oneworld(port)
    rlist = search_muxes(fan_dir, tile, port, DBG-1)

#     # in_0_BUS16_S2_T0 can connect to ['raddr', 'waddr', 'wdata']
#     # Sometimes e.g. 'in_0_BUS16_1_2' is called 'in_0_BUS16_S1_T2' and
#     # vice versa UGH yes it's a bug.
#     port2 = mem_alias(port)
#     if port2:
#         if DBG: print "        # UGH must also check '%s'" % port2
#         rlist = rlist+search_muxes(fan_dir, tile, port2, DBG-1)
#         port = '%s/%s' % (port,port2)

    return rlist


def search_muxes(fan_dir, tile, port, DBG=0):
    DBG = max(0,DBG)
    port = oneworld(port)
    if fan_dir == 'fan_out':
        sblist = find_sources(tile, 'sb', port, DBG)
        cblist = find_sources(tile, 'cb', port, DBG)
    elif fan_dir == 'fan_in':
        sblist = find_sinks(tile, 'sb', port, DBG)
        cblist = find_sinks(tile, 'cb', port, DBG)
    else:
        assert False

    if DBG>2: print 'sb:', port, 'can connect to', sblist
    if DBG>2: print 'cb:', port, 'can connect to', cblist

    return sblist+cblist


def find_mux(tile, src, snk, DBG=0):
    '''Find the mux that connects "src" to "snk" in "tile"'''
    DBG = max(DBG,0)
    rlist = []
    src = oneworld(src)
    snk = oneworld(snk)
    for box in ['sb','cb']:
        for bb in tile.iter(box):
            for mux in bb.iter('mux'):

                # Can't do single-bit wires (yet)
                if re.search('_BUS1_', mux.attrib['snk']): continue

                # Look for sinks whose src is rdst
                # if mux.attrib['snk'] == rdst:
                # ow = oneworld(mux.attrib['snk'])
                # owsnk = cgra2canon(mux.attrib['snk'], DBG=9)
                owsnk = oneworld(mux.attrib['snk'])
                if owsnk == snk:
                    if DBG: print 'found snk', mux.attrib['snk']
                    for msrc in mux.iter('src'):
                        owsrc = oneworld(msrc.text)
                        if src == owsrc:
                            return get_encoding(tile,bb,mux,msrc,DBG-1)

    return False

def get_encoding(tile,box,mux,msrc,DBG=0):
    DBG = max(DBG,0)
    parms={}

    parms['tileno'] = int(tile.attrib['tile_addr'])
    parms['fa']     = int(box.attrib['feature_address'])
    parms['sel']    = int(msrc.attrib['sel'])

    # want sb/cb item 'sel_width':
    # <cb feature_address='4' bus='BUS1'>
    #     <sel_width>4</sel_width>
    assert box[0].tag == 'sel_width'
    parms['sw'] = int(box[0].text)
    # print '  ', box[0].tag, '=', sw

    if box.tag=='sb':
        parms['configh']= int(mux.attrib['configh'])
        parms['configl']= int(mux.attrib['configl'])
        parms['configr']= int(mux.attrib['configr'])
    else:
        parms['configh']= (parms['sw'] - 1)
        parms['configl']= 0
        parms['configr']= -1
    
    if DBG:
        print 'found src', msrc.text
        print "  tile",            parms['tileno']
        print "  feature address", parms['fa']
        print '  sel',             parms['sel']
        print '  sel_width',       parms['sw']
        print '  configh', parms['configh']
        print '  configl', parms['configl']
        print '  configr', parms['configr']

    return parms


def encode_parms(parms, DBG=0):
    DBG = max(DBG,0)
    if DBG:
        print "  tileno",          parms['tileno']
        print "  feature address", parms['fa']
        print '  sel',             parms['sel']
        print '  sel_width',       parms['sw']
        print '  configh', parms['configh']
        print '  configl', parms['configl']
        print '  configr', parms['configr']
        print ''

    tileno   = parms['tileno']
    fa       = parms['fa'] # feature_address
    sel      = parms['sel']
    sw       = parms['sw'] # sel_width
    configh  = parms['configh']
    configl  = parms['configl']
    configr  = parms['configr']

    if configh == -1: configh=0
    if configl == -1: configl=0
    if configr == -1: configr=0

    # First encode the select field
    regh = configh/32
    regl = configl/32
    assert regh==regl, 'select field crossed reg boundary!'

    addr = '%02X%02X%04X' % (regh, fa, tileno)
    addr = int(addr,16)
    if DBG: print 'select address is %08X' % addr

    # mask = (1<< (1+configh-configl)) - 1
    mask = (1 << sw) - 1
    if DBG: print 'select mask is    0x%X' % mask
    assert sel < 2**sw, 'select exceeds mask size!'

    data = sel << (configl%32)
    if DBG: print 'select data is    %08X\n' % data

    regr = configr/32
    raddr = '%02X%02X%04X' % (regr, fa, tileno)
    raddr = int(raddr,16)
    if DBG: print 'reg address is %08X' % raddr

    rdata = 1 << (configr%32)
    if DBG: print 'reg data is    %08X\n' % data

    return (addr,data,raddr,rdata)


def gen_comment_conn(configh,configl,tileno,sel,src,snk):
    # Stupid comment
    # data[(21, 20)] : @ tile (2, 2) connect wire 2 (in_BUS16_S3_T0) to out_BUS16_S2_T0

    # data[(21, 20)]
    data = 'data[(%d, %d)]' % (configh,configl)

    # tile (2, 2)
    tile = 'tile (%d, %d)' % tileno2rc(tileno)

    # wire 2 (in_BUS16_S3_T0)
    w1 = 'wire %d (%s)' % (sel,src)

    # out_BUS16_S2_T0
    w2 = snk

    c = '%s : @ %s connect %s to %s' % (data,tile,w1,w2)
    # print c
    return c


def gen_comment_latch(configr,tileno,outwire):
    # Stupid comment
    # data[(14, 14)] : @ tile (4, 0) latch output wire out_BUS16_S1_T1

    # data[(21, 20)]
    data = 'data[(%d, %d)]' % (configr,configr)

    # tile (2, 2)
    tile = 'tile (%d, %d)' % tileno2rc(tileno)

    c = '%s : @ %s latch output wire %s' % (data,tile,outwire)
    # print c
    return c


def find_sources(tile, box, rsrc, DBG=0):
    '''
    Search all boxes of type 'box' to see what can source 'rsrc'
    'box' can be one of: ['sb','cb']
    '''
    DBG = max(DBG,0)
    assert box in ['sb','cb']
    rsrc = oneworld(rsrc)
    rlist = []

    for box in tile.iter(box):
        for mux in box.iter('mux'):
            for src in mux.iter('src'):

                # (Unnecessary) optimization
                if re.search('BUS1_', src.text): continue

                owsrc = oneworld(src.text)
                if DBG: print 'found src', src.text
                # if src.text == rsrc:
                if oneworld(src.text) == rsrc:
                    snk = mux.attrib['snk']
                    if DBG: print 'found snk', snk
                    rlist.append(oneworld(snk))
    return rlist

    DBG=1
    if DBG: print rsrc, 'can connect to', rlist
    print ''
     

def find_sinks(tile, box, rdst, DBG=0):
    '''
    Search all boxes of type 'box' to see what can sink 'rdst'
    'box' can be one of: ['sb','cb']
    '''
    DBG = max(DBG,0)
    assert box in ['sb','cb']
    rdst = oneworld(rdst)
    rlist = []

    for bb in tile.iter(box):
        for mux in bb.iter('mux'):
            # Look for sinks whose src is rdst
            # if mux.attrib['snk'] == rdst:
            # ow = oneworld(mux.attrib['snk'])
            owsnk = oneworld(mux.attrib['snk'])

            # (Unnecessary) optimization
            if re.search('BUS1_', owsnk): continue

            if owsnk == rdst:
                if DBG: print 'found snk', mux.attrib['snk']
                for src in mux.iter('src'):
                    if DBG: print 'found src', src.text
                    rlist.append(oneworld(src.text))
    return rlist

     
def get_tile(tileno):
    for tile in CGRA.findall('tile'):
        t = int(tile.attrib['tile_addr'])
        if t == tileno: return tile
    return -1

def oneworld(w, DBG=0):
    '''
    Sometimes e.g. 'in_0_BUS16_1_2' is called 'in_0_BUS16_S1_T2' and vice vera.
    UGH yes it is a bug.
    This func converts all names to the canonical '...S1_T2' form
    '''
    w2 = w # default

#     parse = re.search('^(in|out)_([01])_BUS16_S(\d+)_T(\d+)', w)
#     if parse:
#         if DBG: print '           # OH NO found ST wire name "%s"' % w
#         dir = parse.group(1)
#         tb  = parse.group(2)
#         side  = parse.group(3)
#         track = parse.group(4)
#         w2 = "%s_%s_BUS16_%s_%s" % (dir,tb,side,track)

    parse = re.search('^(in|out)_([01])_BUS16_(\d+)_(\d+)', w)
    if parse:
        if DBG: print '           # OH NO found non-ST wire name "%s"' % w
        dir = parse.group(1)
        tb  = parse.group(2)
        side  = parse.group(3)
        track = parse.group(4)
        w2 = "%s_%s_BUS16_S%s_T%s" % (dir,tb,side,track)

    return w2


def parse_resource(r):
    '''
    resource must be of the form "T0_in_s0t0" or "T3_mem_out"
    returns tileno+remains e.g. parse_resource("T0_in_s0t0") = (0, 'in_s0t0')
    '''
    parse = re.search('^T(\d+)_(.*)', r)
    if not parse: assert False, r
    (tileno,resource) = (int(parse.group(1)), parse.group(2))
    return (tileno,resource)


def parse_canon(w):
    '''wire MUST have embedded tileno e.g. "T0_in_s0t0"'''
    # Examples
    # "T0_in_s0t0" returns (0, 'in', 0, 0)
    # "T3_mem_out" returns (3, 'mem_out', -1, -1)
    (tileno,w) = parse_resource(w)

    parse = re.search('(in|out)_s(\d+)t(\d+)', w)
    if not parse: return (tileno,w,-1,-1)

    (dir,side,track) = (
        parse.group(1), parse.group(2), parse.group(3))
    return (int(tileno),dir,int(side),int(track))


def test_canon2global():
    vectors = [
        [ 'T0_out_s0t0', 'wire_0_0_BUS16_S0_T0'],
        [ 'T0_in_s3t3', 'wire_m1_0_BUS16_S1_T3'],
        [ 'T0_in_s1t0',  'wire_1_0_BUS16_S3_T0'],

        # T10 is pe at 1,2; 1,3 is lower-half mem
        ['T10_in_s0t5',  'wire_1_3_BUS16_S2_T5'],

        [ 'T3_in_s2t5',  'wire_0_2_BUS16_S0_T5'],
        [ 'T3_in_s6t5',  'wire_1_2_BUS16_S0_T5'],
        ]

    for v in vectors:
        print 'Want:', v[0],v[1]
        c2g = canon2global(v[0])
        print 'Got: ', v[0], c2g, '\n'
        assert c2g == v[1], 'c2g(%s) != %s' % (v[0],v[1])
    return


def canon2global(name, DBG=0):
    '''
    Converts canonical wirename to global wirename, e.g.
    T0_out_s0t0 =>  wire_0_0_BUS16_S0_T0
    T0_in_s3t0  => wire_m1_0_BUS16_S0_T0
    T0_in_s1t0 =>   wire_1_0_BUS16_S3_T0
    '''
    (tileno,dir,side,track) = parse_canon(name)
    (r,c) = tileno2rc(tileno)

    if dir=='out':
        if side>=4: r = r+1 # Right? RIGHT??
        gname = 'wire_%d_%d_BUS16_S%d_T%d' % (r,c,side,track)
    else:
        assert dir=='in'

        if   side%4==0: c = c + 1 # Coming in from the right
        elif side%4==1: r = r + 1 # Coming in from the bottom
        elif side%4==2: c = c - 1 # Coming in from the left
        elif side%4==3: r = r - 1 # Coming in from the top

        if side>=4: r = r+1 # Right? RIGHT??
        
        # side  adj    side adj
        #  0     2      4    2
        #  1     3      5    3
        #  2     0      6    0
        #  3     1      7    1
        adj_side = (side+2)%4 # print side,adj_side

        # Take care of the case where outwrie goes into bottom of a mem tile
        if (r>0) and (c>0) and (r%2==1):
            adj_tile = rc2tileno(r,c) # print adj_tile, type(adj_tile)
            # if is_mem(adj_tile): adj_side = adj_side+4 # No, never!

        if c<0: c = 'm1'
        if r<0: r = 'm1'

        gname = 'wire_%s_%s_BUS16_S%d_T%d' % (str(r),str(c),adj_side,track)
    return gname

    # INPUT  tile  2 (0,2) / out_BUS16_S1_T0 / wire_0_2_BUS16_S1_T0
    # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
    # INPUT  tile  0 (0,0) / out_BUS16_S1_T4 / wire_0_0_BUS16_S1_T4
    # OUTPUT tile  0 (0,0) / in_BUS16_S1_T1 / wire_1_0_BUS16_S3_T1
    # OUTPUT tile 15 (2,1) / in_BUS16_S2_T4 / wire_2_0_BUS16_S0_T4
    # OUTPUT tile 15 (2,1) / in_BUS16_S2_T4 / wire_2_0_BUS16_S0_T4

def canon2cgra(name, DBG=0):
    '''
    Converts canonical wirename to cgra wirename, e.g.
    in_s1t2    => in_BUS16_S1_T2
    T0_in_s1t2 => in_BUS16_S1_T2
    in_s5t2    => in_2_BUS16_S1_T2
    T3_in_s1t2 => sb_wire_in_1_S3_T2  (if T3 is a mem tile)
    T3_out_s7t2=> sb_wire_out_1_S3_T2 (if T3 is a mem tile)
    '''
    if DBG>1: print "converting", name

    # E.g. 'T0_in_s1t2' => 'in_BUS16_S1_T2'
    (T,d,side,t) = parse_canon(name)
    # assert T != -1
    if DBG>1: print (T,d,s,t)
    if side == -1:
        # not a wire; name is returned as 'd'
        if d == 'op1'   :  newname = 'data0'
        if d == 'op2'   :  newname = 'data1'
        if d == 'pe_out':  newname = 'pe_out_res'

        if d == 'mem_in':  newname = 'wdata'
        if d == 'mem_out': newname = 'rdata'

    else:
        dnot = 'out';
        if d == 'out': dnot = 'in'

        # if not is_mem_tile(T):
        if mem_or_pe(T) != 'mem':
            newname = '%s_BUS16_S%d_T%d' % (d,side,t)

        else:
            # must know if top or bottom
            tb = 'top';
            if side>3: tb='bottom'
            if   (tb == 'top')    and (side == '1'):
                newname = 'sb_wire_%s_1_BUS16_S3_T%d' % (dnot,t)
            elif (tb == 'bottom') and (side == '7'):
                newname = 'sb_wire_%s_1_BUS16_S3_T%d' % (d,t)
            else:
                # newname = '%s_%d_BUS16_S%d_T%d' % (d,s/4,s%4,t)
                # yes; sometimes; maybe; but better is:
                newname = '%s_%d_BUS16_S%d_T%d' % (d,side/4,side%4,t)

    if DBG: print "to_cgra: cgra name for '%s' is '%s'" % (name, newname)
    if DBG: print ''

    assert newname == oneworld(newname)
    return newname

            # sample memtile wire names:
            # {in,out}_0_BUS16_[023]_[0-4]
            # {in,out}_1_BUS16_[012]_[0-4]
            # 
            # {in,out}_0_BUS16_S2_T[0-4] (whoops!!)
            # 
            # sb_wire_{in,out}_1_BUS16_3_[0-4]
            # 
            # sb_wire_in_1_BUS16_3_[0-4]
            # > wire going from top to bottom (into side 3 (N) wrt bottom (1))
            # > maps to out/side3 if row even (top)
            # > or      in/ side1 if row odd (bottom)
            # sb_wire_out_1_BUS16_3_[0-4]
            # > wire going from bottom to top (out of side 3 (N) wrt bottom (1))
            # > maps to in/ side3 if row even (top)
            # > or      out/side1 if row odd (bottom)

            #         if is_mem_tile(T):
            #             newname = '%s_%d_BUS16_S%d_T%d' % (d,s/4,s%4,t)



# FIXME split into multiple funcs maybe
# - fix it to read also in_0_... DONE
def parse_cgra_wirename(w, DBG=0):
    (dir,tb,side,track) = (-1,-1,-1,-1)
    # rval = (-1,-1,-1)

    assert not re.search('_BUS1_', w),\
           'Oops cannot handle single-bit wires (yet)'
        
    # Look for most common case first, howbowda
    parse = re.search('(in|out)_BUS16_S(\d+)_T(\d+)', w)
    if (parse):
        print 'parsed'
        (dir,side,track) = (parse.group(1), int(parse.group(2)), int(parse.group(3)))
        rval = (dir,tb,side,track)
        if DBG: print rval
        return rval

    # Crazy memtile wire non-ST
    parse = re.search('^(in|out)_([01])_BUS16_(\d+)_(\d+)', w)
    if parse:
        if DBG: print '           # OH NO found non-ST wire name "%s"' % w
        dir = parse.group(1)
        tb  = parse.group(2)
        side  = int(parse.group(3))
        track = int(parse.group(4))
        # w2 = "%s_%s_BUS16_S%s_T%s" % (dir,tb,side,track)
        if tb=='0': tb = 'top'
        else:
            tb = 'bottom'
            side = side + 4
        rval = (dir,tb,side,track)
        if DBG: print rval
        return rval

    # Crazy memtile wire sb_wire
    parse = re.search('sb_wire_(in|out)_1_BUS16_(\d+)_(\d+)', w)
    if parse:
        if DBG: print '           # OH NO found stupid sb_wire "%s"' % w
        dir = parse.group(1)
        tb  = 'bottom'
        side  = int(parse.group(2))+4
        track = int(parse.group(3))
        # w2 = "%s_%s_BUS16_S%s_T%s" % (dir,tb,side,track)
        # if tb=='0': tb = 'top'
        # else      : tb = 'bottom'
        rval = (dir,tb,side,track)
        if DBG: print rval
        return rval


    # Crazy memtile wire ST
    parse = re.search('^(in|out)_([01])_BUS16_S(\d+)_T(\d+)', w)
    if parse:
        if DBG: print '           # OH NO found ST wire name "%s"' % w
        dir = parse.group(1)
        tb  = parse.group(2)
        side  = int(parse.group(3))
        track = int(parse.group(4))
        # w2 = "%s_%s_BUS16_%s_%s" % (dir,tb,side,track)
        if tb=='0': tb = 'top'
        else:
            tb = 'bottom'
            side = side + 4
        rval = (dir,tb,side,track)
        if DBG: print rval
        return rval

    # Not a wire; maybe it's e.g. 'data1'
    # print 'out', rval
    rval = (-1,-1,-1,-1)
    if DBG: print rval
    return rval

def cgra2canon(name, tileno=-1, DBG=0):
    '''
    Converts cgra wirename to canonical wirename, e.g.
    in_BUS16_S1_T2 =>     in_s1t2     (if tileno = -1)
    in_BUS16_S1_T2 =>     T12_in_s1t2 (if tileno = 12)
    in_2_BUS16_S1_T2 =>   in_s5t2   
    sb_wire_in_1_S3_T2 => in_s1t2
    sb_wire_out_1_S3_T2=> out_s7t2
    '''
    if DBG: print "converting", name
    (dir,tb,side,track) = parse_cgra_wirename(name)
    if DBG: print (dir,tb,side,track)

    if dir == -1:
        # not a wire
        if   name == 'data0': newname = 'op1'
        elif name == 'data1': newname = 'op2'
        elif name == 'wdata': newname = 'mem_in'
        elif name == 'rdata': newname = 'mem_out'
        elif name == 'pe_out_res': newname = 'pe_out'
        else:
            print 'cannot decode "%s"' % name
            assert False, 'sb_wire or something?'
    else:
        # uh...parse_wirename should do this?
        # if tb=='bottom': side = side + 4
        assert side < 8
        newname = '%s_s%st%s' % (dir,side,track)

    if tileno != -1:
        newname = 'T%d_%s' % (tileno, newname)

    if DBG: print 'from_cgra: new name is', newname
    if DBG: print ''
    return newname


def connect_within_tile(tileno, src, snk, DBG):
    '''
    Given two wires (src,snk) e.g.
      in_0_BUS16_S3_T0,wdata
      in_BUS16_S0_T0,  data0
      in_BUS16_S2_T0,  out_BUS16_S1_T0
      pe_out_res,      out_BUS16_S3_T1
      rdata,           out_0_BUS16_S0_T0
    return True or False according to whether src can connect to snk
    also, return the bit pattern for connecting them.
    '''


    # BOOKMARK
    # Return (addr,data,regaddr,regdata)
    # (addr,data) for the connection
    # (regaddr,regdata) for registering the sink (if applicable)

    # FIXME DO WE STILL NEED SEARCH_MUXES()??
    # #     port = oneworld(port)
    # #     rlist = search_muxes(fan_dir, tile, port, DBG-1)

    tile = get_tile(tileno)
    assert tile != -1, '404 tile not found'

    src_cgra = canon2cgra(src)
    snk_cgra = canon2cgra(snk)

    # FIXME maybe canon2cgra(0 should be done in find_mux()...
    parms = find_mux(tile, src_cgra, snk_cgra, DBG)

    if parms == False: return False
    else:
        ep = encode_parms(parms, DBG)

        # Stupid comment
        # data[(21, 20)] : @ tile (2, 2) connect wire 2 (in_BUS16_S3_T0) to out_BUS16_S2_T0
        c = gen_comment_conn(
            parms['configh'],
            parms['configl'],
            tileno,
            parms['sel'],
            canon2cgra(src),
            canon2cgra(snk))

        # Stupid comment
        # data[(14, 14)] : @ tile (4, 0) latch output wire out_BUS16_S1_T1
        cr = gen_comment_latch(
            parms['configr'],
            tileno,
            canon2cgra(snk))

        return ep + (c,cr)


#     ################################################################
#     # FIXME this needs cleaning terribly
#     # (aprime,bprime) = (to_cgra(a),to_cgra(b))
#     (a,b) = (src,snk)
#     (aprime,bprime) = (canon2cgra(a),canon2cgra(b))
# 
#     # print "       Can '%s' connect to '%s'?" % (aprime,bprime)
# 
#     # rlist = all ports that a can reach in tile T
#     # FO = cgra_info.fan_out(to_cgra(a), T, DBG-1)
#     FO = fan_out(aprime, tileno, DBG-1)
#     rlist = FO
# 
#     print "         %s can connect to %s" % (aprime,rlist)
# 
#     # bprime = to_cgra(b)
#     # bprime = canon2cgra(b)
# 
#     print "         Is '%s' in the list?" % bprime
#     if bprime in rlist: return True
#     else              : return False



# def mem_alias(w, DBG=0):
#     '''
#     Sometimes e.g. 'in_0_BUS16_1_2' is called 'in_0_BUS16_S1_T2' and
#     vice versa UGH yes it's a bug.
#     '''
#     # FIXME Here's a painful hack
#     # Someimtes memtile wires look like this:
#     # {in,out}_0_BUS16_S2_T[0-4] (whoops!!)
#     # when they're supposed to look like this:
#     #             # {in,out}_0_BUS16_[023]_[0-4]



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


