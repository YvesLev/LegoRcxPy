""" Allow interaction with Lego RCX with Lego IR Tower, Serial Communication version """
__author__ = 'Yves Levesque'
__version__ = '2026.02.21.0' # : Added LastCmdSerStr() that prints the last byte string sent to serial port

import serial, time #, threading, queue
lastOpCode = 0
_ser = None # serial object for comms

class RCX:
    A, B, C = 0x01, 0x02, 0x04
    a, b, c = 0x01, 0x02, 0x04
    inp1, inp2, inp3 = 0, 1, 2
    
    TypeRaw = 0
    TypeTouch = 1
    TypeTemp = 2
    TypeLight = 3
    TypeRot = 4
    
    ModeRaw = 0x00
    ModeBool = 0x20
    ModeEdge = 0x40
    ModePulse = 0x60
    ModePct = 0x80
    ModeTempC = 0xA0
    ModeTempF = 0xC0
    ModeAngle = 0xE0
    
    SrcVar = 0
    SrcTmr = 1
    SrcImm = 2
    SrcMot = 3
    SrcRdm = 4
    SrcPrg = 8
    SrcSv = 9
    SrcSt = 10
    SrcSm = 11
    SrcSr = 12
    SrcSb = 13
    SrcClk = 14
    SrcMsg = 15
    
    opCodeEx = (0xf7, -1)
    LastCmdSerStr=""
    
    def __init__(self, comPort):
        
        global _ser
        
        self.outMot = {}
        self.sensors = {}
        
        """ Initialize communications to RCX.
        comPort -- COM port number or name (like 'COM1' or '/dev/ttyUSB0')
        """
        
        try:
            _ser = serial.Serial(comPort, 2400,bytesize = serial.EIGHTBITS, parity = serial.PARITY_ODD, stopbits = serial.STOPBITS_ONE, timeout = 2)

            if _ser != None:
                _ser.reset_input_buffer()
                r = self.rcxCmd(b'\x10')
                
                if r == None :
                    print("Please, power on the RCX")
#                    self.close()
                    
        except serial.SerialException:
            print("Could not open port " + repr(comPort))
            _ser = None
        
        
        
    def close(self):
        print("Shutting down.")
        
        if _ser != None:
            _ser.close()


    def mkSerBuffWr(self, cmd):
        global lastOpCode
        if len(cmd)==0 : cmd = b'\x10'
        opCode = cmd[0]
        if 'lastOpCode' not in globals(): lastOpCode = 0
        if (opCode == lastOpCode) and (opCode not in self.opCodeEx):
            if (opCode & 0x08) == 0 :
                opCode |= 0x08
            else :
                opCode &= ~0x08
            cmd = bytearray(cmd)
            cmd[0] = opCode
            cmd = bytes(cmd)
        lastOpCode = opCode
        buff = b''
        sum = 0
        for b in cmd:
            buff += b.to_bytes(1, 'big')
            buff += (0xff - b).to_bytes(1, 'big')
            sum += b
        buff += (sum & 0xff).to_bytes(1, 'big')
        buff += ((-1-sum) & 0xff).to_bytes(1, 'big')
        buff = b'\x55\xff\x00' + buff
        return buff

    def rcxCmd(self, cmd, vblen=0): # cmd = bytes , vblen = returned value(s) byte length.  0 (default) if no returned values expected.
        global _ser, LastCmdSerStr
        buff= self.mkSerBuffWr(cmd)
        LastCmdSerStr = "b'" + (''.join(f'\\x{b:02x}' for b in buff)) + "'"
        s=b'\x55\xff\x00' + buff[4].to_bytes(1,"big") + buff[3].to_bytes(1,"big")
#        print(buff.hex(),LastCmdSerStr)
        r=b''
        f=-1
        t0=time.time()            
        _ser.reset_input_buffer()
        _ser.write(buff)
        while f == -1 and time.time() < (t0 + 1):
            r += _ser.read(_ser.in_waiting)
            f=r.find(s)
        if f == -1 :
            v = None # Returns None if no reply code found in the reply
