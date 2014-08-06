#control the BIG SKY ablation laser
import time
import os
import numpy as np
import visa

#Get the list of instrumetns connected to the computer.
insts= visa.get_instruments_list()

print "Instruments found:", (insts)
#User chooses which instrument to use. Should be 0.
person = int(raw_input('Which instrument? Type number...'  ))
insts=str(insts[person]).strip('[]')
print insts
#Define scope as the instrument the user chose.
bigsky = visa.SerialInstrument("%s" % insts)
print bigsky.ask("$ECHO 0")

def fire():
	#fires the laser with the parameters set on front panel
	print (bigsky.ask("$FIRE 1")).strip("\n")
	
def prep():
	#turns on the laser with the parameters set on front panel. Q switch off
	print (bigsky.ask("$FIRE 1")).strip("\n")
	print (bigsky.ask("$QSWITCH 0")).strip("\n")

def fireqswitch():
	print (bigsky.ask("$QSWITCH 1")).strip("\n")

def stopqswitch():
	print (bigsky.ask("$QSWITCH 0")).strip("\n")
	
def stop():
	#stops the laser with the parameters set on front panel
	print (bigsky.ask("$STOP 0")).strip("\n")