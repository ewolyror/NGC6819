"""plotpos.py a program to plot dolphot output on the reference image
used for photometry"""
#import modules
from pylab import *
from scipy import *
from numpy import *
from photutils import CircularAperture
from astropy.io import fits
#do awk stuff here with numpy
#dolph = loadtxt('/Volumes/64FLASH/dolphotresults/ib2o01/ngc6819_wfc3_grid4.phot')
#gdolph=dolph[where(all(dolph[:,6] >= -.3 * dolph[:,6] <= .3 * dolph[:,23]  == 0 * dolph[:,5]  >= 75 * dolph[:,7] <= 1 * dolph[:,9] <= 1))]
#import data
pos = loadtxt('/Volumes/64FLASH/dolphotresults/ib2o01/positions.txt')
#pos = gdolph[:,2,:,3]
#print(pos)
#print(len(pos))
clf()
hdu = fits.open("/Volumes/64FLASH/astro/photometry/NGC6819/raw/raw+/ib2o01/ib2o01020_drc.fits")[1]
data = hdu.data

#plot the data
apertures = CircularAperture(pos, r=50)
print(len(pos))
#show everything- v min and v max define the end points of the color mapping
#imshow(data, cmap='Greys', origin='lower', vmin=0, vmax=1)
#imshow(data, cmap='gray', origin='lower', vmin=0, vmax=1)
#imshow(data, cmap='coolwarm', origin='lower', vmin=0, vmax=1)
imshow(data, cmap='rainbow', origin='lower', vmin=0, vmax=1)
apertures.plot(color='xkcd:tangerine', lw=1)
savefig('ib2o01.png',dpi=300)
show()
