Non linear waves propagation over a flat bottom  benchmark case
===============================================================

Plane regular nonlinear waves are mild and high steepness waves that propagate in a single direction, in uniform wave fronts.  The wave profile deviates from the sinusoidal shape, and it typically exhibits high and sharp wave crests and low and flat wave troughs.  We cannot always accurately calculate the wave celerity from the linear dispersion theory, especially for highly nonlinear waves.  Fenton (1988) proposes a method for calculating the nonlinear wave properties and profile, which we have adopted for the modelling of nonlinear waves within Proteus. 

Non linear waves are steeper waves than the linear, with larger surface slope. The free-surface slope depends on:
The ratio of the wave height (H) to the wavelength (L), as an indication of the free-surface slope magnitude.
The ratio of the wave height (H) to the depth (d), as an indication for the wave profile shape.
Large height to depth ratios contribute in non-sinusoidal and steeper wave profiles. Given the wave period, the wavelength will be a function of the water depth. So it is the wave period, water depth and the wave height that contribute to the linearity or nonlinearity of the wave. Their interrelation is summarised in the following figure (Lé Méhauté 1976).


.. figure:: ./Mehaute_nonlinear_waves_01.png


where, the vertical axis corresponds to the no dimensional wave height and the horizontal to the no dimensional water depth. The term gT\ :sup:`2`\ is proportional to the wavelength in deep water and the dot named A corresponds to the tested case which is described below.
The present problem consists of 2D rectangular numerical flume with height of 1.5 m and a length of 40.6 m, where the mean water depth is equal to 0.873 m. At the left boundary, a non-linear wave is generated with a height of 0.109 m and a period of 2.95 s using Fenton's method. The bottom boundary acts as a free-slip wall and in the right boundary free outflow conditions have been assigned. 

This case tests demonstrates the ability of PROTEUS to simulate the generation and propagation of non-linear waves as well as their absorption.

References
--------------------------------

- Fenton JD (1988) The numerical solution of steady water wave problems, Comp and Geosc, 14(3), 357-368.







