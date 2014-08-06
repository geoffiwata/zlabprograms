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
scope = visa.instrument("%s" % insts)

def scopeinfo():
    #Identifies the scope being used.
    print scope.ask("*IDN?")

def sendcommand(cmd):
	print cmd
	#Sends and receives an arbitrary command
	scope.write(cmd)
	print scope.read()

	
def checkerr()	:
	#check for errors and clear messages
	print scope.ask("*esr?")
	#check scope status
	print scope.ask("allev?")


def acq_one():
	#single sequence acquisition
	scope.write("acquire:stopafter sequence")
	scope.write("acquire:state on")
	controlcheck=True
	while controlcheck:
		s = scope.ask("Busy?")
		s=int(s[6])
		if s:
			controlcheck=False
		else:
			time.sleep(1)
	scope.ask("*opc?")
	print "Acquisition complete!"
	
def acravg():
	#single sequence acquisition
	scope.write("acquire:mode average")
	scope.write("acquire:numavg 16")
	scope.write("acquire:stopafter sequence")
	scope.write("acquire:state on")
	controlcheck=True
	while controlcheck:
		s = scope.ask("acquire:state?")
		s=int(s[15])
		if not s:
			controlcheck=False
		else:
			time.sleep(0.5)
	scope.ask("*opc?")
	print "Acquisition complete!"
	
def measuremin(outfile=None):
	tester = outfile
	#use built in scope functions to extract minimum and write to file
	scope.write("measu:immed:type min") #specify measurement to take
	minim = scope.ask("measu:immed:value?")
	minn = minim.split()
	minn =str(minn[1])
	print minn
	if outfile is not None:
		try:
			#write out the value to a file
			fout=open("%s_minimums.txt" % (tester),'a')
			fout.write('%s\n' % (minn))
			fout.close()
			print ("%s saved." % (minim))
		except:
			print("FILE OUTPUT FAILED, trying to continue")    
	#check for errors
	scope.ask("*esr?")
	print scope.ask("allev?")
	
def getwaveform(outfile=None):
	wavelength = raw_input('Enter Wavelength: ')
	saveq = raw_input('Save waveform?(y/n) ')
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
	print dcval
	absin = (np.argmin(curve[(idx+150):xlen])) #find absorption minimum
	abspmin = ymult*(curve[idx+150+absin]-yoff)
	print abspmin
	relabs = (dcval-abspmin)/dcval
	m=0
	yvals = []
	for item in curve:
		yvals.append(ymult*(item-yoff))
		m=m+1
	if outfile is not None:
		try:
			#write minimum the value to a file
			fout=open("%s.txt" % (outfile),'a')
			fout.write('%s\t%s \n' % (wavelength,relabs))
			fout.close()
			print ("minimum saved in %s.txt" % (outfile))
		except:
			print("FILE OUTPUT FAILED, trying to continue")
	if saveq is 'y':
		try:
			#write out the value to a file
			fout=open("%s.txt" % (wavelength),'a')
			n=1
			for item in xvalue:
				fout.write('%s\t%s \n' % (item,yvals[n]))
				n=n+1
			fout.close()
			print ("waveform saved.")
		except:
			print("FILE OUTPUT FAILED, trying to continue")