#!/usr/bin/env python
import pytest
from proteus.iproteus import *
from proteus import Comm
comm = Comm.get()
import os
import numpy as np
import collections as cll
import csv
from proteus.test_utils import TestTools

class TestDambreakColagrossiTetgen(TestTools.AirWaterVVTest):
       
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self,method):
        pass

    def teardown_method(self,method):
        """ Tear down function """
        FileList = ['dambreak_Colagrossi.xmf',
                    'dambreak_Colagrossi.h5']
        for file in FileList:
            if os.path.isfile(file):
                os.remove(file)
            else:
                pass

    fast = pytest.mark.skipif(not pytest.config.getoption("--runfast"), 
            reason="need --runfast option to run")
    
    slow = pytest.mark.skipif(pytest.config.getoption("--runfast"), 
            reason="no --runfast option to run")

    @fast
    def test_run_fast(self):
        os.chdir('2d/benchmarks/dambreak_Colagrossi/')
        import dambreak_Colagrossi_so
        import dambreak_Colagrossi as dc
        from petsc4py import PETSc
        pList = []
        nList = []
        for (p,n) in dambreak_Colagrossi_so.pnList:
            pList.append(__import__(p))
            nList.append(__import__(n))
            if pList[-1].name == None:
                pList[-1].name = p
        so = dambreak_Colagrossi_so
        so.name = "dambreak_Colagrossi"
        if so.sList == []:
            for i in range(len(so.pnList)):
                s = default_s
                so.sList.append(s)
        Profiling.logLevel=7
        Profiling.verbose=True
        # PETSc solver configuration
        OptDB = PETSc.Options()
        with open("../../../inputTemplates/petsc.options.asm") as f:
            all = f.read().split()
            i=0
            while i < len(all):
                if i < len(all)-1:
                    if all[i+1][0]!='-':
                        print "setting ", all[i].strip(), all[i+1]
                        OptDB.setValue(all[i].strip('-'),all[i+1])
                        i=i+2
                    else:
                        print "setting ", all[i].strip(), "True"
                        OptDB.setValue(all[i].strip('-'),True)
                        i=i+1
                else:
                    print "setting ", all[i].strip(), "True"
                    OptDB.setValue(all[i].strip('-'),True)
                    i=i+1
        so.tnList=[0.0,0.001]+[0.001 + i*0.01 for i in range(1,int(round(0.09/0.01))+1)]
        ns = NumericalSolution.NS_base(so,pList,nList,so.sList,opts)
        ns.calculateSolution('dambreak_Colagrossi')
        assert(True)

    @slow
    def test_run_slow(self):
        from petsc4py import PETSc
        import dambreak_Colagrossi_so
        import dambreak_Colagrossi as dc
        pList = []
        nList = []
        for (p,n) in dambreak_Colagrossi_so.pnList:
            pList.append(__import__(p))
            nList.append(__import__(n))
            if pList[-1].name == None:
                pList[-1].name = p
        so = dambreak_Colagrossi_so
        so.name = "dambreak_Colagrossi"
        if so.sList == []:
            for i in range(len(so.pnList)):
                s = default_s
                so.sList.append(s)
        Profiling.logLevel=7
        Profiling.verbose=True
        # PETSc solver configuration
        OptDB = PETSc.Options()
        with open("../../../inputTemplates/petsc.options.asm") as f:
            all = f.read().split()
            i=0
            while i < len(all):
                if i < len(all)-1:
                    if all[i+1][0]!='-':
                        print "setting ", all[i].strip(), all[i+1]
                        OptDB.setValue(all[i].strip('-'),all[i+1])
                        i=i+2
                    else:
                        print "setting ", all[i].strip(), "True"
                        OptDB.setValue(all[i].strip('-'),True)
                        i=i+1
                else:
                    print "setting ", all[i].strip(), "True"
                    OptDB.setValue(all[i].strip('-'),True)
                    i=i+1
        ns = NumericalSolution.NS_base(so,pList,nList,so.sList,opts)
        ns.calculateSolution('dambreak_Colagrossi')
        assert(True)

    @slow
    def test_validate(self):
        import dambreak_Colagrossi_so
        import dambreak_Colagrossi as dc
        # Reading file
        filename='pressureGauge.csv'
        with open (filename, 'rb') as csvfile: 
            data=csv.reader(csvfile, delimiter=",")
            a=[]
            time=[]
            probes=[]
            nRows=0
            for row in data:
                if nRows!=0:
                    time.append(float(row[0]))
                if nRows==0:              
                    for i in row:              
                        if i!= '      time':   
                            i=float(i[14:24])  
                            probes.append(i)   
                row2=[]
                for j in row:
                    if j!= '      time' and nRows>0.:
                        j=float(j)
                        row2.append(j)
                a.append(row2)
                nRows+=1
            # Making the pressure dimensionless   
            pressure2=np.zeros(nRows-1, dtype=float)
            pressure2A=np.zeros(nRows-1, dtype=float)
            timeA=np.zeros(nRows-1, dtype=float)
            for k in range(1,nRows):
                pressure2[k-1]=(float(a[k][1]))    
                timeA[k-1]=time[k-1]*(9.81/0.6)**0.5
            pressure2A=pressure2/(998.2*9.81*0.6)
            # Validation of the results
            maxPressureCal = max(pressure2A)
            maxPressureRef = 0.876481416000
            err = 100*abs(maxPressureRef-maxPressureCal)/maxPressureRef
            assert(err<12.0)

if __name__ == '__main__':
    pass
