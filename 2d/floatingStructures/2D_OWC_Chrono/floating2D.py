from proteus import Domain, Context, Comm
from proteus.mprans import SpatialTools as st
from proteus import WaveTools as wt
from proteus.Profiling import logEvent
from proteus.mbd import CouplingFSI as fsi
import pychrono as pc
from math import *
import numpy as np


opts=Context.Options([
    # predefined test cases
    ("water_level", 1.03, "Height of free surface above bottom"),
    # tank
    ("tank_dim", (3.137*2, 3.,), "Dimensions of the tank"),
    ("tank_sponge", (3.137, 3.137*2), "Length of absorption zones (front/back, left/right)"),     #redundant
    ("tank_BC", 'freeslip', "Length of absorption zones (front/back, left/right)"),
    ("gauge_output", False, "Places Gauges in tank"),
    ("gauge_fixed", False, "Places Gauges in tank"),
    # waves
    ("waves", True, "Generate waves (True/False)"),
    ("wave_period", 1.4185, "Period of the waves"),
    ("wave_height", 0.07, "Height of the waves"),
    ("wave_dir", (1., 0., 0.), "Direction of the waves (from left boundary)"),
    ("wave_type", 'Fenton', "type of wave (Fenton/Linear)"),
    ("eps", 0.5, "eps"),
    ("w", 0., "frequency"),
    # caisson
    ("caisson", True, "caisson"),
    ("caisson_dim", (0.9, 0.36), "Dimensions of the caisson"),
    ("caisson_gap", 0.18, "Diameter of the WEC water column"),
    ("caisson_lid", 0.06, "Thickness of the WEC Lid"),
    ("caisson_pto", 0.18, "Diameter of the PTO hole"),
    ("caisson_ycoord", None, "Dimensions of the caisson"),
    ("caisson_xcoord", None, "Dimensions of the caisson"),
    ("caisson_width", 1., "Width of the caisson"),
    ("caisson_corner_r", 0.00, "radius of the corners of the caisson"),
    ("caisson_corner_side", 'all', "corners placement"),
    ("caisson_BC", 'freeslip', "BC on caisson ('noslip'/'freeslip')"),
    ("free_x", (1.0, 1.0, 0.0), "Translational DOFs"),
    ("free_r", (0.0, 0.0, 1.0), "Rotational DOFs"),
    ("VCG", 0.18, "vertical position of the barycenter of the caisson"),
    ("caisson_mass", 50., "Mass of the caisson"),
    ("caisson_inertia", 16.605, "Inertia of the caisson"),
    ("rotation_angle", 0., "Initial rotation angle (in degrees)"),
    ("chrono_dt", 0.00001, "time step of chrono"),
    ("coupling_scheme", "CSS", "coupling scheme"),
    ("timestepper", "Euler", "Chrono timestepper"),
    ("addedMass", True, "Apply Added Mass"),
    ("forced_oscillation", False, "Apply Forced Oscilation to the body"),
    ("forced_freq", 5.30, "Frequency of Forced oscillation"),
    ("forced_amp", 0.0025, "Amplitude of Forced oscillation"),
     # mooring
    ("mooring", True, "add moorings"),
    ("mooring_type", 'Chrono_Catenary', "type of moorings"),
    #Simplie Spring
    ("mooring_anchor", (0.5,0,0.), "anchor coordinates (x relative to barycenter, y,z global"),
    ("mooring_anchor_2", (-0.5,0,0.), "Anchor coordinates"),
    ("mooring_fairlead", (0.5,-0.18,0.), "fairlead cooridnates (relative coordinates from barycenter)"),
    ("mooring_fairlead_2", (-0.5,-0.18,0.), "fairlead coordinates (relative coordinates from barycenter)"),
    ("mooring_K", 58549.35, "mooring (spring) stiffness"),
    ("mooring_R", 1530.35, "mooring (spring) damping"),
    ("mooring_restlength", 0.84, "mooring (spring) rest length"),
    #Chrono Catenary Mooring options
    ("ChFairlead_r", 0.39, "Fairlead of Chrono Mooring"),
    ("ChFairlead_D", 0.18, "Fairlead Depth below Barycentre"),
    ("ChAnchor_r", 0.89, "Anchor Radius"),
    ("ChAnchor_D", 1.03, "Anchor Depth below Free Surface"),
    ("ChLineLength", 1.14, "Catenary Length"),
    #TBC
    # mesh refinement
    ("refinement", True, "Gradual refinement"),
    ("he", 0.1, "Set characteristic element size"),
    ("he_max", 0.1, "Set maximum characteristic element size"),
    ("he_caisson", 0.1, "Set maximum characteristic element size on caisson boundary"),
    ("he_max_water", 0.1, "Set maximum characteristic in water"),
    ("he_free_surface", 0.1, "Set Maximum characteristic near the free surface"),
    ("refinement_freesurface", 0.35, "Set area of constant refinement around free surface (+/- value)"),
    ("refinement_caisson", 0.75, "Set area of constant refinement (Box) around caisson (+/- value)"),
    ("refinement_grading", 1.1, "Grading of refinement/coarsening (default: 10% volume)"),
    # numerical options
    ("genMesh", False, "True: generate new mesh every time. False: do not generate mesh if file exists"),
    ("use_gmsh", True, "True: use Gmsh. False: use Triangle/Tetgen"),
    ("movingDomain", True, "True/False"),
    ("T", 10.0, "Simulation time"),
    ("dt_init", 0.001, "Initial time step"),
    ("dt_fixed", None, "Fixed (maximum) time step"),
    ("timeIntegration", "backwardEuler", "Time integration scheme (backwardEuler/VBDF)"),
    ("cfl", 0.4 , "Target cfl"),
    ("nsave", 5, "Number of time steps to save per second"),
    ("useRANS", 0, "RANS model"),
    ("sc", 0.25, "shockCapturing factor"),
    ("weak_factor", 10., "weak bc penalty factor"),
    ("strong_dir", False, "strong dirichlet (True/False)"),
    ("parallel", True ,"Run in parallel")])

