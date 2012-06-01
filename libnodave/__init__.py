#!/usr/bin/env python
# -*- coding: utf-8 -*-
#libnodave.py

"""
    ein Wrapper für die c- Bibliothek libnodave
    
    TODO:
            Methode um Merkerbyte als Dict. abzurufen

"""
import ctypes
import os
import code
import readline
import atexit


    # copied constants from nodave.h
#Protocol types to be used with newInterface:
daveProtoMPI  = 0    # MPI for S7 300/400 
daveProtoMPI2 = 1    # MPI for S7 300/400, "Andrew's version" without STX 
daveProtoMPI3 = 2    # MPI for S7 300/400, Step 7 Version, not yet implemented 
daveProtoMPI4 = 3    # MPI for S7 300/400, "Andrew's version" with STX 

daveProtoPPI  = 10    # PPI for S7 200 
daveProtoAS511 = 20    # S5 programming port protocol 
daveProtoS7online = 50    # use s7onlinx.dll for transport 
daveProtoISOTCP = 122    # ISO over TCP */
daveProtoISOTCP243 = 123 # ISO over TCP with CP243 */
daveProtoISOTCPR = 124   # ISO over TCP with Routing */

daveProtoMPI_IBH = 223   # MPI with IBH NetLink MPI to ethernet gateway */
daveProtoPPI_IBH = 224   # PPI with IBH NetLink PPI to ethernet gateway */

daveProtoNLpro = 230     # MPI with NetLink Pro MPI to ethernet gateway */

daveProtoUserTransport = 255    # Libnodave will pass the PDUs of S7 Communication to user */
                                      # defined call back functions. */
                    
#ProfiBus speed constants:
daveSpeed9k = 0
daveSpeed19k = 1
daveSpeed187k = 2
daveSpeed500k = 3
daveSpeed1500k = 4
daveSpeed45k = 5
daveSpeed93k = 6

#    S7 specific constants:
daveBlockType_OB = '8'
daveBlockType_DB = 'A'
daveBlockType_SDB = 'B'
daveBlockType_FC = 'C'
daveBlockType_SFC = 'D'
daveBlockType_FB = 'E'
daveBlockType_SFB = 'F'

daveS5BlockType_DB = 0x01
daveS5BlockType_SB = 0x02
daveS5BlockType_PB = 0x04
daveS5BlockType_FX = 0x05
daveS5BlockType_FB = 0x08
daveS5BlockType_DX = 0x0C
daveS5BlockType_OB = 0x10


#Use these constants for parameter "area" in daveReadBytes and daveWriteBytes  
daveSysInfo = 0x3      # System info of 200 family 
daveSysFlags = 0x5    # System flags of 200 family 
daveAnaIn = 0x6       # analog inputs of 200 family 
daveAnaOut = 0x7      # analog outputs of 200 family 

daveP = 0x80           # direct peripheral access 
daveInputs = 0x81    
daveOutputs = 0x82    
daveFlags = 0x83
daveDB = 0x84          # data blocks 
daveDI = 0x85          # instance data blocks 
daveLocal = 0x86       # not tested 
daveV = 0x87           # don't know what it is 
daveCounter = 28       # S7 counters 
daveTimer = 29         # S7 timers 
daveCounter200 = 30    # IEC counters (200 family) 
daveTimer200 = 31      # IEC timers (200 family) 
daveSysDataS5 = 0x86   # system data area ? 
daveRawMemoryS5 = 0    # just the raw memory 


    #locate the acutal location so we will later find the 
    #libnodave-libs
APPDIR = os.path.dirname(os.path.abspath(__file__))

if os.name == 'nt':
    DLL_LOC = os.path.join(APPDIR, 'libnodave', 'win', 'libnodave.dll')
elif os.name == 'posix':
    DLL_LOC = 'libnodave.so'
else:
    print 'only win and linux supportet yet'


def int_to_bitarr(integer):
    """
        aus einem übergebenen Integer ein 8-stelliges Array erstellen in dem die einzelnen 
        Enthaltenen Bits aufzufinden sind
        im bitarr sind die Positionen im array gleich den Werten im Merkerbyte auf der SPS
        m0.0 ist 1. Bit im Merkerbyte (arr[0]
    """
    string = bin(integer)[2:]
    arr = list()
    
    for bit in xrange(8 - len(string)):
        arr.append(0)   
    
    for bit in string:
        arr.append(int(bit))    
    
    arr.reverse()
    return arr

def bitarr_to_int(bitarr):
    """
        eine liste die ein Byte repräsentiert in den passenden
        integer-Wert umrechnen
    """
    str_bitarr = list()
    bitarr.reverse()
    for elem in bitarr:
        str_bitarr.append(str(elem))
    print str_bitarr
    string = ''.join(str_bitarr)
    return int(string,2)


    #class to represent a c-struct
class _daveOSserialType(ctypes.Structure):
    _fields_ = [("rfd", ctypes.c_int),
                ("wfd", ctypes.c_int)]
    

