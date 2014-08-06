#Program to take BaH data
#Includes servo motor as shutter

#Upon running, there will be prompt to connect to the instruments. You must have the computer connected to tektronix tds 2024b oscilloscope and to the
#big sky laser. Then you must indicate which connections corresponds to what. Since the scope is usb and lasr is serial, should be pretty simple to 
#identify which is which. 

#There are some definitions that aren't used in the main program, but may be useful for later.
#The main program asks you what to save the filename as. I suggest doing it in the format: [BaH_yyyy-mm-dd_#nn]90?.?? where the last number is the
#header for the wavelength. All the wavelengths and relative absorption strengths will be saved there. 
#The output files are saved into the directory from which you ran python. Please copy these files to \\freedomfries in the appropriate folder.


#There are still some issues with the plotter crashing when you try and move it. this seems to be a bug with the code for plt.ion.
#^^Fixed using plt.pause(0.001). not sure why it needs a little break right before updating the plot.

#pyvisa documentation at http://pyvisa.readthedocs.org/en/1.5/
#tektronix programming manual at http://websrv.mece.ualberta.ca/electrowiki/images/c/c7/TDS2024B_Programmer_Manual.pdf
#BigSky manual in the lab.

import time
import os
import numpy as np
import visa
import matplotlib.pyplot as plt
from ctypes import *
import sys
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, CurrentChangeEventArgs, PositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes

"""All the phidget stuff..."""

try:
    advancedServo = AdvancedServo()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
	
def DisplayDeviceInfo():
	print "shutter attached"
def Attached(e):
    attached = e.device
    print("Servo %i Attached!" % (attached.getSerialNum()))

def Detached(e):
    detached = e.device
    print("Servo %i Detached!" % (detached.getSerialNum()))

def Error(e):
    try:
        source = e.device
        print("Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))

print("Opening phidget object....")

try:
    advancedServo.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)
	
advancedServo.waitForAttach(10000)
advancedServo.setServoType(0, ServoTypes.PHIDGET_SERVO_HITEC_HS322HD)
advancedServo.setAcceleration(0, advancedServo.getAccelerationMax(0))
advancedServo.setVelocityLimit(0, advancedServo.getVelocityMax(0))
advancedServo.setEngaged(0, True)
time.sleep(0.5)
advancedServo.setPosition(0, advancedServo.getPositionMin(0))
#servo in default position.

"""Now the rest of the stuff"""
#Get the list of instruments connected to the computer.
insts= visa.get_instruments_list()

print "Instruments found:", (insts)
#User chooses which instruments are which. list starts with 0.
scopenumber = int(raw_input('Which instrument is scope? Type number...'  ))
bigskynumber = int(raw_input('Which instrument is laser? Type number...'  ))
scopeid = str(insts[scopenumber]).strip('[]')
bigskyid = str(insts[bigskynumber]).strip('[]')
print ("Scope is %s. Laser is %s" % (scopeid,bigskyid))
#Define scope as the instrument the user chose.
bigsky = visa.SerialInstrument("%s" % bigskyid)
scope = visa.instrument("%s" % scopeid)
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
	
def acravg(numavg):
	#single sequence acquisition from scope
	#first defines the acquisition parameters
	scope.write("acquire:mode average") #mode
	scope.write("acquire:numavg %s" % (numavg)) #number of averages
	scope.write("acquire:stopafter sequence") #how many sequences
	scope.write("acquire:state on") #go
	#need a loop to poke the scope to see if it is done
	controlcheck=True
	while controlcheck:
		s = scope.ask("acquire:state?")
		s=int(s[15])
		if not s:
			controlcheck=False
		else: 
			continue
	scope.ask("*opc?") #do i need this??
	print "Acquisition complete!"
		