# ----- CONTEXT ------ #

wavelength=1.
# general options
waterLevel = opts.water_level
rotation_angle = np.radians(opts.rotation_angle)

g = [0.0, -9.81]
rho_0=998.2


st_circle = False

# waves
height = opts.wave_height
mwl = depth = opts.water_level
period = opts.wave_period    
wave = wt.MonochromaticWaves(period=opts.wave_period, waveHeight=height, mwl=mwl, depth=depth,
                                 g=np.array([0., -9.81, 0.]), waveDir=opts.wave_dir,
                                 waveType=opts.wave_type,
                                 Nf=8,
                                 fast=False)
wavelength = wave.wavelength


# tank options
tank_dim = (8*wavelength+opts.caisson_dim[0], opts.water_level*2)
tank_sponge = (wavelength, 2*wavelength)

logEvent("TANK SPONGE: "+str(tank_sponge))
logEvent("TANK DIM: "+str(tank_dim))




# ----- DOMAIN ----- #

##FOR TESTING
dim=opts.caisson_dim

domain = Domain.PlanarStraightLineGraphDomain()
# caisson options
if opts.caisson is True:
    dim = opts.caisson_dim
    VCG = opts.VCG
    if VCG is None:
        VCG = dim[1]/2.
    free_x = opts.free_x
    free_r = opts.free_r
    rotation = np.radians(opts.rotation_angle)
    coords = [0,0]
    coords[0] = opts.caisson_xcoord or tank_dim[0]/2.
    coords[1] = opts.caisson_ycoord or tank_dim[1]/2.
    barycenter = (0, -dim[1]/2.+VCG, 0.)
    width = opts.caisson_width
    inertia = opts.caisson_inertia/width


    caisson_coords = coords
    caisson_dim = opts.caisson_dim

    if opts.he_caisson:
        he_caisson = opts.he_caisson
    else:
        he_caisson = opts.he

    radius = opts.caisson_corner_r
    if radius != 0:
        def quarter_circle(center, radius, p_nb, angle, angle0=0., v_start=0.):
            # p_nb = int(np.ceil(2*np.pi*radius/dx))  # number of points on segment
            # p_nb = refinement
            vertices = []
            segments = []
            for i in range(p_nb):
                x = radius*np.sin(angle0+angle*float(i)/(p_nb-1))
                y = radius*np.cos(angle0+angle*float(i)/(p_nb-1))
                vertices += [[center[0]+x, center[1]+y]]
                if i > 0:
                    segments += [[v_start+(i-1), v_start+i]]
                elif i == p_nb-1:
                    segments += [[v_start+i, v_start]]
            return vertices, segments
 

        #nb = int(np.pi/2/(np.arcsin(he_caisson/2./radius)*2))
        #nb = int((np.pi*2*radius/4.)/(he_caisson))
        nb = 6
        vertices = []
        vertexFlags = []
        segments = []
        segmentFlags = []
        dim = opts.caisson_dim
        gap = opts.caisson_gap
        lid = opts.caisson_lid
        if opts.caisson_corner_side == 'bottom':
            angle0 = [np.pi/2., 0., 3.*np.pi/2., np.pi, 3.*np.pi/2., 0., 3.*np.pi/2., np.pi]
            angle1 = [-np.pi/2., -np.pi/2., -np.pi/2., -np.pi/2., -np.pi/2., -np.pi/2., -np.pi/2., -np.pi/2.]
            centers = [[dim[0]/2., dim[1]/2.], 
                       [-dim[0]/2., dim[1]/2.],
                       [-dim[0]/2.+radius, -dim[1]/2.+radius],
                       [-gap/2.-radius, -dim[1]/2.+radius],
                       [-gap/2., dim[1]/2.-lid],
                       [gap/2., dim[1]/2.-lid],
                       [gap/2.+radius, -dim[1]/2.+radius],
                       [dim[0]/2.-radius, -dim[1]/2.+radius]]
            p_nb = [0, 0, nb, nb, 0, 0, nb, nb]
        else:
            angle0 = [np.pi/2., 0., 3.*np.pi/2., np.pi, 3.*np.pi/2., 0., 3.*np.pi/2., np.pi]
            angle1 = [-np.pi/2., -np.pi/2., -np.pi/2., -np.pi/2., np.pi/2., np.pi/2., -np.pi/2., -np.pi/2.]
            centers = [[dim[0]/2.-radius, dim[1]/2.-radius],
                       [-dim[0]/2.+radius, dim[1]/2.-radius],
                       [-dim[0]/2.+radius, -dim[1]/2.+radius],
                       [-gap/2.-radius, -dim[1]/2.+radius],
                       [-gap/2.+radius, dim[1]/2.-lid-radius],
                       [gap/2.-radius, dim[1]/2.-lid-radius],
                       [gap/2.+radius, -dim[1]/2.+radius],
                       [dim[0]/2.-radius, -dim[1]/2.+radius]]
            p_nb = [nb, nb, nb, nb, nb, nb, nb, nb]
        center = [0., 0.]
        flag = 1
        v_start = 0
        for i in range(len(angle0)):
            v_start = len(vertices)
            if p_nb[i] != 0:
                v, s = quarter_circle(center=centers[i], radius=radius, p_nb=p_nb[i],
                                      angle=angle1[i], angle0=angle0[i],
                                      v_start=v_start)
            else:
                v = [centers[i]]
                if v_start > 1:
                    s = [[v_start-1, v_start]]
                else:
                    s = []
            vertices += v
            vertexFlags += [1]*len(v)
            segments += s+[[len(vertices)-1, len(vertices)]]
            segmentFlags += [1]*len(s)+[1]
        segments[-1][1] = 0  # last segment links to vertex 0
        boundaryTags = {'caisson': 1}
        caisson = st.CustomShape(domain, barycenter=barycenter,
                                 vertices=vertices, vertexFlags=vertexFlags,
                                 segments=segments, segmentFlags=segmentFlags,
                                 boundaryTags=boundaryTags)
        facet = []
        for i, vert in enumerate(caisson.vertices):
            facet += [i]
        caisson.facets = np.array([[facet]])
        caisson.facetFlags = np.array([1])
        caisson.regionFlags = np.array([1])
    else:
        if opts.caisson_pto == opts.caisson_gap:
            d = opts.caisson_dim[1]
            bd = (opts.caisson_dim[0] - opts.caisson_gap)/2.
            gap = opts.caisson_gap
            lid = opts.caisson_lid
            pto = opts.caisson_pto
            vertices = [[    gap/2.,-d/2.    ],
                        [ bd+gap/2.,-d/2.    ],
                        [ bd+gap/2., d/2.    ],
                        [    pto/2., d/2.    ],
                        [   -pto/2., d/2.    ],
                        [-bd-gap/2., d/2.    ],
                        [-bd-gap/2.,-d/2.    ],
                        [   -gap/2.,-d/2.    ]]
            vertexFlags = [1]*len(vertices)
            segments = []
            facet1 = []
            facet2 = []
            for i in (range(len(vertices)/2)):
                segments += [[i, i+1]]
                segmentFlags = [1]*4
            segments[-1][1] = 0              # Last Segment to link
            for i in range((1+len(vertices))/2,len(vertices)):
                segments += [[i, i+1]]
            segments[-1][1] = (len(vertices))/2
            segmentFlags = [1]*len(segments)
            #print('SEGMENTS',segments)
            boundaryTags = {'caisson': 1}
            caisson = st.CustomShape(domain, barycenter=barycenter,
                                         vertices=vertices, vertexFlags=vertexFlags,
                                         segments=segments, segmentFlags=segmentFlags,
                                         boundaryTags=boundaryTags )
            for i in range((len(vertices))/2):
                facet1 += [i]
            for i in range((1+len(vertices))/2,len(vertices)):
                facet2 += [i]
            #print('facets',facet1, facet2)
            caisson.facets = ([facet1], [facet2])
            #print(caisson.facets)
            caisson.facetFlags = np.array([1, 1])
            caisson.regionFlags = np.array([1, 1])
        else:
            d = opts.caisson_dim[1]
            bd = (opts.caisson_dim[0] - opts.caisson_gap)/2.
            gap = opts.caisson_gap
            lid = opts.caisson_lid
            pto = opts.caisson_pto
            vertices = [[    pto/2., d/2.-lid],
                        [    gap/2., d/2.-lid],
                        [    gap/2.,-d/2.    ],
                        [ bd+gap/2.,-d/2.    ],
                        [ bd+gap/2., d/2.    ],
                        [    pto/2., d/2.    ],
                        [   -pto/2., d/2.    ],
                        [-bd-gap/2., d/2.    ],
                        [-bd-gap/2.,-d/2.    ],
                        [   -gap/2.,-d/2.    ],
                        [   -gap/2., d/2.-lid],
                        [   -pto/2., d/2.-lid]]
            vertexFlags = [1]*len(vertices)
            segments = []
            facet1 = []
            facet2 = []
            for i in (range(len(vertices)/2)):
                segments += [[i, i+1]]
                segmentFlags = [1]*6
            segments[-1][1] = 0              # Last Segment to link
            for i in range((1+len(vertices))/2,len(vertices)):
                segments += [[i, i+1]]
            segments[-1][1] = (len(vertices))/2
            segmentFlags = [1]*len(segments)
            #print('SEGMENTS',segments)
            boundaryTags = {'caisson': 1}
            caisson = st.CustomShape(domain, barycenter=barycenter,
                                     vertices=vertices, vertexFlags=vertexFlags,
                                     segments=segments, segmentFlags=segmentFlags,
                                     boundaryTags=boundaryTags )
            for i in range((len(vertices))/2):
                facet1 += [i]
            for i in range((1+len(vertices))/2,len(vertices)):
                facet2 += [i]
            #print('facets',facet1, facet2)
            caisson.facets = ([facet1], [facet2])
            #print(caisson.facets)
            caisson.facetFlags = np.array([1, 1])
            caisson.regionFlags = np.array([1, 1])

    ang = rotation_angle
    caisson.setHoles([[ opts.caisson_dim[0]/2 - opts.caisson_gap/2., 0.],
                      [-opts.caisson_dim[0]/2 + opts.caisson_gap/2., 0.]])
    caisson.holes_ind = np.array([0, 1])
    caisson.translate([caisson_coords[0], caisson_coords[1]])
    #print(caisson.vertices)
    #print("Caisson_Barycenter, pre",caisson.barycenter)
    # system = crb.System(np.array([0., -9.81, 0.]))
    # rotation = np.array([1, 0., 0., 0.])
    rotation_init = np.array([np.cos(ang/2.), 0., 0., np.sin(ang/2.)*1.])
    caisson.rotate(ang, pivot=caisson.barycenter)
    system = fsi.ProtChSystem()
    system.ChSystem.Set_G_acc(pc.ChVectorD(g[0], g[1], 0.))
    system.setTimeStep(opts.chrono_dt)
    system.setTimestepperType(opts.timestepper)
    system.setCouplingScheme(opts.coupling_scheme, prediction="backwardEuler")
    body = fsi.ProtChBody(system=system)
    x, y, z = caisson.barycenter
    #print("Caisson_Barycenter, post",caisson.barycenter)
    pos = pc.ChVectorD(x, y, z)
    e0, e1, e2, e3 = rotation_init
    rot = pc.ChQuaternionD(e0, e1, e2, e3)
    inertia = pc.ChVectorD(1., 1., inertia)
    # chrono functions
    body.ChBody.SetPos(pos)
    body.ChBody.SetRot(rot)
    body.ChBody.SetMass(opts.caisson_mass)
    body.ChBody.SetInertiaXX(inertia)
    # customised functions
    body.attachShape(caisson)
    body.setConstraints(free_x=np.array(opts.free_x), free_r=np.array(opts.free_r))
    body.setRecordValues(all_values=True)

