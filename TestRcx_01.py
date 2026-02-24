import time
from legorcx import RCX
r=RCX("COM4")

if not r.alive() :
    print("Not detecting the RCX, please power up the brick!")
    exit()

r.snd(1)
r.snd(1)

v=r.getval(r.SrcSv,r.inp2)
print(v)
print("Entering the loop.  Press Touch sensor on Input 2 to exit")

while (not v) and (v!=None):
#    r.snd(1)
    v=r.getval(r.SrcSv,r.inp2)
if v == None:
    print("Check that RCX is ON!!")
else:
    print("Input 2 = ON")
    
r.close()
