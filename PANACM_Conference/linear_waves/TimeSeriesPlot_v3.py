#from scipy import *
from pylab import *
import numpy 
import collections as cll
from tank import *
#from math import pi

# Read data
Datasource=1 #or 0:Paraview gauges 1:Gauge functions 2:Vof integration

NumberOfCases=1

NumberOfLines=[1985]

x_loc=[]
for i in range(0,int(L[0]/gauge_dx+1)): #+1 only if gauge_dx is an exact 
  x_loc.append(gauge_dx*i)

NumLocations=int(len(x_loc))
NumCol=3*NumLocations +1
y_loc=-0.5 #y=0 in the mean free surface

filename_PR=[]
filename_PR.append('combined_gauge_0_0.5_sample_all.txt')

filename_VOF=[]
filename_VOF.append('column_gauge.csv')

fig1 = figure()
fig1.add_subplot(1,1,1)
linetype=['k-', 'g-','b-','g-']
code=['Proteus'] 

n=NumberOfLines[0]
y_p_PR = zeros((int(n),int(NumLocations)),float)
y_p_PV = zeros((int(n),int(NumLocations)),float)
y_phi_PV = zeros((int(n),int(NumLocations)),float)
y_VOF = zeros((int(n),int(NumLocations)),float)
filename_PV=[]
for ss in range (0,int(NumLocations),10):
 close("all")
 fig1= figure()
 fig1.add_subplot(1,1,1)
 
 filename_PV.append('probe'+str(ss)+'.csv')  
 for j in range (0,int(NumberOfCases)):

   
  #read data
  if Datasource==1:
   p_PR  = zeros(int(n),float)
   u_PR  = zeros(int(n),float)
   v_PR  = zeros(int(n),float)
   time_P = zeros(int(n),float)
   fid = open(filename_PR[j],'r')
   fid.seek(0)
   headerline = 1
   D = fid.readlines()
   header = D[:headerline]
   n=len(D)
   print n
   b1 = numpy.array(zeros((int(n-1.0),int(NumCol))))
   for i in range (1,int(n)):
    b1[i-1,:]=D[i].split(',')
   b1 = numpy.array(b1,dtype=float32)
   print ss
   p_PR[:]=b1[:,int(2*NumLocations+1+ss)] 
   u_PR[:]=b1[:,int(1+ss)]
   v_PR[:]=b1[:,int(NumLocations+1+ss)]
   time_P[:]=b1[:,0]
   a=p_PR[:]  - mean(p_PR)
   print  mean(p_PR)
   y_p_PR[:,ss] = a[:]
   y_p_PR[:,ss] /=float(rho_0)*9.81*cosh(float(k)*(float(inflowHeightMean)+float(y_loc)))/cosh(float(k)*inflowHeightMean)
   plot(time_P[:],y_p_PR[:,ss],linetype[j],lw=1.0,label=code[j]) #,color = cs[j])

  elif Datasource==0:
   p_PV   = zeros(int(n),float)
   u_PV   = zeros(int(n),float)
   v_PV  = zeros(int(n),float)
   time_P = zeros(int(n),float)
   fid = open(filename_PV[ss],'r')
   fid.seek(0)
   headerline = 1
   D = fid.readlines()
   header = D[:headerline]
   n=len(D)
   print n
   b2 = numpy.array(zeros((int(n-1.0),19)))
   for i in range (1,int(n)):
    b2[i-1,:]=D[i].split(',')
   b2 = numpy.array(b2,dtype=float32)
   p_PV=b2[:,5]
   u_PV=b2[:,6]
   v_PV=b2[:,7]
   time_P = b2[:,15]
   meanp = mean(b2[:,5])
   y_p_PV[:,ss]=b2[:,5]-meanp
   y_p_PV[:,ss] /= float(rho_0)*9.81*cosh(float(k)*(float(inflowHeightMean)+float(y_loc)))/cosh(float(k)*inflowHeightMean) #based on linear theory
   y_phi_PV[:,ss]=-b2[:,9]+float(y_loc)
   y_phi_PV-=mean(y_phi_PV)
   plot(time_P[:],y_phi_PV[:,ss],linetype[j],lw=1.0,label='PV') #,color = cs[j])
  
  elif Datasource==2:
  
   time_P = zeros(int(n),float)
   fid = open(filename_VOF[j],'r')
   fid.seek(0)
   headerline = 1
   D = fid.readlines()
   header = D[:headerline]
   n=len(D)
   print n
   b3 = numpy.array(zeros((int(n-1.0),int(NumLocations+1))))
   for i in range (1,int(n)):
     b3[i-1,:]=D[i].split(',')
   b3 = numpy.array(b3,dtype=float32)
   y_VOF[:,ss]=b3[:,ss+1]
   y_VOF[:,ss]-=mean(y_VOF[:,ss])
   y_VOF[:,ss]=-y_VOF[:,ss]
   time_P = b3[:,0]
   plot(time_P[:],y_VOF[:,ss],linetype[j],lw=1.0,label='y_VOF') #,color = cs[j])



  n=n-1
  y_theor=zeros(int(n),float)
  u_theor=zeros(int(n),float)
  v_theor=zeros(int(n),float)
   
  loc=[x_loc[ss],y_loc]  
  kk = 0
  for ts in time_P:
    y_theor[kk]=float(waveheight)/2.0*cos(theta(loc,ts))  
    u_theor[kk]=float(sigma*amplitude*cosh(k*(z(loc)+h))*cos(theta(loc,ts))/sinh(k*h))
    v_theor[kk]=float(sigma*amplitude*sinh(k*(z(loc)+h))*sin(theta(loc,ts))/sinh(k*h))
    kk+=1
 
  y_theor-=mean(y_theor) 
  
    
  if j==0 :
   
   plot(time_P[:],y_theor[:],'r--',lw=1.0,label='Analytical')#,color = cs[j])
  legend(bbox_to_anchor=[0.99,0.99],ncol=2,fontsize=13)
 
  #xlim(0.0,4.0)
  ylim(-0.03,0.03)
  grid()
  title('x='+ str(x_loc[ss]) + ', y='+ str(y_loc) + '(m)',fontsize=16) 
  xticks(fontsize = 14) 
  yticks(fontsize = 14) 
  ylabel(r'$\eta (m)$',fontsize=16)
  xlabel(r'$time (s)$', fontsize=16)

  
 if Datasource==0:
  savefig('probe_PV' + str(ss) +'.png',dpi=100)
 elif Datasource==1:
  savefig('probe_G' + str(ss) +'.png',dpi=100)
 elif Datasource==2:
  savefig('probe_VOF' + str(ss) +'.png',dpi=100)
 #savefig('probe_graph_p.png',dpi=100)

#fig2 = figure()
#fig2.add_subplot(1,1,1)
#plot(time_PR,u_PR,"k-",lw=1.5,label='u_GF')
 
#plot(time_PR,v_PR,"k-",color = '0.3',lw=1.5,label='v_GF')
  
#legend(bbox_to_anchor=[0.99,0.99],ncol=2,fontsize=13)
#xlim(0.0,4.0)
#ylim(-0.03,0.06)
#grid()
#title('Free surface elevation at x='+ str(x_loc[j]) + ', y='+ str(y_loc) + '(m)',fontsize=16)
#xticks(fontsize = 14) 
#yticks(fontsize = 14) 
#ylabel(r"$velocity (m/s)$",fontsize=16)
#xlabel(r'$time (s)$', fontsize=16)
#  savefig('probe_graph_vel' + str(j) +'.png',dpi=100)
