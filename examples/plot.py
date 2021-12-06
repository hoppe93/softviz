#!/usr/bin/env python3
#
# A simple example of how to use
# the SyntheticImage class. In
# difference to the main softviz
# program, this example does not
# require Qt.
##################################

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')

from SyntheticImage import SyntheticImage

si = SyntheticImage()

# Load the SOFT image
si.loadImageFile('image.mat')

# Plot the image
si.assembleImage()

plt.show()

