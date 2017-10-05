# Plot wall

import numpy as np

def limitwall(rc, zc, rlim, zuplim, zlowlim):
    """ Sort out the segments that are within radial
        bound 'rlim' and z interval [zlowlim, zuplim] """
    nrc, nzc = np.array([]), np.array([])
    for i in range(len(rc)):
        if rlim <= 0 or rc[i] < rlim:
            if zuplim != 0 and zc[i] > zuplim: continue
            if zlowlim != 0 and zc[i] < zlowlim: continue

            nrc = np.append(nrc, rc[i])
            nzc = np.append(nzc, zc[i])

    return nrc, nzc

def rotateWall(rc, zc, angle=0, cossin=[]):
    """ Rotate wall section around the symmetry axis """
    nrc, nyc, nzc = rc, rc, zc
    if len(cossin) == 2:
        nrc = rc * cossin[0]
        nyc =-rc * cossin[1]
        nzc = zc
    else:
        radAngle = angle * np.pi / 180
        nrc = rc * np.cos(radAngle)
        nyc =-rc * np.sin(radAngle)
        nzc = zc

    return nrc, nyc, nzc

def transformWall(rc, yc, zc, cameraPosition, cameraDirection):
    """ Transform wall section (rotate and translate) so that
        it matches the camera setup """
    # [1] COMPUTE ROTATION MATRIX
    y = [0,1,0]
    v = np.cross(cameraDirection, y)
    c = np.dot(cameraDirection, y)

    vmat = [[0,-v[2],v[1]], [v[2],0,-v[0]], [-v[1],v[0],0]]
    R = np.add(np.identity(3), vmat)
    vmat2 = np.dot(vmat, vmat) * 1 / (1+c)
    R = np.add(R, vmat2)

    nrc = np.subtract(rc, cameraPosition[0])
    nyc = np.subtract(yc, cameraPosition[1])
    nzc = np.subtract(zc, cameraPosition[2])

    wallVector = np.dot(R, [nrc,nyc,nzc])

    return wallVector[0,:], wallVector[1,:], wallVector[2,:]

def plotOrthogonalCrossSection(ax, wall, cameraPosition, cameraDirection, plotstyle='w', linewidth=0.1):
    """ Plot the wall cross section that us orthogonal to the camera's viewing direction """
    rc = wall[:,0]
    zc = wall[:,1]

    cossin = [np.dot(cameraDirection, [0,1,0]), np.dot(cameraDirection, [1,0,0])]
    nrc, nyc, nzc = rotateWall(rc, zc, cossin=cossin)
    #nrc, nyc, nzc = rotateWall(rc, zc, angle=0)
    plotCrossSection(ax, nrc, nyc, nzc, cameraPosition, cameraDirection, plotstyle, linewidth)

def plotwall(ax, wall, cameraPosition, cameraDirection, plotstyle='w',
             degreesStart=[0], degreesEnd=[360], spacing=1, linewidth=0.1,
             rlim=0, zuplim=0, zlowlim=0, rmin=-1, rmax=1, zmin=-1, zmax=1):
    """ Plot the wall. Allows setting limits on which parts to plot, and
        plot several parts of the wall simultaneously. """
    rc = wall[:,0]
    zc = wall[:,1]

    # Limit the wall to only inner parts
    rc, zc = limitwall(rc, zc, rlim, zuplim, zlowlim)

    for i in range(len(degreesStart)):
        for degree in range(degreesStart[i], degreesEnd[i], spacing):
            # [1] ROTATE WALL SECTION AROUND ORIGO
            nrc, nyc, nzc = rotateWall(rc, zc, angle=degree)

            # [2] ROTATE, TRANSLATE AND PLOT WALL SECTION AROUND CAMERA
            plotCrossSection(ax, nrc, nyc, nzc, cameraPosition, cameraDirection, plotstyle, linewidth)

    #plt.axis([rmin,rmax,zmin,zmax])
    #plt.show()

def plotCrossSection(ax, rc, yc, zc, cameraPosition, cameraDirection, plotstyle='w', linewidth=0.1):
    """ Plot a wall cross-section (that is rotated to some toroidal angle in the
        tokamak coordinate system before this function is called) """
    n = len(rc)

    # Rotate and translate wall section
    nrc, nyc, nzc = transformWall(rc, yc, zc, cameraPosition, cameraDirection)
    wallVector = [nrc, nzc, nyc, np.ones((1,n))[0]]

    # Apply camera matrix
    cameraMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0]])
    projectedVector = np.dot(cameraMatrix, wallVector)
    factor = np.divide(1, wallVector[2])
    factorMatrix = np.array([factor,factor,factor])
    projectedVector = factorMatrix * projectedVector

    ax.plot(projectedVector[0,:], projectedVector[1,:], plotstyle, linewidth=linewidth)
    
#plotwall('../resources/C-Mod/C-Mod-wall.wall_2d', [0,-1.069,-0.20655], [-0.05931,0.99824,0])
