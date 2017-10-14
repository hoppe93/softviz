# SOFT SyntheticImage PLOT CLASS
#
# This class is a simple interface for plotting SOFT images
# with overlays etc. using Python's matplotlib.
#

import h5py
import matplotlib.pyplot as plt
import numpy as np
import scipy
from matplotlib.colors import LinearSegmentedColormap

class SyntheticImage:
    
    def __init__(self, figure=None, canvas=None, registerGeriMap=True):
        # PROPERTIES
        self.canvas = canvas
        self.captions = []
        self.colorbar = False
        self.colorbarRelative = True
        self.colormapName = 'GeriMap'
        self.detectorDirection = None
        self.detectorPosition = None
        self.detectorVisang = None
        self.figure = figure
        self.imageData = None
        self.imageIntensityMax = 1      # Ceiling of colormap
        self.logarithmic = False
        self.overlays = {
            'wall': False,
            'separatrix': False,
            'flux': False,
            'topview': False,
            'tokamak': []
        }
        self.separatrix = None
        self.wall = None
        self.wall_rmax = None
        self.wall_rmin = None

        # Internal properties
        self._colorbar = None
        self._fluxOverlayHandles = []   # Matplotlib handles to flux overlays
        self._imageMax = 0              # Max intensity of image
        self._separatrixOverlayHandle = None
        self._wallOverlayHandle = None

        if self.figure is None:
            self.figure = Figure(facecolor='black')
            if self.canvas is not None:
                raise ValueError("Canvas set, but no figure given. If no figure is given, no canvas may be given.")
        if self.canvas is None:
            self.canvas = FigureCanvas(self.figure)

        self.axes = None

        if registerGeriMap:
            SyntheticImage.registerGeriMap()

    #####################################################
    #
    # GETTERS
    #
    #####################################################
    def hasImage(self): return self.imageData is not None
    def getImageMax(self): return self._imageMax

    #####################################################
    #
    # SETTERS
    #
    #####################################################
    def setCaptions(self, captions): self.captions = captions
    def setColormap(self, cmname): self.colormapName = cmname
    def setDetector(self, direction, position, visionangle): self.detectorDirection, self.detectorPosition, self.detectorVisang = direction, position, visionangle
    def setFluxSurfaces(self, flux): self.flux = flux
    def setImage(self, image): self.imageData = image
    def setOverlays(self, overlays): self.overlays = overlays
    def setSeparatrix(self, separatrix): self.separatrix = separatrix
    def setWall(self, wall): self.wall, self.wall_rmax, self.wall_rmin = wall, np.amax(wall[0,:]), np.amin(wall[0,:])

    def toggleColorbar(self, hasColorbar): self.colorbar = hasColorbar
    def toggleColorbarRelative(self, hasColorbarRelative): self.colorbarRelative = hasColorbarRelative
    def toggleLogarithmic(self, log): self.logarithmic = log

    #####################################################
    #
    # PUBLIC METHODS
    #
    #####################################################
    def assembleImage(self):
        """
        Plot a SOFT image, applying all settings
        given to this SyntheticImage object. This means
        any overlays, colorbars and captions will be plotted.
        """
        self.clearImage()
        self.axes = self.figure.add_subplot(111)

        # Plot image
        self.plotImage()

        # Plot overlays
        self.plotOverlays()

        # Add colorbar
        if self.colorbar:
            self.plotColorbar()

        # Add captions
        self.plotCaptions()

    def changeIntensity(self, maxIntensity, relative=False):
        """
        Change the intensity of an already plotted image
        """
        if self._image is None:
            raise ValueError("No image has been plotted, so there is no image to change intensity for.")

        if relative:
            self.imageIntensityMax = maxIntensity
        else:
            if self._imageMax > 0:
                self.imageIntensityMax = maxIntensity / self._imageMax
            else:
                self.imageIntensityMax = 1

        intmax = self.imageIntensityMax * self._imageMax

        zerolevel = 0
        if self.logarithmic:
            intmax = np.log10(intmax)
            zerolevel = intmax - 40

        self._image.set_clim(vmin=zerolevel, vmax=intmax)
        #self.canvas.draw_idle()

    def loadImageFile(self, filename):
        """
        Load a SOFT image file.

        filename: Name of file to load.
        """
        # DAT-file: for legacy support
        if filename.endswith('.dat') or filename.endswith('.topview'):
            self.imageData = np.genfromtxt(filename)
        elif filename.endswith('.mat'):
            # First, try to load old-style MAT file
            try:
                matfile = scipy.io.loadmat(filename)

                self.imageData = np.transpose(matfile['image'])
                self.detectorPosition = matfile['detectorPosition'][0]
                self.detectorDirection = matfile['detectorDirection'][0]
                self.detectorVisang = matfile['detectorVisang'][0]
                self.wall = matfile['wall']
            # Otherwise, load modern (HDF5-based) MAT-file
            except NotImplementedError:
                matfile = h5py.File(filename)

                self.imageData = np.transpose(matfile['image'][:,:])
                self.detectorPosition = matfile['detectorPosition'][:,0]
                self.detectorDirection = matfile['detectorDirection'][:,0]
                self.detectorVisang = matfile['detectorVisang'][0,0]
                self.wall = matfile['wall'][:,:]

            self.wall_rmax = np.amax(self.wall[0,:])
            self.wall_rmin = np.amin(self.wall[0,:])
        else:
            raise NotImplementedError("Unrecognized image format. Unable to load file.")

        self._imageMax = np.amax(self.imageData)
        self._intmax = self._imageMax

    @staticmethod
    def registerGeriMap():
        """
        Register the perceptually uniform colormap 'GeriMap' with matplotlib
        """
        gm = [(0, 0, 0), (.15, .15, .5), (.3, .15, .75),
              (.6, .2, .50), (1, .25, .15), (.9, .5, 0),
              (.9, .75, .1), (.9, .9, .5), (1, 1, 1)]
        gerimap = LinearSegmentedColormap.from_list('GeriMap', gm)
        gerimap_r = LinearSegmentedColormap.from_list('GeriMap_r', gm[::-1])
        plt.register_cmap(cmap=gerimap)
        plt.register_cmap(cmap=gerimap_r)

    def savePlot(self, filename):
        pass

    def update(self):
        self.canvas.draw()

    #####################################################
    #
    # SEMI-PUBLIC PLOT ROUTINES
    #
    #####################################################
    def clearImage(self):
        self.figure.clear()

        # Reset plot handles
        self._colorbar = None
        self._fluxOverlayHandles = []
        self._separatrixOverlayHandle = None
        self._wallOverlayHandle = None

    def plotCaptions(self):
        for i in range(0, len(self.axes.texts)):
            self.axes.texts.remove(self.axes.texts[0])

        for item in self.captions:
            X, Y = float(item[0]), float(item[1])
            fontsize = int(item[2])
            caption = item[3]

            self.axes.text(X, Y, caption, color='white', fontsize=fontsize)

    def plotColorbar(self):
        """
        Add a colorbar to the axes 'ax' of figure 'fig'.
        Respects the 'colorbarRelative' setting and uses percentage
        ticks if 'colorbarRelative' is True.
        """
        self.removeColorbar()

        if self.colorbarRelative:
            mx = self.imageIntensityMax * self._imageMax
            self._colorbar = self.figure.colorbar(self._image, shrink=0.8, ticks=[0,mx*0.2,mx*0.4,mx*0.6,mx*0.8,mx])
            self._colorbar.ax.set_yticklabels(['0%','20%','40%','60%','80%','100%'])
        else:
            self._colorbar = self.figure.colorbar(self._image, shrink=0.8)
        self._colorbar.ax.tick_params(labelcolor='white', color='white')

    def removeColorbar(self):
        """
        Removes any existing colorbar on the plot
        """
        if self._colorbar is not None:
            self._colorbar.remove()
            self._colorbar = None

    def plotImage(self):
        """
        Plots the current SOFT image with the colormap whose
        name is specified in 'colormapName'. Proper extents of
        the image are computed and applied.
        """
        # Get colormap
        colormap = plt.get_cmap(self.colormapName)

        # Get the image (linear or logarithmized)
        imageData, intmin, intmax = self._getImageData()

        # Compute image extent
        extent = self._getImageExtent()

        # Plot image
        self._image = self.axes.imshow(imageData, origin='lower', cmap=colormap,
                          interpolation=None, clim=(intmin, intmax),
                          extent=extent)
        self.axes.set_axis_off()

    def plotOverlays(self):
        """
        Plot wall/equilibrium overlays as specified in
        the 'overlays' list.
        """
        if self.overlays['wall'] and self.wall is not None:
            plotOrthogonalCrossSection(self.axes, self.wall, self.detectorPosition, self.detectorDirection, linewidth=1)
        elif self._wallOverlayHandle is not None:
            self._wallOverlayHandle.remove()
            self._wallOverlayHandle = None

        if self.overlays['separatrix'] and self.separatrix is not None:
            plotCrossSection(self.axes, self.wall, self.detectorDirection)
        elif self._separatrixOverlayHandle is not None:
            self._separatrixOverlayHandle.remove()
            self._separatrixOverlayHandle = None

        """
        if self.vesselStatus['flux']:
            plotCrossSection(self.axes, self.wall, self.detectorDirection)
        elif len(self._fluxOverlayHandles) > 0:
            for fh in self._fluxOverlayHandles:
                fh.remove()
            self._fluxOverlayHandles = []

        if self.vesselStatus['topview']:
            pass
        elif self._topviewOverlayHandles is not None:
            for th in self._topviewOverlayHandles:
                th.remove()
            self._topviewOverlayHandles = []
        """

    #####################################################
    #
    # INTERNAL ROUTINES
    #
    #####################################################
    def _getImageData(self):
        """
        Returns the appropriate image data to plot, as well as
        the appropriate color limits. If 'logarithmic' is NOT
        set, this is just 'image', 0 and 'imageIntensityMax'.
        Otherwise a logarithmized 'image' and 'imageIntensityMax'
        are returned,
        """
        img = self.imageData
        intmax = self.imageIntensityMax * self._imageMax
        zerolevel = 0

        if self.logarithmic:
            img = np.log10(img)
            intmax = np.log10(intmax)
            zerolevel = intmax - 40

            # Set all elements that are log10(0) = -inf or
            # at least below the "zero" level to "zero"
            img[np.where(img < zerolevel)] = zerolevel

        return img, zerolevel, intmax

    def _getImageExtent(self):
        """
        Compute the extent of the image (i.e. the physical size
        of the image in the plane at a unit distance from the camera).
        This is necessary for obtaining correct dimensions of overlays.
        """
        extent = np.array([-1,1,-1,1]) / 2
        
        if self.detectorVisang is not None:
            extent = extent * np.tan(self.detectorVisang/2)

        return extent