## Moorings

    if opts.mooring is True:
        #Scale Anchor Coordinates to absolute coordinates
        anchor = np.array([0.,0.,0.])
        anchor2 = np.array([0.,0.,0.])
        anchor[0] = opts.mooring_anchor[0] + coords[0]
        anchor[1] = opts.mooring_anchor[1]
        anchor2[0] = opts.mooring_anchor_2[0] + coords[0]
        anchor2[1] = opts.mooring_anchor_2[1]

        if opts.mooring_type == 'spring':
            body.addSpring(stiffness=opts.mooring_K, damping=opts.mooring_R,
                           fairlead=np.array(opts.mooring_fairlead),
                           anchor=anchor,
                           rest_length=opts.mooring_restlength)
            body.addSpring(stiffness=opts.mooring_K, damping=opts.mooring_R,
                           fairlead=np.array(opts.mooring_fairlead_2),
                           anchor=anchor2,
                           rest_length=opts.mooring_restlength)
        elif opts.mooring_type == 'prismatic':
            body.addPrismaticLinksWithSpring(stiffness=opts.mooring_K, damping=opts.mooring_R,
                           pris1=np.array([0.,caisson.barycenter[1],0.]),
                           pris2=np.array([0.,0.,0.]),
                           rest_length=caisson.barycenter[0])
        elif opts.mooring_type == 'Chrono_Catenary':
            #2 Moorings
            #Variables
	    L = opts.ChLineLength
            d = 0.01
            A0 = 0.25*np.pi*d**2.
            w = 30.              #kg/m
            nb_elems = 50
            dens = w/A0 + rho_0
            E = 100.0e6/A0
            
            fairlead_radius = opts.ChFairlead_r
            anchor_radius = opts.ChAnchor_r
            fairlead_depth = opts.ChFairlead_D
            anchor_depth = opts.ChAnchor_D

            mooring_X = anchor_radius-fairlead_radius
            mooring_Y = anchor_depth-fairlead_depth  #depth +ve downwards
	    fairlead_height = waterLevel-fairlead_depth
            anchor_height = waterLevel-anchor_depth

            #Fairleads
            fairlead_centre = np.array([caisson.barycenter[0], caisson.barycenter[1]-fairlead_depth, 0])
            fairlead_1 = fairlead_centre + np.array([fairlead_radius, 0, 0])
            fairlead_2 = fairlead_centre - np.array([fairlead_radius, 0, 0])
            
            #Anchors
            anchor_1 = fairlead_1 + np.array([ mooring_X, -mooring_Y, 0])
            anchor_2 = fairlead_2 + np.array([-mooring_X, -mooring_Y, 0])

            #print("Anchor1",anchor_1)
            #print("Fairlead1", fairlead_1)
            #print("Anchor2",anchor_2)
            #print("fairlead2",fairlead_2)

            #Quasi-Statics
            from catenary import MooringLine
            EA = 1e20 #To prevent stretching
	    l1 = MooringLine(L=L, w=w, EA=EA, anchor=anchor_1, fairlead=fairlead_1, nd=2, tol=1e-8)
            l2 = MooringLine(L=L, w=w, EA=EA, anchor=anchor_2, fairlead=fairlead_2, nd=2, tol=1e-8)
            #print("l1a",l1.anchor,"l1f",l1.fairlead)
            l1.setVariables()
            l2.setVariables()
            #function for setting out the cables
            #print("l1a_postset",l1.anchor,"l1f",l1.fairlead)
            m1_s = l1.s
            m2_s = l2.s
            m1_ds = l1.ds
            m2_ds = l2.ds

            #Testing
            test_l1=l1
            test_l2=l2
            #Make Chrono Cables
            mesh = fsi.ProtChMesh(system)
            L = np.array([L])
            d = np.array([d])
            nb_elems = np.array([nb_elems])
            E = np.array([E])
            dens = np.array([dens])
            cable_type = "CableANCF"
            m1 = fsi.ProtChMoorings(system=system, mesh=mesh, length=L, nb_elems=nb_elems, d=d, rho=dens, E=E, beam_type=cable_type)
            m2 = fsi.ProtChMoorings(system=system, mesh=mesh, length=L, nb_elems=nb_elems, d=d, rho=dens, E=E, beam_type=cable_type)
            m1.setName('mooring1')
            m2.setName('mooring2')
            m1.setNodesPositionFunction(m1_s, m1_ds)
            m2.setNodesPositionFunction(m2_s, m2_ds)
            # for anchor (with fixed body)
    	    #body2 = fsi.ProtChBody(system)
    	    #body2.ChBody.SetBodyFixed(True)
            #body2.barycenter0 = np.zeros(3)
            moorings = [m1, m2]
            
            for m in moorings:
       		m.external_forces_from_ns = True
        	m.external_forces_manual = True
        	
                m.setNodesPosition()
       	        # set NodesPosition must be calle dbefore buildNodes!
     	    	#print("TEST")
                m.buildNodes()
       		m.external_forces_manual = True
        	m.external_forces_from_ns = True
        	m.setApplyDrag(True)
        	m.setApplyBuoyancy(True)
        	m.setApplyAddedMass(True)
        	m.setFluidDensityAtNodes(np.array([rho_0 for i in range(m.nodes_nb)]))
        	m.setDragCoefficients(tangential=1.15, normal=0.213, segment_nb=0)
        	m.setAddedMassCoefficients(tangential=0.269, normal=0.865, segment_nb=0)
        	# small Iyy for bending
        	m.setIyy(1e-20, 0)
        	m.attachBackNodeToBody(body)

        	#m.attachFrontNodeToBody(body2)
        	m.fixFrontNode('fixed')

                etas = np.array([-0.5, 0., 0.5, 1.])  # etas to record strain
        	m.recordStrainEta(etas)
                

            # seabed contact
    	    pos1 = m1.getNodesPosition()
    	    pos2 = m2.getNodesPosition()
            Efloor = 2e4
	    material = pc.ChMaterialSurfaceSMC()
	    #material.SetYoungModulus(Efloor)
	    material.SetKn(300e6)  # normal stiffness
	    material.SetGn(1.)  # normal damping coefficient
	    material.SetFriction(0.3)
	    material.SetRestitution(0.2)
	    material.SetAdhesion(0)
	    m1.setContactMaterial(material)
	    m2.setContactMaterial(material)
	    # build floor
	    vec = pc.ChVectorD(0., -0.1, 0.)
	    box_dim = [10.,10.,0.2]
	    box = pc.ChBodyEasyBox(box_dim[0], box_dim[1], box_dim[2], 1000, True)
	    box.SetPos(vec)
	    box.SetMaterialSurface(material)
	    box.SetBodyFixed(True)
	    system.ChSystem.Add(box)

            ## Set Boundary Flags for contact bodies
            #body2.setBoundaryFlags(np.array([1]))
            

    for bc in caisson.BC_list:
        if opts.caisson_BC == 'noslip':
            bc.setNoSlip()
        if opts.caisson_BC == 'freeslip':
            bc.setFreeSlip()
    
    def prescribed_motion(t):
        new_x = np.array(caisson_coords)
        new_x[1] = caisson_coords[1]+0.01*cos(2*np.pi*(t/4)+np.pi/2)
        return new_x

