import numpy as np
import matplotlib.pyplot as plt
import scipy.constants
import math

pi=math.pi
hbar=scipy.constants.hbar
lbda = 589*10**(-9)
k = 2*pi/lbda
Gamma = 2*pi*9.8*10**6
m = 23*(scipy.constants.value('atomic mass constant'))
s = 1
d0 = -Gamma
A = .001
gu=1
mu=gu*(scipy.constants.value('Bohr magneton'))
beta= -8*s*hbar*(k**2)*d0/(m*Gamma*(1+s+4*(d0**2)/(Gamma**2))**2)
omega2 = -16*k*s*A*mu*d0/(m*Gamma*(1+s+4*(d0**2)/(Gamma**2))**2)

t=0.01 #Timestep
def test(time=0.01):
	#Initialize position and velocity
	t=time
	z = 3*10**(-3)
	vz = 0
	az = -beta*vz-omega2*z
	alist = [az]
	vzlist = [vz]
	zlist = [z]
	i=0
	while (i <200):
		z1=z+0.5*az*t**2 + vz*t
		vz1=vz+az*t
		#print (z,vz,az)
		z=z1
		vz=vz1
		az = -beta*vz-omega2*z
		alist.append(az)
		zlist.append(z)
		vzlist.append(vz)
		i = i+1
	plt.plot(zlist,vzlist,'r',zlist,alist,'b')
	plt.show()
	#print alist
	
def mot(time=0.01):
	#Initialize position and velocity
	t=time
	z = 1*10**(-10)
	vz = 0
	az = -beta*vz-omega2*z
	alist = [az]
	zlist = [z]
	i=0
	while (i <20):
		z1=z+0.5*az*t**2 + vz*t
		vz1=vz+az*t
		print (z,vz,az)
		z=z1
		vz=vz1
		az = -beta*vz-omega2*z
		alist.append(az)
		zlist.append(z)
		i = i+1
	plt.plot(zlist,alist)
	plt.show()