#########################################################
###
### ROUTINES FOR PLOTTING PROJECTIONS
###
#########################################################
def _limitwall(rc, zc, rlim, zuplim, zlowlim):
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

def _rotateWall(rc, zc, angle=0, cossin=[]):
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

def _transformWall(rc, yc, zc, cameraPosition, cameraDirection):
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
    nrc, nyc, nzc = _rotateWall(rc, zc, cossin=cossin)
    return plotCrossSection(ax, nrc, nyc, nzc, cameraPosition, cameraDirection, plotstyle, linewidth)

def plotwall(ax, wall, cameraPosition, cameraDirection, plotstyle='w',
             degreesStart=[0], degreesEnd=[360], spacing=1, linewidth=0.1,
             rlim=0, zuplim=0, zlowlim=0, rmin=-1, rmax=1, zmin=-1, zmax=1):
    """ Plot the wall. Allows setting limits on which parts to plot, and
        plot several parts of the wall simultaneously. """
    rc = wall[:,0]
    zc = wall[:,1]

    # Limit the wall to only inner parts
    rc, zc = _limitwall(rc, zc, rlim, zuplim, zlowlim)

    handles = []
    for i in range(len(degreesStart)):
        for degree in range(degreesStart[i], degreesEnd[i], spacing):
            # [1] ROTATE WALL SECTION AROUND ORIGO
            nrc, nyc, nzc = _rotateWall(rc, zc, angle=degree)

            # [2] ROTATE, TRANSLATE AND PLOT WALL SECTION AROUND CAMERA
            h = plotCrossSection(ax, nrc, nyc, nzc, cameraPosition, cameraDirection, plotstyle, linewidth)
            handles.append(h)

def plotCrossSection(ax, rc, yc, zc, cameraPosition, cameraDirection, plotstyle='w', linewidth=0.1):
    """ Plot a wall cross-section (that is rotated to some toroidal angle in the
        tokamak coordinate system before this function is called) """
    n = len(rc)

    # Rotate and translate wall section
    nrc, nyc, nzc = _transformWall(rc, yc, zc, cameraPosition, cameraDirection)
    wallVector = [nrc, nzc, nyc, np.ones((1,n))[0]]

    # Apply camera matrix
    cameraMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0]])
    projectedVector = np.dot(cameraMatrix, wallVector)
    factor = np.divide(1, wallVector[2])
    factorMatrix = np.array([factor,factor,factor])
    projectedVector = factorMatrix * projectedVector

    h, = ax.plot(projectedVector[0,:], projectedVector[1,:], plotstyle, linewidth=linewidth)
    return h
    