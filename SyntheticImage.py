# SOFT SyntheticImage PLOT CLASS
#
# This class is a simple interface for plotting SOFT images
# with overlays etc. using Python's matplotlib.
#

import h5py
import matplotlib.pyplot as plt
import numpy as np
import scipy.io
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker
from PolarizedImage import ImageType, PolarizedImage

class SyntheticImage:
    
    def __init__(self, figure=None, canvas=None, registerGeriMap=True, gerimapTransparencyThreshold=None):
        # PROPERTIES
        self.canvas = canvas
        self.captions = []
        self.colorbar = False
        self.colorbarRelative = True
        self.colormapName = 'GeriMap'
        self.detectorDirection = None
        self.detectorPosition = None
        self.detectorVisang = None
        self.detectorRoll = 0
        self.figure = figure
        #self.flux = {'R': [], 'Z': [], 'lengths': [], 'radii': []}
        self.flux = None
        self.maskLevel = None
        self.overlayWallCrossSection = False# Show wall cross-section overlay?
        self.overlaySeparatrix = False      # Show separatrix overlay?
        self.overlayDetectorNormal = False
        self.overlayFluxSurfaces = False     # Show flux surface overlay?
        self.overlayTopview = False         # Show topview overlay?
        self.overlayTopviewSeparatrix = False
        self.overlayTopviewOrthogonalCrossSection  = False
        self.imageData = None
        self.imageIntensityMax = 1      # Ceiling of colormap
        self.logarithmic = False
        self.separatrix = None
        self.wall = None
        self.wall_rmax = None
        self.wall_rmin = None

        # Internal properties
        self._colorbar = None
        self._detectorNormalHandle = None
        self._fluxOverlayHandles = []   # Matplotlib handles to flux overlays
        self._imageMax = 0              # Max intensity of image
        self._separatrixOverlayHandle = None
        self._topviewOCSHandle = None
        self._topviewOverlayHandles = None
        self._topviewSeparatrixOverlayHandles = None
        self._wallCrossSectionOverlayHandle = None

        if self.figure is None:
            self.figure = plt.gca().figure
            self.figure.patch.set_facecolor('black')
            if self.canvas is not None:
                raise ValueError("Canvas set, but no figure given. If no figure is given, no canvas may be given.")
        if self.canvas is None:
            self.canvas = self.figure.canvas

        self.axes = None

        if registerGeriMap:
            SyntheticImage.registerGeriMap(transparencyThreshold=gerimapTransparencyThreshold)

    #####################################################
    #
    # GETTERS
    #
    #####################################################
    def getImageMax(self): return self._imageMax
    def hasImage(self): return self.imageData is not None
    def hasSeparatrix(self): return self.separatrix is not None
    def hasTopview(self): return self.hasWall()
    def hasWall(self): return self.wall is not None

    #####################################################
    #
    # SETTERS
    #
    #####################################################
    def setCaptions(self, captions): self.captions = captions
    def setColormap(self, cmname): self.colormapName = cmname
    def setDetector(self, direction, position, visionangle, roll=0): self.detectorDirection, self.detectorPosition, self.detectorVisang, self.detectorRoll = direction, position, visionangle, roll
    def setFluxSurfaces(self, flux): self.flux = flux
    def setImage(self, image): self.imageData = image
    def setMaskLevel(self, level=None): self.maskLevel = level
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

    def limitExtents(self):
        extent = self._getImageExtent()
        self.axes.set_xlim(extent[0], extent[1])
        self.axes.set_ylim(extent[2], extent[3])

    def loadImageFile(self, filename, imgtype=ImageType.I):
        """
        Load a SOFT image file.

        filename: Name of file to load.
        imgtype:  Type of image to load (applicable only to
                  polarized images)
        """
        # DAT-file: for legacy support
        if filename.endswith('.dat') or filename.endswith('.topview'):
            self.imageData = np.genfromtxt(filename)
        elif filename.endswith('.mat'):
            # First, try to load old-style MAT file
            try:
                matfile = scipy.io.loadmat(filename)

                if 'image' in matfile:
                    self.imageData = np.transpose(matfile['image'])
                elif 'StokesI' in matfile:
                    I = np.transpose(matfile['StokesI'])
                    Q = np.transpose(matfile['StokesQ'])
                    U = np.transpose(matfile['StokesU'])
                    V = np.transpose(matfile['StokesV'])

                    self.imageData, _, _ = PolarizedImage.getPolarizationQuantity(imgtype, I, Q, U, V)

                self.detectorPosition = matfile['detectorPosition'][0]
                self.detectorDirection = matfile['detectorDirection'][0]
                self.detectorVisang = matfile['detectorVisang'][0][0]

                try: self.detectorRoll = matfile['detectorRoll'][0][0]
                except KeyError: pass

                try:
                    self.wall = matfile['wall']
                    if self.wall.shape[0] == 2:
                        self.wall = np.transpose(self.wall)
                except KeyError: pass

                try: self.separatrix = matfile['separatrix']
                except KeyError: pass

            # Otherwise, load modern (HDF5-based) MAT-file
            except NotImplementedError:
                self._loadHDF5(filename, imgtype)

            self.wall_rmax = np.amax(self.wall[:,0])
            self.wall_rmin = np.amin(self.wall[:,0])
        elif filename.endswith('.h5') or filename.endswith('.hdf5'):
            self._loadHDF5(filename, imgtype)

            self.wall_rmax = np.amax(self.wall[:,0])
            self.wall_rmin = np.amin(self.wall[:,0])
        else:
            raise NotImplementedError("Unrecognized image format. Unable to load file.")

        self._imageMax = np.amax(self.imageData)
        self._intmax = self._imageMax

    def _loadHDF5(self, filename, imgtype=ImageType.I):
        matfile = h5py.File(filename, 'r')

        if 'image' in matfile:
            self.imageData = np.transpose(matfile['image'][:,:])
        elif 'StokesI' in matfile:
            I = np.transpose(matfile['StokesI'][:,:])
            Q = np.transpose(matfile['StokesQ'][:,:])
            U = np.transpose(matfile['StokesU'][:,:])
            V = np.transpose(matfile['StokesV'][:,:])

            self.imageData, _, _ = PolarizedImage.getPolarizationQuantity(imgtype, I, Q, U, V)

        self.detectorPosition = matfile['detectorPosition'][:]
        self.detectorDirection = matfile['detectorDirection'][:]

        if len(matfile['detectorVisang'].shape) == 2:
            self.detectorVisang = matfile['detectorVisang'][0,0]
        else:
            self.detectorVisang = matfile['detectorVisang'][0]

        try: self.detectorRoll = matfile['detectorRoll'][:][0]
        except KeyError: pass

        if len(self.detectorPosition.shape) == 2:
            if self.detectorPosition.shape[0] == 3:
                self.detectorPosition = self.detectorPosition.reshape((1,3))
            if self.detectorDirection.shape[0] == 3:
                self.detectorDirection = self.detectorDirection.reshape((1,3))

            self.detectorPosition = self.detectorPosition[0]
            self.detectorDirection = self.detectorDirection[0]

        try:
            self.wall = matfile['wall'][:,:]
            if self.wall.shape[0] == 2:
                self.wall = np.transpose(self.wall)
        except KeyError: pass

        try:
            self.separatrix = matfile['separatrix'][:,:]
            if self.separatrix.shape[0] == 2:
                self.separatrix = np.transpose(self.separatrix)
        except KeyError: pass

    @staticmethod
    def registerGeriMap(transparencyThreshold=0.4):
        """
        Register the perceptually uniform colormap 'GeriMap' with matplotlib

        transparencyThreshold: All intensities below this threshold will have
                               a non-zero alpha value (making them more or
                               less transparent). The opacity varies linearly,
                               being 1 at this value, and 0 at zero.
        """
        gm = [(0, 0, 0), (.15, .15, .5), (.3, .15, .75),
              (.6, .2, .50), (1, .25, .15), (.9, .5, 0),
              (.9, .75, .1), (.9, .9, .5), (1, 1, 1)]
        gerimap = LinearSegmentedColormap.from_list('GeriMap', gm)
        gerimap_r = LinearSegmentedColormap.from_list('GeriMap_r', gm[::-1])

        if transparencyThreshold is not None:
            n = int(gerimap.N * transparencyThreshold)
            nn = gerimap.N - n

            if n < 0 or nn < 0:
                raise ValueError('Transparency threshold must be a value between 0 and 1.')

            a = np.linspace(0, 1, n)
            b = np.ones((nn,))

            gmap = gerimap(np.arange(gerimap.N))
            gmap[:,-1] = np.concatenate((a,b), axis=None)
            gerimap = LinearSegmentedColormap.from_list('GeriMap', gmap)

            gmap_r = gerimap_r(np.arange(gerimap.N))
            gmap_r[:,-1] = np.concatenate((a,b), axis=None)
            gerimap_r = LinearSegmentedColormap.from_list('GeriMap_r', gmap_r)

        plt.register_cmap(cmap=gerimap)
        plt.register_cmap(cmap=gerimap_r)

    def savePlot(self, filename):
        #self.axes.margins(0,0)
        #self.axes.get_xaxis().set_visible(False)
        #self.axes.get_yaxis().set_visible(False)
        #self.axes.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
        #self.axes.get_yaxis().set_major_locator(matplotlib.ticker.NullLocator())
        self.axes.set_axis_off()
        self.figure.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        #self.axes.margins(0,0)
        self.axes.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
        self.axes.get_yaxis().set_major_locator(matplotlib.ticker.NullLocator())

        fcolor = self.figure.patch.get_facecolor()

        #self.canvas.print_figure(filename, bbox_inches='tight', pad_inches=0, facecolor='black')
        self.canvas.print_figure(filename, bbox_inches='tight', pad_inches=0, facecolor=fcolor, dpi=600)

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
        self._topviewOverlayHandles = None
        self._topviewSeparatrixOverlayHandles = None
        self._topviewOCSHandle = None
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
        self.colorbar = True

        if self.colorbarRelative:
            mx = self.imageIntensityMax * self._imageMax
            self._colorbar = self.figure.colorbar(self._image, shrink=0.8, ticks=[0,mx*0.2,mx*0.4,mx*0.6,mx*0.8,mx])
            self._colorbar.ax.set_yticklabels(['0%','20%','40%','60%','80%','100%'])
        else:
            mn = self._image.get_clim()[0]

            if mn < 0:
                mx = max(abs(mn), self._image.get_clim()[1])
                dm = 2*mx
                mn = -mx
                self._colorbar = self.figure.colorbar(self._image, shrink=0.8, ticks=[mn, mn+dm*0.2, mn+dm*0.4, mn+dm*0.6, mn+dm*0.8, mx])
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

        # Apply mask if requested
        zorder = 0
        if self.maskLevel is not None:
            imageData = np.ma.masked_where(imageData <= intmax*self.maskLevel, imageData)
            zorder = 10     # Put on top of everything

        # Compute image extent
        extent = self._getImageExtent()

        # Plot image
        #self._image = self.axes.imshow(imageData, origin='lower', cmap=colormap,
        self._image = self.axes.imshow(imageData, cmap=colormap,
                          interpolation=None, clim=(intmin, intmax),
                          extent=extent, zorder=zorder)
        self.axes.set_axis_off()

    def plotOverlays(self):
        """
        Plot wall/equilibrium overlays as specified in
        the 'overlays' list.
        """
        if self.overlayFluxSurfaces:
            self.plotFluxSurfaces()
        if self.overlaySeparatrix:
            self.plotSeparatrix()
        if self.overlayTopview:
            self.plotTopview()
        if self.overlayTopviewSeparatrix:
            self.plotTopviewSeparatrix()
        if self.overlayTopviewOrthogonalCrossSection:
            self.plotTopviewOrthogonalCrossSection()
        if self.overlayWallCrossSection:
            self.plotWallCrossSection()

    def plotDetectorNormal(self, color='w', arrowheadsize=1, arrowheadlength=1, arrowtaillength=1, linewidth=2):
        """
        Draw an arrow in the direction of the
        camera's viewing direction (camera plane
        normal) in the topview.
        """
        self.removeDetectorNormal()

        extent = self._getImageExtent()
        x, y = self.detectorPosition[0], self.detectorPosition[1]
        dx, dy = self.detectorDirection[0], self.detectorDirection[1]
        dr = (self.wall_rmax-self.wall_rmin) * arrowtaillength
        normf = self.wall_rmax / extent[1]
        self._detectorNormalHandle = self.axes.arrow(x/normf, y/normf, dx*dr/normf, dy*dr/normf, color=color, linewidth=linewidth, head_width=dr*0.02*arrowheadsize, head_length=dr*0.02*arrowheadlength)

        self.overlayDetectorNormal = True

    def removeDetectorNormal(self):
        if self._detectorNormalHandle is not None:
            self._detectorNormalHandle.remove()
            self._detectorNormalHandle = None

        self.overlayDetectorNormal = False

    def plotFluxSurfaces(self, plotstyle='w', linewidth=1):
        if self.flux is None:
            raise ValueError("No flux surfaces have been provided!")

        self.removeFluxSurfaces()
        self._fluxOverlayHandles = []

        R = self.flux['R']
        Z = self.flux['Z']
        lengths = self.flux['lengths']
        for i in range(0, len(lengths)):
            rz = np.transpose(np.array([R[i,:lengths[i]], Z[i,:lengths[i]]]))
            h = plotOrthogonalCrossSection(self.axes, rz, self.detectorPosition, self.detectorDirection, linewidth=linewidth, plotstyle=plotstyle)
            self._fluxOverlayHandles.append(h)

        self.overlayFluxSurfaces = True

    def removeFluxSurfaces(self):
        if not self._fluxOverlayHandles:
            for h in self._fluxOverlayHandles:
                h.remove()

            self._fluxOverlayHandles = []

        self.overlayFluxSurfaces = False

    def plotWallCrossSection(self, plotstyle='w', linewidth=1):
        """
        Plots a wall cross section ovelay over the image.
        Also toggles the setting so that 'assembleImage' will
        automatically include the overlay.
        """
        if self.wall is None:
            raise ValueError("No wall data has been provided!")

        self.removeWallCrossSection()
        self._wallCrossSectionOverlayHandle = plotOrthogonalCrossSection(self.axes, self.wall, self.detectorPosition, self.detectorDirection, linewidth=linewidth, plotstyle=plotstyle)
        self.overlayWallCrossSection = True

    def removeWallCrossSection(self):
        """
        Removes any wall cross section overlay plotted
        over the image.
        """
        if self._wallCrossSectionOverlayHandle is not None:
            self._wallCrossSectionOverlayHandle.remove()
            self._wallCrossSectionOverlayHandle = None

        self.overlayWallCrossSection = False

    def plotSeparatrix(self, plotstyle='w', linewidth=1):
        """
        Plots a separatrix ovelay over the image.
        Also toggles the setting so that 'assembleImage' will
        automatically include the overlay.
        """
        if self.separatrix is None:
            raise ValueError("No separatrix data has been provided!")

        self.removeSeparatrix()
        self._separatrixOverlayHandle = plotOrthogonalCrossSection(self.axes, self.separatrix, self.detectorPosition, self.detectorDirection, linewidth=linewidth, plotstyle=plotstyle)
        self.overlaySeparatrix = True

    def removeSeparatrix(self):
        """
        Removes any separatrix overlay plotted
        over the image.
        """
        if self._separatrixOverlayHandle is not None:
            self._separatrixOverlayHandle.remove()
            self._separatrixOverlayHandle = None
        self.overlaySeparatrix = False

    def plotTopview(self, wall=None, color='w', linewidth=1):
        """
        Plots a topview ovelay over the image.
        Also toggles the setting so that 'assembleImage' will
        automatically include the overlay.
        """
        if wall is None:
            if self.wall is None:
                raise ValueError("No wall data has been specified, which is required for the topview")
            else:
                wall = self.wall

        self.removeTopview()
        t = np.linspace(0, 2*np.pi)
        extent = self._getImageExtent()

        wall_rmin = np.amin(wall[:,0])
        wall_rmax = np.amax(wall[:,0])

        rmaj = extent[1]
        rmin = rmaj * (wall_rmin/wall_rmax)

        h1 = self.axes.plot(rmaj * np.cos(t), rmaj * np.sin(t), color, linewidth=linewidth)[0]
        h2 = self.axes.plot(rmin * np.cos(t), rmin * np.sin(t), color, linewidth=linewidth)[0]

        if wall is None:
            self._topviewOverlayHandles = (h1, h2)
            self.overlayTopview = True
        else:
            return (h1, h2)

    def removeTopview(self):
        """
        Removes any topview overlay plotted
        over the image.
        """
        if self._topviewOverlayHandles is not None:
            h1, h2 = self._topviewOverlayHandles
            h1.remove()
            h2.remove()

        self._topviewOverlayHandles = None
        self.overlayTopview = False

    def plotTopviewSeparatrix(self, color='w', linewidth=1):
        """
        Plots the separatrix boundaries in a top view.
        Also toggles the setting so that 'assembleImage' will
        automatically include the overlay.
        """
        if self.separatrix is None:
            raise ValueError("No separatrix data has been specified, which is required for the topview")

        (h1, h2) = self.plotTopview(wall=self.separatrix, color=color, linewidth=linewidth)
        self._topviewSeparatrixOverlayHandles = (h1, h2)
        self.overlayTopviewSeparatrix = True

    def removeTopviewSeparatrix(self):
        """
        Removes any topview separatrix overlay plotted
        over the image.
        """

        if self._topviewSeparatrixOverlayHandles is not None:
            h1, h2 = self._topviewSeparatrixOverlayHandles
            h1.remove()
            h2.remove()

        self._topviewSeparatrixOverlayHandles = None
        self.overlayTopviewSeparatrix = False

    def plotTopviewOrthogonalCrossSection(self, plotstyle='w', linewidth=1):
        """
        Plot the toroidal section corresponding to the
        cross-section that is orthogonal to the camera
        view (in topview).
        """

        if self.wall is None:
            raise ValueError("No wall data has been specified, which is required for the topview")

        self.removeTopviewOrthogonalCrossSection()

        # Rotate points along with camera
        cossin = [np.dot(self.detectorDirection, [0,1,0]), np.dot(self.detectorDirection, [1,0,0])]
        cossin = cossin / np.sqrt(cossin[0]**2 + cossin[1]**2)  # Normalize

        extent = self._getImageExtent()
        l1 = extent[1]
        l2 = extent[1] * (self.wall_rmin/self.wall_rmax)

        self._topviewOCSHandle = self.axes.plot([l1*cossin[0], l2*cossin[0]], [-l1*cossin[1], -l2*cossin[1]], plotstyle, linewidth=linewidth)

    def removeTopviewOrthogonalCrossSection(self):
        """
        Removes the orthogonal cross-section line
        of a topview plot.
        """
        if self._topviewOCSHandle is not None:
            self._topviewOCSHandle.remove()
            self._topviewOCSHandle = None

        self.overlayTopviewOrthogonalCrossSection = True

    def plotWall(self, plotstyle='w', degreesStart=[0], degreesEnd=[360],
             spacing=1, linewidth=0.1, rlim=0, zuplim=0, zlowlim=0,
             rmin=-1, rmax=1, zmin=-1, zmax=1):
        plotwall(self.axes, self.wall, self.detectorPosition, self.detectorDirection,
             self.detectorRoll, plotstyle, degreesStart, degreesEnd, spacing, linewidth,
             rlim, zuplim, zlowlim, rmin, rmax, zmin, zmax)

    def drawCircle(self, r, z, plotstyle='w', linewidth=1, degreeStart=180, degreeEnd=360):
        t = np.linspace(degreeStart * np.pi / 180, degreeEnd * np.pi / 180)
        xp = r * np.cos(t)
        yp = r * np.sin(t)
        zp = np.zeros(t.shape) + z
        plotCrossSection(self.axes, xp, yp, zp, self.detectorPosition, self.detectorDirection, linewidth=linewidth, plotstyle=plotstyle)

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
        intmin = np.amin(img)

        if intmin < 0:
            intmax = max(abs(intmin), intmax)
            intmin = -intmax

        if self.logarithmic:
            img = np.log10(img)
            intmax = np.log10(intmax)
            intmin = intmax - 40

            # Set all elements that are log10(0) = -inf or
            # at least below the "zero" level to "zero"
            img[np.where(img < intmin)] = intmin

        return img, intmin, intmax

    def _getImageExtent(self):
        """
        Compute the extent of the image (i.e. the physical size
        of the image in the plane at a unit distance from the camera).
        This is necessary for obtaining correct dimensions of overlays.
        """
        extent = np.array([-1,1,-1,1]) / 2
        
        if self.detectorVisang is not None:
            extent = extent * np.sqrt(2) * np.tan(self.detectorVisang/2)

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
            if zuplim != 0 and zc[i] > zuplim:
                nrc = np.append(nrc, np.nan)
                nzc = np.append(nzc, np.nan)
                continue
            if zlowlim != 0 and zc[i] < zlowlim:
                nrc = np.append(nrc, np.nan)
                nzc = np.append(nzc, np.nan)
                continue

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