# ----- SHAPES ----- #
tank = st.Tank2D(domain, tank_dim)

# Generation / Absorption zones
tank.setSponge(x_n=tank_sponge[0], x_p=tank_sponge[1])
omega = 2*np.pi/period
dragAlpha = 5.*omega/1e-6
smoothing = 3.*opts.he

tank.setGenerationZones(x_n=True, waves=wave, dragAlpha=dragAlpha, smoothing = smoothing)
tank.setAbsorptionZones(x_p=True, dragAlpha = dragAlpha)

if opts.caisson:
        tank.setChildShape(caisson, 0)
    
# ----- FORCED OSCILLATION ----- #

if opts.forced_oscillation:
    amp = opts.forced_amp
    freq = opts.forced_freq
    #body.setPrescribedMotionSine(amp, freq)    #Acts in x direction
    
    omega = (9.81*freq/0.18)**0.5          #Convert Normalised Frequency to actual frequency
    
    #Manual
    T=opts.T
    dt = 0.01 
    t_vec = np.arange(0., T, dt)
    t_vec = np.append(t_vec,T) 
    y_vec = amp*np.sin((omega)*t_vec)
    body.setPrescribedMotionCustom(t=t_vec, y=y_vec, t_max=T)
    

# ----- BOUNDARY CONDITIONS ----- #

