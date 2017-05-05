Linear wave propagation and absorption
======================================

To consider a wave linear, its free-surface slope must be very small (~ 0.1%).  The 
free-surface slope depends on:

* The ratio of the wave height (:math:`H`) to the wavelength (:math:`L`), as an 
indication of the free-surface slope magnitude.
* The ratio of the wave height (:math:`H`) to the depth (:math:`d`), as an 
indication for the wave profile shape.  
Large height to depth ratios contribute in non-sinusoidal and steeper wave profiles.
Given the wave period, the wavelength will be a function of the water depth.  
So it is the wave period, water depth and the wave height that contribute to the 
linearity or nonlinearity of the wave. 
Their interrelation is summarised in the following figure (Lé Méhauté 1976).  

.. figure:: ./Mehaute_linear_waves_01.png 

where, the vertical axis corresponds to the no dimensional wave height and the 
horizontal to the no dimensional water depth.  The term :math: `gT^2` is 
proportional to the wavelength in deep water and the dot named A corresponds to the 
tested case which is described below.   

The present problem consists of a 1.5m x 30.0m (height x length) numerical flume with 
a flat bottom and a mean water depth equal to 1.0m. At the left boundary, a linear 
wave is generated with a height of 0.025m and a period of 1.94s. There is a 5m 
generation zone on the left side and a 10m absorption zone on the right.

This case tests demonstrates the ability of PROTEUS to simulate the generation of 
linear waves as well as their absorption.

The python test file named ``test_linearWaves.py`` is made up of three tests:

* The first one is to know if the case can run.
* The second test is to validate the results comparing them to the theory. For this case we will compare the numerical and theoretical wave height in the middle of the tank.
* The third one is to test the reflection. 
One can run this test file typing ``py.test --boxed test_linearWaves.py``.

References
----------

- US Army Corps of Engineer (2002) Coastal Engineering Manual. Engineer Manual 
1110-2-1100, US Army Corps of Engineers, Washington, DC (in 6 volumes)

- Lé Méhauté, B., (1976). “Introduction to Hydrodynamics and water waves”, 
Springer-Verlag, New York.