#            print(r.hex())
        else:
            if vblen > 0 :
                nbsupp = len(s) + 2 * vblen
                while len(r)<(f+nbsupp):
                    r += _ser.read(_ser.in_waiting)
                v=b''
                for x in range(vblen):
                    v += r[f + len(s) + x * 2].to_bytes(1,"big")
            else:
                v = b'\x00'  # Default returned when reply code found and no Values expected.
                
        ts= (t0 + 0.1) - time.time()
        if ts > 0 : time.sleep(ts)
        
        return v # Return None if reply NOT OK, b'\x00' if reply OK , returns bytes representing the value expected (Needs to be decoded) ex. if value is 255, will return b'\xFF\x00'

    def LastCmdSerStr(self):
        global LastCmdSerStr
        print(LastCmdSerStr)
        
    def alive(self):
        cmd=b'\x10'
        r = self.rcxCmd(cmd)
        if r == None :
            return False
        else:
            return True

    def pwroff(self):
        cmd = b'\x60'
        self.rcxCmd(cmd)
            
    def snd(self, soundtype):
        cmd = b'\x51' + soundtype.to_bytes(1,"big")
        self.rcxCmd(cmd)
        
    def prg(self, progno=1):
        if (progno < 1) or (progno > 5):
            progno = 0
        else:
            progno = progno -1
        cmd = b'\x91' + progno.to_bytes(1,"big")
        self.rcxCmd(cmd)
    
    def start(self, taskno=0):
        if (taskno < 0) or (taskno > 9):
            taskno = 0
        cmd = b'\x71' + taskno.to_bytes(1,"big")
        self.rcxCmd(cmd)

    def stop(self, taskno=-1):
        if (taskno < 0) or (taskno > 9):
            cmd = b'\x50'
        else:
            cmd = b'\x81' + taskno.to_bytes(1,"big")
        self.rcxCmd(cmd)

    def msg(self, msgb):
        msgb = msgb & 0xff
        cmd = b'\xf7' + msgb.to_bytes(1,"big")
        self.rcxCmd(cmd)
        
    def getval(self, source, argum = 0):
        cmd = b'\x12' + source.to_bytes(1,"big") + argum.to_bytes(1,"big")
        vb = self.rcxCmd(cmd,2)
        if vb==None : return None
        v=(vb[1]<<8)+vb[0]
        if v >= (256*256)//2:
            v = v - (256*256)
        return v

    def mot(self, motors):
        if motors not in self.outMot:
            self.outMot[motors] = OutMot(motors)
        return self.outMot[motors]

    def sensor(self, input):
        if input not in self.sensors:
            self.sensors[input] = Sensors(input)
        return self.sensors[input]
    
class OutMot(RCX):
    def __init__(self, motors):
        self.motors = motors
    def on(self):
        cmd = b'\x21' + (0x80 | self.motors).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def off(self):
        cmd = b'\x21' + (0x40 | self.motors).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def float(self):
        cmd = b'\x21' + (0x00 | self.motors).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def flip(self):
        cmd = b'\xe1' + (0x40 | self.motors).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def f(self):
        cmd = b'\xe1' + (0x80 | self.motors).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def r(self):
        cmd = b'\xe1' + (0x00 | self.motors).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def pow(self, power):
        self.power = power & 7
        cmd = b'\x13' + (self.motors).to_bytes(1,"big") + b'\x02' + (self.power).to_bytes(1,"big")
        self.rcxCmd(cmd)

class Sensors(RCX):
    def __init__(self, input):
        if input < 0 or input > 2:
            self.input = 0
        else:
            self.input = input
    def type(self, typeno):
        if typeno >= 0 and typeno <= 4:
            self.typeno = typeno
        else:
            self.typeno = 0
        cmd = b'\x32' + (self.input).to_bytes(1,"big") + (self.typeno).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def mode(self, code):
        self.code = code
        cmd = b'\x42' + (self.input).to_bytes(1,"big") + (self.code).to_bytes(1,"big")
        self.rcxCmd(cmd)
    def clear(self):
        cmd = b'\xd1' + (self.input).to_bytes(1,"big")
        self.rcxCmd(cmd)
        