tank.BC['x-'].setFreeSlip()    #setUnsteadyTwoPhaseVelocityInlet(wave, smoothing=smoothing, vert_axis=1)
tank.BC['y+'].setAtmosphere()
tank.BC['y-'].setFreeSlip()
tank.BC['x+'].setFreeSlip()
tank.BC['sponge'].setNonMaterial()

tank.BC['x-'].setFixedNodes()
tank.BC['x+'].setFixedNodes()
tank.BC['sponge'].setFixedNodes()
tank.BC['y+'].setTank()  # sliding mesh nodes
tank.BC['y-'].setTank()  # sliding mesh nodes

# ----- GAUGES ----- #
"""
GAUGES NOT WORKING WITH MOVING MESH
"""

# ----- MESHING -----#


domain.MeshOptions.he = opts.he
domain.use_gmsh = opts.use_gmsh
domain.MeshOptions.use_gmsh = opts.use_gmsh
domain.MeshOptions.genMesh = opts.genMesh
mesh_fileprefix = 'meshgeo_'+str(wavelength)+'_'+str(opts.he)+str(opts.he_caisson)+'_'+str(opts.he_free_surface,)
mesh_fileprefix = mesh_fileprefix.replace(' ', '')
mesh_fileprefix = mesh_fileprefix.replace('(', '')
mesh_fileprefix = mesh_fileprefix.replace(')', '')
mesh_fileprefix = mesh_fileprefix.replace('[', '')
mesh_fileprefix = mesh_fileprefix.replace(']', '')
mesh_fileprefix = mesh_fileprefix.replace('.', '-')
mesh_fileprefix = mesh_fileprefix.replace(',', '_')
domain.MeshOptions.setOutputFiles(name=mesh_fileprefix)
if opts.genMesh is False:
    domain.geofile = mesh_fileprefix 