class libnodave(object):
    def __init__(self):
            
        self. fds = _daveOSserialType()
        self.init_dll()
        
        self.buffer = ctypes.create_string_buffer('buffer')
        self.buffer_p = ctypes.pointer(self.buffer)
        
    def init_dll(self):
        """
            initiate the os depending dll-File
            set argtypes and resttypes for used functions
        """
        if os.name == 'nt':
            self.dave = ctypes.windll.LoadLibrary(DLL_LOC)
        else:
            self.dave =  ctypes.cdll.LoadLibrary(DLL_LOC)
    
        self.dave.setPort.restype =  ctypes.c_int
        self.dave.setPort.argtypes = [ctypes.c_char_p,
                                      ctypes.c_char_p,
                                      ctypes.c_char]
        
        self.dave.daveNewInterface.resttype = ctypes.c_void_p
        self.dave.daveNewInterface.argtypes = [_daveOSserialType,
                                               ctypes.c_char_p,
                                               ctypes.c_int,
                                               ctypes.c_int,
                                               ctypes.c_int]

        self.dave.openSocket.resttype = ctypes.c_int
        self.dave.openSocket.argtypes = [
                                               ctypes.c_int,
                                               ctypes.c_char_p,
                                        ]
                                        
        self.dave.daveSetDebug.resttype = ctypes.c_void_p
        self.dave.daveSetDebug.argtypes = [ ctypes.c_int ]

        
        
        self.dave.daveInitAdapter.resttype = ctypes.c_void_p
        self.dave.daveInitAdapter.argtypes = [ctypes.c_void_p]
        
        self.dave.daveNewConnection.resttype = ctypes.c_void_p
        self.dave.daveNewConnection.argtypes = [ctypes.c_void_p,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int]
        
        self.dave.daveStop.resttype = ctypes.c_int
        self.dave.daveStop.argtypes = [ctypes.c_void_p]
        
        self.dave.daveConnectPLC.resttype = ctypes.c_int
        self.dave.daveConnectPLC.argtypes = [ctypes.c_void_p]

        self.dave.daveSetTimeout.resttype = ctypes.c_void_p
        self.dave.daveSetTimeout.argtypes = [ctypes.c_void_p, 
                                             ctypes.c_int]
        
        self.dave.daveGetU8.resttype = ctypes.c_int
        self.dave.daveGetU8.argtypes = [ctypes.c_void_p]
        
        self.dave.daveDisconnectPLC.resttype = ctypes.c_int
        self.dave.daveDisconnectPLC.argtypes = [ctypes.c_void_p]
        
        self.dave.daveFree.resttype = None
        self.dave.daveFree.argtypes = [ctypes.c_void_p]
        
        self.dave.daveDisconnectAdapter.resttype = ctypes.c_int
        self.dave.daveDisconnectAdapter.argtypes = [ctypes.c_void_p]
        
        self.dave.daveReadBytes.resttype = ctypes.c_int
        self.dave.daveReadBytes.argtypes = [ctypes.c_void_p,
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.c_void_p]
        
        self.dave.daveGetCounterValue.resttype = ctypes.c_int
        self.dave.daveGetCounterValue.argtypes = [ctypes.c_void_p,
                                                  ctypes.c_int,
                                                  ctypes.c_int,
                                                  ctypes.c_int,
                                                  ctypes.c_int,
                                                  ctypes.c_void_p]
        
        self.dave.daveWriteBytes.resttype = ctypes.c_int
        self.dave.daveWriteBytes.argtypes = [ctypes.c_void_p,
                                             ctypes.c_int,
                                             ctypes.c_int,
                                             ctypes.c_int,
                                             ctypes.c_int,
                                             ctypes.c_void_p]
        
        
    def set_port(self, port, baud='9600', parity = 'E'):
        """
            set a serial connection port
        """
        self.fds.rfd = self.dave.setPort(port, baud, parity)
        self.fds.wfd = self.fds.rfd

    def open_socket(self, ip, port=102):

        self.fds.rfd = self.dave.openSocket(port, ip)
        self.fds.wfd = self.fds.rfd
        
    def new_interface(self, name, localMPI, protocol, speed):
        """
            EXPORTSPEC daveInterface * DECL2 daveNewInterface(_daveOSserialType nfd,
                            char * nname, int localMPI, int protocol, int speed);
        """
        self.di = self.dave.daveNewInterface(self.fds, name, localMPI, protocol, speed)
    
    def set_timeout(self, time):
        """
            set a new timeout
            EXPORTSPEC void DECL2 daveSetTimeout(daveInterface * di, int tmo);
        """
        self.dave.daveSetTimeout(self.di, time)
    
    def init_adapter(self):
        """
            initiate the configurated adapter
            EXPORTSPEC int DECL2 _daveInitAdapterNLpro(daveInterface * di);
        """
        self.dave.daveInitAdapter(self.di)
        
    def connect_plc(self, mpi, rack, slot):
        """
            connect to the plc
            daveConnection * DECL2 daveNewConnection(daveInterface * di, int MPI,int rack, int slot);
        """
        self.dc = self.dave.daveNewConnection(self.di, mpi, rack, slot)
        res = self.dave.daveConnectPLC(self.dc)

    def stop(self):
        """
            connect to the plc
            daveConnection * DECL2 daveNewConnection(daveInterface * di, int MPI,int rack, int slot);
        """
        res = self.dave.daveStop(self.dc)

    def SetDebug(self, level):
        """
            connect to the plc
            daveConnection * DECL2 daveNewConnection(daveInterface * di, int MPI,int rack, int slot);
        """
        res = self.dave.daveSetDebug(level)


    def disconnect(self):
        """
            disconnect connection to PLC and Adapter
        """
        self.dave.daveDisconnectPLC(self.dc)
        self.dave.daveFree(self.dc)
        self.dave.daveDisconnectAdapter(self.di)
        self.dave.daveFree(self.di)
        return True
        
    def read_bytes(self, area, db, start, len):
        """
            int daveReadBytes(daveConnection * dc, int area, int DB, int start, int len, void * buffer);
            set the pointer to specified memory in the plc
            returns True if pointer is set
        """
        res = self.dave.daveReadBytes(self.dc, area, db, start, len, self.buffer)
        if res == 0:
            return True
        return False
    
    def get_counter_value(self, counter_number):
        """
            read a counter from the plc
        """
        self.read_bytes(daveCounter, 0, 0, 1)  
        counters = list()
        for val in xrange(16):
            counters.append(self.dave.daveGetCounterValue(self.dc)) 
        return counters[counter_number]
    
    def get_counters(self):
        """
            Liste mit allen Zählern der S5 auslesen und zurückgeben
            TODO: wird das wirklich gebraucht?
        """
        if self.read_bytes(daveCounter, 0, 0, 1):  
            counters = list()
            for val in xrange(16):
                counters.append(self.dave.daveGetCounterValue(self.dc)) 
            return counters
        return False
    
    def get_marker_byte(self, marker):
        """
            einen merkerbyte auslesen 
            rückgabewert ist ein Integer. Sollen die einzelnen Bits untersucht werden
            muss der rückgabewert nach binär konvertiert werden -> bin(result)
        """
        if self.read_bytes(daveFlags, 0, marker, 1):
            return self.dave.daveGetU8(self.dc)
        return -1
        
    def get_output_byte(self, output):

        if self.read_bytes(daveOutputs, 0, output, 1):
            return self.dave.daveGetU8(self.dc)
        return -1
    
    def get_marker(self, marker, byte):
        """
            einen bestimmten Merker aus einem Merkerbyte auslesen
        """
        m_byte = self.get_marker_byte(marker)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False
        
    def get_output(self, output, byte):
        """
            einen bestimmten Merker aus einem Merkerbyte auslesen
        """
        m_byte = self.get_output_byte(output)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    
    def get_marker_byte_list(self, marker):
        """
            ein Merkerbyte als liste zurückgeben
            get a list with a bits representing all marker from read byte
        """   
        if self.read_bytes(daveFlags, 0, marker, 1):
            return int_to_bitarr(self.dave.daveGetU8(self.dc))
        return False
    
    def get_marker_byte_dict(self, marker):
        """
            ein Merkerbyte als Dict zurückgeben
        """
        _l = self.get_marker_byte_list(marker)
        print 'libnodave - merkerbyte:', _l
        d = dict()
        for val in xrange(8):
            d[val]=_l[val]
        return d
        
    def write_marker_byte(self, marker, value):
        """
            EXPORTSPEC int DECL2 daveWriteBytes(daveConnection * dc, int area, int DB, int start,
                                                int len, void * buffer);
            ein Merkerbyte in die SPS schreiben
            TODO: anpassen und testen
        """
        buffer = ctypes.c_byte(int(value))
        buffer_p =  ctypes.pointer(buffer)
        self.dave.daveWriteBytes(self.dc, daveFlags, 0, marker, 1, buffer_p)
        
    def write_vm_byte(self, vm, value):
        """
            EXPORTSPEC int DECL2 daveWriteBytes(daveConnection * dc, int area, int DB, int start,
                                                int len, void * buffer);
            ein Merkerbyte in die SPS schreiben
            TODO: anpassen und testen
        """
        buffer = ctypes.c_byte(int(value))
        buffer_p =  ctypes.pointer(buffer)
        self.dave.daveWriteBytes(self.dc, daveDB, 1, vm, 1, buffer_p)
        
    def outputs(self):
        Q1 = self.get_output(0,0)
        Q2 = self.get_output(0,1)
        Q3 = self.get_output(0,2)
        Q4 = self.get_output(0,3)

        print "Padverlichting      : " + str(Q1)
        print "Tuinhuisverlichting : " + str(Q2)
        print "Tuinhuis buiten     : " + str(Q3)
        print "Terrasverlichting   : " + str(Q4)
        

# Calling this class will launch an interactive console         
class HistoryConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>", histfile=os.path.expanduser("~/.console-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        try:
            import readline
        except ImportError:
            pass
        else:
            try:
                import rlcompleter
                readline.set_completer(rlcompleter.Completer(locals).complete)
            except ImportError:
                pass
            readline.parse_and_bind("tab: complete")
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)