def getwaveform(wavelength, saveq, outfile=None):
	print "Getting waveform..."
	#wavelength = raw_input('Enter Wavelength: ')
	#saveq = raw_input('Save waveform?(y/n) ')
	#define data type
	scope.write("data.encdg ascii")
	rawcurve = scope.ask("curve?") #get waveform y values
	rawcurve = rawcurve.split()
	rawcurve = rawcurve[1] #extractes as csv string
	curve =  [float(x) for x in rawcurve.split(',')] #creates list
	datalength = len(curve)
	#xunit = scope.ask("wfmpre:xunit?")
	#get horizontal increment
	xincr = scope.ask("WFMPre:XINcr?")
	xincr = xincr.split()
	xincr = float(xincr[1])
	 #get first horizontal point
	xzero = scope.ask("wfmpre:xzero?")
	xzero = xzero.split()
	xzero = float(xzero[1])
	yoff = scope.ask("wfmpre:yoff?")
	yoff = yoff.split()
	yoff = float(yoff[1])
	ymult = scope.ask("wfmpre:ymult?")
	ymult = ymult.split()
	ymult = float(ymult[1])
	i=0
	#need list of x values
	xvalue = []
	while i < (datalength-1):	
		xvalue.append(xzero + i*xincr)
		i=i+1
	xlen = len(xvalue)
	idx = (np.abs(xvalue)).argmin() #find index closest to 0
	dcval = np.mean(curve[0:idx]) #take average of values before ablation pulse
	dcval = ymult*(dcval-yoff)
	#Yn = YZEro + YMUIty (yn - YOF)
	print ("dc value is %s" %(dcval))
	absin = (np.argmin(curve[(idx+250):xlen])) #find absorption minimum
	absmin = np.mean(curve[idx+240+absin:idx+260+absin])
	abspmin = ymult*(absmin-yoff)
	#print abspmin
	relabs = (dcval-abspmin)/dcval
	relabf = float(relabs)
	#print (type(relabs) is float)
	m=0
	yvals = []
	for item in curve:
		yvals.append(ymult*(item-yoff))
		m=m+1
	if outfile is not None:
		try:
			#write wavelength and rel absorption value to a file
			fout=open("%s.txt" % (outfile),'a')
			fout.write('%s\t%s \n' % (wavelength,relabs))
			fout.close()
			print ("minimum saved in %s.txt" % (outfile))
		except:
			print("FILE OUTPUT FAILED, trying to continue")
	if saveq is 'y':
		try:
			#write out the waveform to a file
			fout=open("%s.txt" % (wavelength),'a')
			n=1
			for item in xvalue:
				fout.write('%s\t%s \n' % (item,yvals[n]))
				n=n+1
			fout.close()
			print ("waveform saved.")
		except:
			print("FILE OUTPUT FAILED, trying to continue")
	print relabf
	return relabf
			
def update_line(pldata, x_data, y_data):
	pldata.set_xdata(np.append(pldata.get_xdata(), x_data))
	pldata.set_ydata(np.append(pldata.get_ydata(), y_data))
	#ax.relim()
	#ax.autoscale_view()
	plt.draw()
	print pldata
			
			########MAIN######

date = raw_input("Enter filename (no '.txt'): ")
savq = raw_input('Save waveforms?(y/n) ')
numb = raw_input('How many averages? ')
showplot = raw_input('show plot(y/n)? ')
print ("data file will be saved as %s.txt" % (date))
raw_input("Put on safety goggles. Hit Enter to begin taking data: ")
prep()
print "FLASHLAMP ON"
datacontrol = True
#plot setup
x=list()
y=list()
plt.ion()
plt.show()
shutterstate = False
	
while datacontrol:
	if shutterstate:
		advancedServo.setPosition(0, 15)
		time.sleep(0.5)
		print("Pump beam blocked!")
	else:
		advancedServo.setPosition(0, advancedServo.getPositionMin(0))
		time.sleep(0.5)
		print("Pump beam clear!")
	wavel = raw_input('Enter Wavelength: ')
	#savq = raw_input('Save waveform?(y/n) ')
	fireqswitch()
#	time.sleep(0.5)
	acravg(numb)
	stopqswitch()
	ydat = getwaveform(wavel, savq, date)
	print ydat
	if showplot is 'y':
		try:
			x.append(float(wavel))
			y.append(ydat)
			plt.scatter(float(wavel),ydat)
			#time.sleep(0.0001)
			plt.pause(0.001)
			plt.draw()
			#time.sleep(0.0001)
			#update_line(pldata, float(wavel), ydat)
			#plt.show()
		except:
			print ("PLOT UPDATE FAILED")
	q = raw_input("Type 'quit' to quit. 'newfile' for new file. 'pause' to pause laser. 's' for keep shutter state. Return for next. ")
	if 'quit' in q:
		stop()
		datacontrol=False
	if 'newfile' in q:
		stop()
		date = raw_input("Enter filename(no '.txt'): ")
		numb = raw_input('How many averages? ')
		print ("data file will be saved as %s.txt" % (date))
		raw_input("Put on safety goggles. Hit Enter to begin taking data: ")
		prep()
	if 'pause' in q:
		stop()
		raw_input("Hit Enter to resume measurements. ")
		prep()
	if 's' in q:
		continue
	elif not shutterstate:
			shutterstate = True
	else:
				shutterstate=False