# ASSEMBLE DOMAIN
st.assembleDomain(domain)

# MESH REFINEMENT

he = opts.he
if opts.refinement is True:
    from py2gmsh import (Mesh, Entity, Field)
    from py2gmsh import geometry2mesh
    my_mesh = geometry2mesh(domain) 
    grading = np.sqrt(opts.refinement_grading*4./np.sqrt(3.))/np.sqrt(1.*4./np.sqrt(3))
    he = opts.he
    he_max = opts.he_max
    he_max_water = opts.he_max_water
    he_caisson = opts.he_caisson
    he_free_surface = opts.he_free_surface

    field_list = []
    
    #Domain
#    P1 = Entity.Point([-tank_sponge[0], tank_dim[1], 0.],mesh=my_mesh)
#    P2 = Entity.Point([-tank_sponge[0], -tank_dim[1], 0.], mesh=my_mesh)
#    P3 = Entity.Point([tank_dim[0]+tank_sponge[1], -tank_dim[1], 0.], mesh=my_mesh)
#    P4 = Entity.Point([tank_dim[0]+tank_sponge[1], tank_dim[1], 0.], mesh=my_mesh)
#    
#    L1 = Entity.Line([P1,P2],mesh=my_mesh)
#    L2 = Entity.Line([P2,P3],mesh=my_mesh)
#    L3 = Entity.Line([P3,P4],mesh=my_mesh)
#    L4 = Entity.Line([P4,P1],mesh=my_mesh)
#
#    LL1 = Entity.LineLoop([L1, L2, L3, L4], mesh=my_mesh)
#    S1 = Entity.PlaneSurface([LL1], mesh=my_mesh)
#
    #F1 = Field.MathEval(mesh=my_mesh)
    #F1.F = '({he})'.format(he=he)
    #
    #field_list += [F1]
    
    #About Free Surface
    p1 = Entity.Point([-tank_sponge[0]            ,tank_dim[1]/2.+opts.refinement_freesurface, 0.],mesh=my_mesh)
    p2 = Entity.Point([-tank_sponge[0]            ,tank_dim[1]/2.-opts.refinement_freesurface, 0.], mesh=my_mesh)
    p3 = Entity.Point([tank_dim[0]+tank_sponge[1] ,tank_dim[1]/2.-opts.refinement_freesurface, 0.], mesh=my_mesh)
    p4 = Entity.Point([tank_dim[0]+tank_sponge[1] ,tank_dim[1]/2.+opts.refinement_freesurface, 0.], mesh=my_mesh)
    
    l1 = Entity.Line([p1,p2],mesh=my_mesh)
    l2 = Entity.Line([p2,p3],mesh=my_mesh)
    l3 = Entity.Line([p3,p4],mesh=my_mesh)
    l4 = Entity.Line([p4,p1],mesh=my_mesh)

    ll1 = Entity.LineLoop([l1, l2, l3, l4], mesh=my_mesh)
    s1 = Entity.PlaneSurface([ll1], mesh=my_mesh)

    f1 = Field.MathEval(mesh=my_mesh)
    f1.F = '((abs(y-{waterLevel})*({grading}-1))+{he_free_surface})/{grading}'.format(waterLevel=waterLevel, grading=grading, he_free_surface=he_free_surface)
    field_list += [f1]
    
    #About Caisson
    #Aiming for condensed mesh one caisson width either side. 
    p5 = Entity.Point([-1.5*dim[0]+tank_dim[0]/2.,  1.5*dim[1]+tank_dim[1]/2., 0.],mesh=my_mesh)
    p6 = Entity.Point([-1.5*dim[0]+tank_dim[0]/2., -1.5*dim[1]+tank_dim[1]/2., 0.],mesh=my_mesh)
    p7 = Entity.Point([ 1.5*dim[0]+tank_dim[0]/2., -1.5*dim[1]+tank_dim[1]/2., 0.],mesh=my_mesh)
    p8 = Entity.Point([ 1.5*dim[0]+tank_dim[0]/2.,  1.5*dim[1]+tank_dim[1]/2., 0.],mesh=my_mesh)
    
    l5 = Entity.Line([p5,p6],mesh=my_mesh)
    l6 = Entity.Line([p6,p7],mesh=my_mesh)
    l7 = Entity.Line([p7,p8],mesh=my_mesh)
    l8 = Entity.Line([p8,p5],mesh=my_mesh)

    f2 = Field.MathEval(mesh=my_mesh)
    f2.F = '(abs(x-{halftankdim})*({grading}-1)+{he_caisson})/{grading}'.format(halftankdim=tank_dim[0]/2, grading=grading, he_caisson=he_caisson)
    field_list += [f2]
     
    # background field
    fmin = Field.Min(mesh=my_mesh)
    fmin.FieldsList = field_list
    my_mesh.setBackgroundField(fmin)

    # max element size
    my_mesh.Options.Mesh.CharacteristicLengthMax = he_max
    my_mesh.Coherence = True
    my_mesh.writeGeo(mesh_fileprefix+'.geo')

