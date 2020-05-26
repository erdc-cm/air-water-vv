#!/usr/bin/env python
import os
#os.chdir('/home/travis/build/erdc/proteus/air-water-vv/2d/benchmarks/quiescent_water_probe_benchmark')
import pytest
from proteus.iproteus import *
from proteus import Comm
comm = Comm.get()
#import quiescent_water_test_gauges_so
#import quiescent_water_test_gauges as qw
import numpy as np
import collections as cll
import csv
from proteus.test_utils import TestTools
import subprocess

from proteus.defaults import (load_physics as load_p,
                              load_numerics as load_n,
                              load_system as load_so)

modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../2d/benchmarks/wavesloshing')
petsc_options = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../inputTemplates/petsc.options.asm")


class NumericResults:

    @staticmethod
    def _read_log(file_name):
        log_file = open(file_name,'r')
        return log_file

    @classmethod
    def create_log(cls,file_name):
        quiescent_log = cls._read_log(file_name)
        return quiescent_log


class TestQuiescentWaterTetgen(TestTools.AirWaterVVTest):

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self,method):
        #pass
        Profiling.openLog("proteus.log",10)
        Profiling.logAllProcesses = True



    def teardown_method(self,method):
        Profiling.closeLog()

        """ Tear down function """
        FileList = ['quiescent_water_test_gauges.xmf',
                    'quiescent_water_test_gauges0.h5',]
        for file in FileList:
            if os.path.isfile(file):
                os.remove(file)
            else:
                pass


            
    def test_run(self):
        #from petsc4py import PETSc
        #pList = []
        #nList = []
        #so = load_so('quiescent_water_test_gauges_so',modulepath)
        #for (p,n) in so.pnList:
        #    pList.append(load_p(p,modulepath))
        #    nList.append(load_n(n,modulepath))
        #    if pList[-1].name == None:
        #        pList[-1].name = p
        ##so = quiescent_water_test_gauges_so
        #so.name = "quiescent_water_test_gauges"
        #if so.sList == []:
        #    for i in range(len(so.pnList)):
        #        s = default_s
        #        so.sList.append(s)
        #Profiling.logLevel=7
        #Profiling.verbose=True
        ## PETSc solver configuration
        #OptDB = PETSc.Options()
        #with open(petsc_options) as f:
        #    all = f.read().split()
        #    i=0
        #    while i < len(all):
        #        if i < len(all)-1:
        #            if all[i+1][0]!='-':
        #                print "setting ", all[i].strip(), all[i+1]
        #                OptDB.setValue(all[i].strip('-'),all[i+1])
        #                i=i+2
        #            else:
        #                print "setting ", all[i].strip(), "True"
        #                OptDB.setValue(all[i].strip('-'),True)
        #                i=i+1
        #        else:
        #            print "setting ", all[i].strip(), "True"
        #            OptDB.setValue(all[i].strip('-'),True)
        #            i=i+1
        #so.tnList=[0.0,0.001,0.011]            
        ##so.tnList=[0.0,0.001]+[0.001 + i*0.01 for i in range(1,int(round(0.03/0.01))+1)]            
        #ns = NumericalSolution.NS_base(so,pList,nList,so.sList,opts)
        #ns.calculateSolution('quiescent_water_test_gauges')
        
        runCommand = "parun --TwoPhaseFlow --path " +modulepath+" -C \"T=0.011 amplitude=0.0 he=0.01\" wavesloshing.py"
        subprocess.check_call(runCommand,shell=True)

        quiescent_log = NumericResults.create_log('proteus.log')

        text = quiescent_log.read()
        
        #if text.find('CFL') != -1:
        if text.find('Step Failed,') != -1:
   
            a = "No convergence"
        else:
            a = "good"
        

        if a  == "No convergence":
            print ("Convergence issue")
            assert False
        else:
            assert True




        #def failed(filename,word):
        #    file = open(filename,"r")
        #    text = file.read()

        #    if text.find(word) != -1:
        #        a = "No convergence"
        #    else:
        #        a = "good"
        #    file.close()
        #    return a

        #b = failed('proteus.log','Step Failed,')

        #if b == "No convergence":
        #    print ("Convergence issue")
        #    assert False
        #else:
        #    assert True

        #assert(True)
       
#    def test_validate(self):
#        # Reading probes into the file
#        file_pressurePoint = 'pressure_PointGauge.csv'
#        file_pressureLine = 'pressure_LineGauge.csv'
#        file_vof = 'vof_LineIntegralGauge.csv'
#
#        def readProbeFile(filename):
#            with open (filename, 'rb') as csvfile:
#                data=np.loadtxt(csvfile, delimiter=",",skiprows=1)
#                time=data[:,0]
#                data = data[:,1:]
#                csvfile.seek(0)
#                header = csvfile.readline()
#                header = header.replace("time","")
#                header = header.replace("[","")
#                header = header.replace("]","")
#                header =  header.replace(","," ")
#                header = header.split()
#                probeType = []
#                probex = []
#                probey = []
#                probez = []        
#                for ii in range(0,len(header),4):
#                    probeType.append(header[ii])
#                    probex.append(float(header[ii+1]))
#                    probey.append(float(header[ii+2]))
#                    probez.append(float(header[ii+3]))
#                probeCoord = zip(np.array(probex),np.array(probey),np.array(probez))
#                datalist = [probeType,probeCoord,time,data]
#                return datalist
#        
#        # Exctracting probes
#        data_p_point = readProbeFile(file_pressurePoint)
#        data_p_line = readProbeFile(file_pressureLine)
#        data_vof = readProbeFile(file_vof)
#        time = data_p_point[2]
#        P_point = data_p_point[3]
#        P_line = data_p_line[3]
#        vof = data_vof[3]
#        water_level = []
#        H = qw.tank_dim[1]
#        for i in range(0,len(vof)):
#            water_level.append(H-vof[i])
#        Y = []
#        for i in range(0,len(data_p_line[1])):
#            Y.append(data_p_line[1][i][1])
#        Y = np.array(Y)
#        # Definition of the theoretical pressure under and over water
#        rho_w = qw.rho_0
#        rho_a = qw.rho_1
#        g = abs(qw.g[1])
#        h = qw.waterLine_z
#        def p(y):
#            if np.any(y<=h):
#                return rho_a*g*(H-h) + rho_w*g*(h-y)
#            else:
#                return rho_a*g*(H-y)
#        # Validation of the result
#        water_level_th = qw.waterLine_z
#        wl = water_level
#        water_level_num = wl[-1][0]
#        err_wl = 100*abs(water_level_th-water_level_num)/water_level_th
#        press_point_th = p(0.3)
#        press_point_num = P_point[-1][0]
#        err_pp = 100*abs(press_point_th-press_point_num)/press_point_th
#        S = 0.
#        for i in range(0,len(Y)-4): # Ignores the 4 last points beside the water surface
#            S = S + abs(p(Y[i])-P_line[-1][i])/p(Y[i])
#        err_pl = 100*S/(len(Y)-4)
#        assert(err_wl<1.)
#        assert(err_pp<1.)
#        assert(err_pl<1.)

if __name__ == '__main__':
    pass
