from numpy import *
from scipy import *
from pylab import *
import collections as cll
import csv

# Put relative path below
filename='pointGauge_levelset.csv'

# Reading file
with open (filename, 'rb') as csvfile:
    data=csv.reader(csvfile, delimiter=",")
    a=[]
    time=[]
    probes=[]
    nRows=0

    for row in data:
# Time steps
        if nRows!=0:
            time.append(float(row[0]))

# Probes location ######################
        if nRows==0:                   #
            for i in row:              #
                if i!= '      time':   #
                    i=float(i[14:24])  #
                    probes.append(i)   #
########################################

        row2=[]
        for j in row:
            if j!= '      time' and nRows>0.:
                j=float(j)
                row2.append(j)
        a.append(row2)
        nRows+=1

#####################################################################################
   
# Choose which probes to plot  
    print('Number of probes : '+ str(len(probes)))
    x = int(raw_input('Enter which probes to plot (range from 1 to number of probes: ')) 
    phi=[]
    for k in range(1,nRows):
        phi.append(a[k][x]+0.05)    
# Plot phi in time
    import matplotlib.pyplot as plt
    plt.plot(time,phi)
    plt.xlabel('time [sec]')    
    plt.ylabel('phi [m]')
    plt.suptitle('Position of the interface at the left boundary plotted against time')
    plt.xlim((0,2.5))
    plt.ylim((0.04,0.06))
    plt.grid(True)
    plt.show()
    savefig('phi_in_time.png')

#####################################################################################

# Print an output file
    info = open('probes.txt','w')
    string1=str(probes)
    string2=string1.replace('[',' ')
    string3=string2.replace(']',' ')   
    string4=string3.replace(',','\t') 
    info.write(str('x')+'\t'+string4+'\n')
    for j in range(1,nRows):
        string5=str(a[j])
        string6=string5.replace('[',' ')
        string7=string6.replace(']',' ')   
        string8=string7.replace(',','\t')   
        info.write(string8+'\n')
    info.close()