### Added Mass ###
if opts.caisson:
    if opts.addedMass is True:
        # passed in added_mass_p.py coefficients
         max_flag = 0 
         max_flag = int(max(domain.vertexFlags))    
         max_flag = int(max(domain.segmentFlags+[max_flag]))
         max_flag = int(max(domain.facetFlags+[max_flag]))
         print type(max_flag)
         flags_rigidbody = np.zeros(max_flag+1, dtype='int32')
         for s in system.subcomponents:
             if type(s) is fsi.ProtChBody:
		if s.boundaryFlags is not None:
                    #print("FILLER")
                    for i in s.boundaryFlags:
                        flags_rigidbody[i] = 1




##########################################
# Numerical Options and other parameters #
##########################################


rho_0=998.2
nu_0 =1.004e-6
rho_1=1.205
nu_1 =1.500e-5
sigma_01=0.0
g = [0., -9.81]




from math import *
from proteus import MeshTools, AuxiliaryVariables
import numpy
import proteus.MeshTools
from proteus import Domain
from proteus.Profiling import logEvent
from proteus.default_n import *
from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.ctransportCoefficients import smoothedHeaviside_integral


#----------------------------------------------------
# Boundary conditions and other flags
#----------------------------------------------------
movingDomain=opts.movingDomain
checkMass=False
applyCorrection=True
applyRedistancing=True
freezeLevelSet=True

#----------------------------------------------------
# Time stepping and velocity
#----------------------------------------------------
weak_bc_penalty_constant = opts.weak_factor/nu_0#Re
dt_init = opts.dt_init
T = opts.T
nDTout = int(opts.T*opts.nsave)
timeIntegration = opts.timeIntegration
if nDTout > 0:
    dt_out= (T-dt_init)/nDTout
else:
    dt_out = 0
runCFL = opts.cfl
dt_fixed = opts.dt_fixed

#----------------------------------------------------

#  Discretization -- input options
useOldPETSc=False
useSuperlu = not True
spaceOrder = 1
useHex     = False
useRBLES   = 0.0
useMetrics = 1.0
useVF = 1.0
useOnlyVF = False
useRANS = opts.useRANS # 0 -- None
            # 1 -- K-Epsilon
            # 2 -- K-Omega, 1998
            # 3 -- K-Omega, 1988