def _rotateAboutAxis(xc, yc, zc, axis, angle=0):
    dx = axis[0]
    dy = axis[1]
    dz = axis[2]

    cs = np.cos(-angle)
    sn = np.sin(-angle)

    R = np.array([
        [cs+dx**2*(1-cs),    dx*dy*(1-cs)-dz*sn, dx*dz*(1-cs)+dy*sn],
        [dy*dx*(1-cs)+dz*sn, cs+dy**2*(1-cs),    dy*dz*(1-cs)-dx*sn],
        [dz*dx*(1-cs)-dy*sn, dz*dy*(1-cs)+dx*sn, cs+dz**2*(1-cs)]
    ])

    V = np.array([xc, yc, zc])
    X = np.matmul(R, V)

    return X[0,:], X[1,:], X[2,:]
    

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
    cossin = cossin / np.sqrt(cossin[0]**2 + cossin[1]**2)      # Normalize
    nrc, nyc, nzc = _rotateWall(rc, zc, cossin=cossin)
    return plotCrossSection(ax, nrc, nyc, nzc, cameraPosition, cameraDirection, plotstyle, linewidth)

def plotwall(ax, wall, cameraPosition, cameraDirection, cameraRoll=0, plotstyle='w',
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

            # [2] INTRODUCE CAMERA ROLL
            if cameraRoll != 0:
                nrc, nyc, nzc = _rotateAboutAxis(nrc, nyc, nzc, cameraDirection, angle=cameraRoll)

            # [2] ROTATE, TRANSLATE AND PLOT WALL SECTION AROUND CAMERA
            h = plotCrossSection(ax, nrc, nyc, nzc, cameraPosition, cameraDirection, plotstyle, linewidth)
            handles.append(h)

    return handles

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
    
