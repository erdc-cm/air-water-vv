import sys
import setuptools
from distutils.core import setup, Extension

import numpy
from Cython.Distutils import build_ext

## \file setup.py setup.py
#  \brief The python script for building proteus
#
#  Set the DISTUTILS_DEBUG environment variable to print detailed information while setup.py is running.
#

from proteus import config
from proteus.config import *

###to turn on debugging in c++
##\todo Finishing cleaning up setup.py/setup.cfg, config.py...
from distutils import sysconfig
cv = sysconfig.get_config_vars()
cv["OPT"] = cv["OPT"].replace("-DNDEBUG","-DDEBUG")
cv["OPT"] = cv["OPT"].replace("-O3","-g")
cv["CFLAGS"] = cv["CFLAGS"].replace("-DNDEBUG","-DDEBUG")
cv["CFLAGS"] = cv["CFLAGS"].replace("-O3","-g")

PROTEUS_PETSC_EXTRA_LINK_ARGS = getattr(config, 'PROTEUS_PETSC_EXTRA_LINK_ARGS', [])
PROTEUS_PETSC_EXTRA_COMPILE_ARGS = getattr(config, 'PROTEUS_PETSC_EXTRA_COMPILE_ARGS', [])

proteus_install_path = os.path.join(sysconfig.get_python_lib(), 'proteus')

# handle non-system installations
for arg in sys.argv:
    if arg.startswith('--root'):
        proteus_install_path = proteus_install_path.partition(sys.prefix + '/')[-1]
        break
    if arg.startswith('--prefix'):
        proteus_install_path = proteus_install_path.partition(sys.prefix + '/')[-1]
        break

#import os
#os.environ["CC"] = "mpicc"
#print("PATH :", os.environ["LD_LIBRARY_PATH"])
#print("LD_LIBRARY_PATH :", os.environ["LD_LIBRARY_PATH"])
#print("INCLUDE_PATH :", os.environ["INCLUDE_PATH"])

setup(name='ChRigidBody',
      cmdclass = {'build_ext':build_ext},
      ext_modules=[Extension("ChRigidBody",['ChRigidBody.pyx'],
                             depends=['ChRigidBody.h'],
                             language='c++',
                             include_dirs=[numpy.get_include(),'proteus',PROTEUS_INCLUDE_DIR],
                             library_dirs=[PROTEUS_LIB_DIR],
                             libraries=['ChronoEngine',
                                        'stdc++','m'],
                             extra_compile_args=["-std=c++11"])]
      )
