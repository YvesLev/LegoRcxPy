# LegoRcxPy
LEGO RCX PYTHON SERIAL COMMUNICATION MODULE (USING IR TOWER WITH SERIAL DB9 Cable.  NOT FOR USB TOWER)


I got an RCX brick few days ago with its Serial IR Tower and I managed to find in this forum and google some information.
The following link seems to be the most complete to explain the serial protocol and list all opcodes etc...

https://www.mralligator.com/rcx/

Python module to interact with RCX using the serial link throuh its IT Tower:

- First, I think I read somewhere you cannot send IR commands with no firware in the RCX
So I loaded the firm0332.lgo into the RCX using Brickx CC.
The firmware can be found at: https://pbrick.info/index.html-p=74.html

- You can use the shell in Thonny IDE or any other shell like the one that comes with python to test this Python module.  I personally use Thonny.
- Copy the LegoRcx.py in your working folder (that you navigate to in the Files left pane of Thonny for ex).
- Then in the python shell, try the following:

```python
>>> from legorcx import RCX
>>> rcx=RCX("COM1")  # use the com port for you IR Tower.  For LINUX, make sure to set user permission for the port as reported by @Gunners TekZone on eurobricks.com. (ex.: ~$ sudo chmod o+rw /dev/ttyUSB0)
>>> rcx.snd(1) # should play BEEP BEEP
>>> rcx.mot(rcx.A).on()  # run motor on output A
>>> rcx.mot(rcx.A + rcx.B + rcx.C).on()  # run motors A, B, C
>>> rcx.mot(rxc.B + rcx.C).off()  # stop motors B and C (Brake)
>>> rcx.mot(rcx.A).float()  # coast to stop motor A
>>> rcx.mot(rcx.A).on()
>>> rcx.mot(rcx.A).r()  # Set reverse direction.
>>> rcx.mot(rcx.A).f()  # Set forward direction.
>>> rcx.mot(rcx.A).flip()  # flip direction.
>>> rcx.mot(rcx.A).pow(0)  # Set speed to minimum  pow(7) is the Maximum

>>> rcx.close()  # Shutdown serial communication and any threads gracefully.
>>> rcx.pwroff() # Powers off the RCX Brick completely

```

Other rcx commands:
rcx.alive() : returns True if it detects the RCX, False otherwise.
rcx.prg(5)  # Set program #5  (can use 1 to 5)
rcx.start(taskno) # where taskno can be 0 to 9.  Default is 0 if not specified like in rcx.start().  I think starting task 0 is the same as pressing run button on rcx brick.
rcx.stop(taskno)  # where taskno can be 0 to 9. if anything else is specified like stop(-1), it will stop all tasks.  This is the default (stop())
rcx.sensor(inputno).type(typeno) # input no = 0, 1, or 2 (Can rather use rcx.inp1, inp2, inp3).  type command is to configure the type of sensor  This define default mode as well.
    # typeno can be following constant
    # TypeRaw = 0
    # TypeTouch = 1
    # TypeTemp = 2
    # TypeLight = 3
    # TypeRot = 4
    Ex: >>> rcx.sensor(rcx.inp1).type(rcx.TypeLight) # configures input 1 as a Light sensor with mode percent

rcx.sensor(inputno).mode(Code) # input no = 1, 2, or 3.  mode command is to configure the value format of the input if you want it different that the type defaults to.
    # 	You can also add the slope value 0-31 (default 0)
    # 	Use the module constant to for the Code:
    #    ModeRaw = 0x00		Value in 0...1023.
    #    ModeBool = 0x20	Either 0 or 1. (default for Touch sensor type)
    #    ModeEdge = 0x40	Number of boolean transitions.
    #    ModePulse = 0x60	Number of boolean transitions divided by two. 
    #    ModePct = 0x80		Raw value scaled to 0..100. (default for Light sensor type)
    #    ModeTempC = 0xA0	1/10ths of a degree, -19.8..69.5. (default for Temperature sensor type)
    #    ModeTempF = 0xC0	1/10ths of a degree, -3.6..157.1.
    #    ModeAngle = 0xE0	1/16ths of a rotation, represented as a signed short.  (Default for Rotation sensor type)

    # 	 Ex.: >>> rcx.sensor(rcx.inp1).mode(rcx.ModeRaw) # configures input 1 for raw value. (Slope 0)
    # 	 Ex.: with slope >>> rcx.sensor(inp1).mode(rcx.ModeBool + 15) # configures input 1 for boolean value with slope of 15.

rcx.sensor(inputno).clear()  # Clear the counter associated with the specified sensor by setting it to a value of zero.

rcx.msg(msg)  # where msg is 0 to 255.  Avoid 0.  sets the IR message buffer with the given value.
    message are interesting because one IR tower might be used to make actions on different RCX...

    Simple NQC program to download into RCX (Prog 1) to demonstrate the msg command:
    task main()
    {
      ClearMessage();
      until(Message() == 11 );
      ClearMessage();
      OnFwd(OUT_A);
      until(Message() == 10 );
      ClearMessage();
      Off(OUT_A);
    }

    Then, in python shell:
    >>> from legorcx import RCX
    >>> r=RCX("COM1")
    >>> r.start()
    >>> r.msg(11) # Motor A with run forward
    >>> r.msg(10) # Motor A with stop and program will end.

rcx.getval(sourceno, argno) # Reads the value corresponding to the source.  Argument depends on the source and defaut is 0.
    # see documentation at https://www.mralligator.com/rcx/
    # value:
    #    SrcVar = 0		Return value of specified variable (argno = 0..31)
    #    SrcTmr = 1		Returns value of specified timer, in 1/100ths of a second.(argno = 0..3)
    #    SrcImm = 2		Returns specified immediate value. (NOT ALLOWED FOR getval command)
    #    SrcMot = 3		Returns state of specified motor. (argno = 0..2 for motor A, B, C) (Bit coded si documentation)
    #    SrcRdm = 4		Returns random value, 0..max. (NOT ALLOWED FOR getval command)
    #    SrcPrg = 8		Returns current program number. (argno = 0)
    #    SrcSv = 9		Returns value of specified sensor. (argno = 0..2)
    #    SrcSt = 10		Returns type of specified sensor. (argno = 0..2)
    #    SrcSm = 11		Returns mode of specified sensor. (argno = 0..2)
    #    SrcSr = 12		Returns raw value of specified sensor, 0..1023. (argno = 0..2)
    #    SrcSb = 13		Returns boolean value of specified sensor, 0..1. (argno = 0..2)
    #    SrcClk = 14	Returns minutes since power on. (argno = 0)
    #    SrcMsg = 15	Returns value of message buffer. (argno = 0)

    ex.: >>> v = rcx.getval(rcx.SrcSv,rcx.inp2) # v will contain the value of sensor at input #2
    ex.: >>> m = rcx.getval(rcx.SrcMsg) # m will conaint the value of the message in the buffer

EDIT: 2026-02-18
Added LastCmdSerStr function that prints the last serial command byte string.
Example:
```python
>>> from legorcx import RCX
>>> r=RCX("COM17")
>>> r.snd(2)
>>> r.LastCmdSerStr
b'\x55\xff\x00\x51\xae\x02\xfd\x53\xac'
>>> r.snd(2)
>>> r.LastCmdSerStr
b'\x55\xff\x00\x59\xa6\x02\xfd\x5b\xa4'

```

Still in development...

Please, report bugs, suggestion on the eurobricks forum:
https://www.eurobricks.com/forum/index.php?/forums/topic/200778-project-programs-to-allow-interactions-between-old-lego-control-interfaces-rcx-lego-interface-b-others/

