
import numpy as np
import scipy.io
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from enum import Enum

class ImageType(Enum):
    EMPTY = 'N/A'
    I = 'I'
    POSQ = 'Q'
    NEGQ = '-Q'
    POSU = 'U'
    NEGU = '-U'
    POSV = 'V'
    NEGV = '-V'
    LINPOLFRAC = 'Linear polarization fraction'
    POLANGLE = 'Polarization angle'
    HORIZONTAL = 'Horizontal'
    VERTICAL = 'Vertical'
    DIAGONAL1 = 'Diagonal 1'
    DIAGONAL2 = 'Diagonal 2'

class PolarizedImage:
    
    def __init__(self, figure=None, canvas=None, registerGeriMap=True):
        self.images = []
        self.imageType = [0]*8
        self.nRows = 1          # Number of image rows
        self.nCols = 1          # Number of image columns
        self._colorbar = None

        self.canvas = canvas
        self.figure = figure
        self.colormapName = 'GeriMap'
        self.labelFontSize = 22
        self.showLabels = False
        self.labeXLoc, self.labelYLoc = 0.9, 0.9
        self.labelHorizontalAlignment = 'right'

        self.StokesI, self.StokesQ, self.StokesU, self.StokesV = None, None, None, None
        self.detectorPosition = np.array([0, 0, 0])
        self.detectorDirection = np.array([0, 0, 0])
        self.detectorVisang = 0

        if self.figure is None:
            self.figure = plt.gca().figure
            self.figure.patch.set_facecolor('black')
            if self.canvas is not None:
                raise ValueError("Canvas set, but no figure given. If no figure is given, no canvas may be given.")
        if self.canvas is None:
            self.canvas = self.figure.canvas

        self.axes = []

        if registerGeriMap:
            PolarizedImage.registerGeriMap()

        # Disable 'divide-by-zero' error which
        # otherwise occurs when calculating the linear
        # polarization fraction (in empty pixels)
        np.seterr(invalid='ignore')


    def toggleLabels(self):
        self.showLabels = not self.showLabels

    def setImageTypes(self, arr):
        self.imageType = arr

    def setLabelLocation(self, x, y):
        self.labelXLoc, self.labelYLoc = x, y

    def setLabelHorizontalAlignment(self, al):
        self.labelHorizontalAlignment = al

    def setLabelFontSize(self, fontsize):
        self.labelFontSize = fontsize


    def assembleImage(self, nRows=None, nCols=None, border=True, plotLabel=True):
        if nRows is not None: self.nRows = nRows
        if nCols is not None: self.nCols = nCols

        if self.nRows >= 10 or self.nCols >= 10:
            raise ValueError('Invalid grid size specified for figure')

        self.clearImage()
        self.axes = []
        self.images = [0] * (self.nRows*self.nCols)
        
        for i in range(0, self.nRows*self.nCols):
            self.axes.append(self.figure.add_subplot(self.nRows, self.nCols, i+1))

            if i < len(self.imageType):
                self.plotImage(i, border, plotLabel)

    def loadPolarizedImage(self, filename):
        """
        Load output from the SOFT 'polimage' sycout.
        """
        if filename.endswith('.mat'):
            try:
                self._loadMatFile(filename)
            except NotImplementedError: 
                self._loadHDF5File(filename)
        elif filename.endswith('.h5') or filename.endswith('.hdf5'):
            self._loadHDF5File(filename)
        else:
            raise NotImplementedError('Unrecognized file format of file: '+filename)

    def _loadMatFile(self, filename):
        """
        Load a legacy Matlab file.
        """
        matfile = scipy.io.loadmat(filename)

        self.StokesI = np.transpose(matfile['StokesI'])
        self.StokesQ = np.transpose(matfile['StokesQ'])
        self.StokesU = np.transpose(matfile['StokesU'])
        self.StokesV = np.transpose(matfile['StokesV'])
        self.detectorPosition = matfile['detectorPosition'][0]
        self.detectorDirection = matfile['detectorDirection'][0]
        self.detectorVisang = matfile['detectorVisang']

        try: self.wall = np.transpose(matfile['wall'])
        except KeyError: pass

        try: self.wall = np.transpose(matfile['separatrix'])
        except KeyError: pass

    def _loadHDF5File(self, filename):
        """
        Load a HDF5 file.
        Used also for modern Matlab files.
        """
        matfile = h5py.File(filename)

        self.StokesI = np.transpose(matfile['StokesI'][:,:])
        self.StokesQ = np.transpose(matfile['StokesQ'][:,:])
        self.StokesU = np.transpose(matfile['StokesU'][:,:])
        self.StokesV = np.transpose(matfile['StokesV'][:,:])
        self.detectorPosition = matfile['detectorPosition'][:,0]
        self.detectorDirection = matfile['detectorDirection'][:,0]
        self.detectorVisang = matfile['detectorVisang'][0,0]

        try: self.wall = matfile['wall'][:,:]
        except KeyError: pass

        try: self.separatrix = matfile['separatrix'][:,:]
        except KeyError: pass

    def plotImage(self, index, border=True, plotLabel=True):
        imgtype = self.imageType[index]
        ax = self.axes[index]
        colormap = plt.get_cmap(self.colormapName)

        img = np.zeros(np.shape(self.StokesI))
        intmin, intmax = 0, 1
        if imgtype == ImageType.EMPTY:
            return
        elif imgtype == ImageType.I:
            img = np.copy(self.StokesI)
            intmin, intmax = 0, np.amax(self.StokesI)
        elif imgtype == ImageType.POSQ:
            img = np.copy(self.StokesQ)
            img[img < 0] = 0
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.NEGQ:
            img = -np.copy(self.StokesQ)
            img[img < 0] = 0
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.POSU:
            img = np.copy(self.StokesU)
            img[img < 0] = 0
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.NEGU:
            img = -np.copy(self.StokesU)
            img[img < 0] = 0
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.POSV:
            img = np.copy(self.StokesV)
            img[img < 0] = 0
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.NEGV:
            img = -np.copy(self.StokesV)
            img[img < 0] = 0
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.LINPOLFRAC:
            img = np.sqrt(self.StokesU**2 + self.StokesQ**2) / self.StokesI
            img = np.nan_to_num(img)
            intmin, intmax = 0, 1
        elif imgtype == ImageType.POLANGLE:
            img = 0.5 * np.atan(self.StokesU / self.StokesQ)
            intmin, intmax = -np.pi/2, np.pi/2
        elif imgtype == ImageType.HORIZONTAL:
            img = 0.5 * (self.StokesI + self.StokesQ)
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.VERTICAL:
            img = 0.5 * (self.StokesI - self.StokesQ)
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.DIAGONAL1:
            img = 0.5 * (self.StokesI + self.StokesU)
            intmin, intmax = 0, np.amax(img)
        elif imgtype == ImageType.DIAGONAL2:
            img = 0.5 * (self.StokesI - self.StokesU)
            intmin, intmax = 0, np.amax(img)

        self.images[index] = ax.imshow(img, origin='lower', cmap=colormap, interpolation=None, clim=(intmin, intmax), extent=[0,1,0,1])
        #ax.set_axis_off()
        if border:
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')

        #ax.set_title(imgtype.value, color='white', fontdict={'fontsize': self.titleFontSize})
        if plotLabel:
            x, y = self.labeXLoc, self.labelYLoc
            ax.text(x, y, imgtype.value, color='white', fontdict={'fontsize': self.labelFontSize}, horizontalalignment=self.labelHorizontalAlignment)

    def plotColorbar(self):
        """
        Add a colorbar to the axes 'ax' of figure 'fig'.
        Respects the 'colorbarRelative' setting and uses percentage
        ticks if 'colorbarRelative' is True.
        """
        self.removeColorbar()

        #                                         X   Y   W    H
        self._colorbarax = self.figure.add_axes([0.02,-0.06,0.97,0.05])

        mx = self.images[0].get_clim()[1]
        self._colorbar = self.figure.colorbar(self.images[0], cax=self._colorbarax, ticks=[0,mx*0.2,mx*0.4,mx*0.6,mx*0.8,mx], orientation='horizontal')
        self._colorbar.ax.set_xticklabels(['0%','20%','40%','60%','80%','100%'])
        self._colorbar.ax.tick_params(labelcolor='white', color='white', labelsize=self.labelFontSize)

    def removeColorbar(self):
        """
        Removes any existing colorbar on the plot
        """
        if self._colorbar is not None:
            self._colorbar.remove()
            self._colorbar = None

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

    def save(self, filename, dpi=100, supertight=True):

        if supertight:
            self.figure.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        else:
            self.figure.subplots_adjust(top=0.93, bottom=0, right=1, left=0, hspace=0, wspace=0)

        self.canvas.print_figure(filename, bbox_inches='tight', pad_inches=0, facecolor='black', dpi=dpi)

    #########################################################
    #
    # INTERNAL METHODS
    #
    #########################################################
    def clearImage(self):
        self.figure.clear()