# Input checks
if spaceOrder not in [1,2]:
    print "INVALID: spaceOrder" + spaceOrder
    sys.exit()

if useRBLES not in [0.0, 1.0]:
    print "INVALID: useRBLES" + useRBLES
    sys.exit()

if useMetrics not in [0.0, 1.0]:
    print "INVALID: useMetrics"
    sys.exit()

#  Discretization
nd = 2
if spaceOrder == 1:
    hFactor=1.0
    if useHex:
	 basis=C0_AffineLinearOnCubeWithNodalBasis
         elementQuadrature = CubeGaussQuadrature(nd,3)
         elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,3)
    else:
    	 basis=C0_AffineLinearOnSimplexWithNodalBasis
         elementQuadrature = SimplexGaussQuadrature(nd,3)
         elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,3)
         #elementBoundaryQuadrature = SimplexLobattoQuadrature(nd-1,1)
elif spaceOrder == 2:
    hFactor=0.5
    if useHex:
	basis=C0_AffineLagrangeOnCubeWithNodalBasis
        elementQuadrature = CubeGaussQuadrature(nd,4)
        elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,4)
    else:
	basis=C0_AffineQuadraticOnSimplexWithNodalBasis
        elementQuadrature = SimplexGaussQuadrature(nd,4)
        elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,4)


# Numerical parameters
if opts.sc == 0.25:
    sc = 0.25 # default: 0.5. Test: 0.25
    sc_beta = 1. # default: 1.5. Test: 1.
    epsFact_consrv_diffusion = 0.1 # default: 1.0. Test: 0.1. Safe: 10.
elif opts.sc == 0.5:
    sc = 0.5
    sc_beta = 1.5
    epsFact_consrv_diffusion = 10.0 # default: 1.0. Test: 0.1. Safe: 10.
else:
    import sys
    sys.quit()
ns_forceStrongDirichlet = opts.strong_dir
backgroundDiffusionFactor=0.01
if useMetrics:
    ns_shockCapturingFactor  = sc
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = sc
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = sc_beta
    vof_shockCapturingFactor = sc
    vof_lag_shockCapturing = True
    vof_sc_uref = 1.0
    vof_sc_beta = sc_beta
    rd_shockCapturingFactor  =sc
    rd_lag_shockCapturing = False
    epsFact_density    = 3.
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 0.33
    epsFact_consrv_diffusion = epsFact_consrv_diffusion
    redist_Newton = True#False
    kappa_shockCapturingFactor = sc
    kappa_lag_shockCapturing = False#True
    kappa_sc_uref = 1.0
    kappa_sc_beta = sc_beta
    dissipation_shockCapturingFactor = sc
    dissipation_lag_shockCapturing = False#True
    dissipation_sc_uref = 1.0
    dissipation_sc_beta = sc_beta
else:
    ns_shockCapturingFactor  = 0.9
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = 0.9
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = 1.0
    vof_shockCapturingFactor = 0.9
    vof_lag_shockCapturing = True
    vof_sc_uref  = 1.0
    vof_sc_beta  = 1.0
    rd_shockCapturingFactor  = 0.9
    rd_lag_shockCapturing = False
    epsFact_density    = 1.5
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 0.33
    epsFact_consrv_diffusion = 10.0
    redist_Newton = False#True
    kappa_shockCapturingFactor = 0.9
    kappa_lag_shockCapturing = True#False
    kappa_sc_uref  = 1.0
    kappa_sc_beta  = 1.0
    dissipation_shockCapturingFactor = 0.9
    dissipation_lag_shockCapturing = True#False
    dissipation_sc_uref  = 1.0
    dissipation_sc_beta  = 1.0

tolfac = 0.001
mesh_tol = 0.001
ns_nl_atol_res = max(1.0e-8,tolfac*he**2)
vof_nl_atol_res = max(1.0e-8,tolfac*he**2)
ls_nl_atol_res = max(1.0e-8,tolfac*he**2)
mcorr_nl_atol_res = max(1.0e-8,0.1*tolfac*he**2)
rd_nl_atol_res = max(1.0e-8,tolfac*he)
kappa_nl_atol_res = max(1.0e-8,tolfac*he**2)
dissipation_nl_atol_res = max(1.0e-8,tolfac*he**2)
mesh_nl_atol_res = max(1.0e-8,mesh_tol*he**2)

#turbulence
ns_closure=0 #1-classic smagorinsky, 2-dynamic smagorinsky, 3 -- k-epsilon, 4 -- k-omega

if useRANS == 1:
    ns_closure = 3
elif useRANS >= 2:
    ns_closure == 4

def twpflowPressure_init(x, t):
    p_L = 0.0
    phi_L = tank_dim[nd-1] - waterLevel
    phi = x[nd-1] - waterLevel
    return p_L -g[nd-1]*(rho_0*(phi_L - phi)+(rho_1 -rho_0)*(smoothedHeaviside_integral(epsFact_consrv_heaviside*opts.he,phi_L)
                                                         -smoothedHeaviside_integral(epsFact_consrv_heaviside*opts.he,phi)))
