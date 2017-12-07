#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')

from PolarizedImage import PolarizedImage, ImageType

plt.figure(figsize=(15,10))
polimg = PolarizedImage()

polimg.loadPolarizedImage('polimg.mat')

polimg.setImageTypes([ImageType.I, ImageType.POSQ, ImageType.POSU, ImageType.LINPOLFRAC, ImageType.NEGQ, ImageType.NEGU])
polimg.assembleImage(2,3)

plt.show()
