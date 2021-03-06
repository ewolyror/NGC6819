#Lines 4-7 bring in the most basic databases that this code needs to understand all the commands below it.
import numpy as np
from matplotlib import pylab
from IPython.core.pylabtools import *
from pylab import *
from numpy import *

#Line 9 brings in the command necessary to call data.
from astropy.io import fits

#Lines 12-13 tell the program where to find data (which, for this program to work, should be on the desktop) and define that data as "data."
hdu = fits.open("/Users/computationalphysics/Desktop/ib2o01020_drz.fits")[1]
data = hdu.data[3000:3500, 3000:3500] #This image is 5644x5895 pixels, and I want to restrict my search to the very small section in the center because the edges of these images are noisy and this code is optimized to work on smaller images.

#Lines 16-18 bring in all the command necessary to detect sources in an image with high precision (using source masking)
from photutils import DAOStarFinder
from photutils import make_source_mask
from astropy.stats import sigma_clipped_stats

#Lines 21-22 create a mask that covers all the sources (something is a source if its signal:noise = 2:1) in an image and compute estimated background level and noise using the mask for higher accuracy. We are only interested in background noise in this case, not level, which is defined as 'std'. This will be more accurate than the noise `make_source_mask` assumed for its signal:noise ratio, which it calculated on its own.
mask = make_source_mask(data, snr=2, npixels=5, dilate_size=10, sigclip_iters=None)
mean, median, std = sigma_clipped_stats(data, sigma=3.0, mask=mask, iters=None)

#Lines 25-27 find sources in the image using a higher signal:noise ratio (3:1) and more precise noise estimate. They then define the sources' positions.
daofind = DAOStarFinder(fwhm=4.0, threshold=200*std)
sources = daofind(data)
positions = (sources['xcentroid'],sources['ycentroid'])

#Lines 30-32 bring in all commands necessary for aperture photometry
from photutils import CircularAperture
from photutils import CircularAnnulus
from photutils import aperture_photometry
from photutils.utils import calc_total_error

#Lines 35-37 create aperture objects (a circle around each source with a concentric annulus around each circle) and group them in a 2x1 array called apers.
apertures = CircularAperture(positions, r=5.)
annuli = CircularAnnulus(positions, r_in=6., r_out=8.)
apers = [apertures, annuli]

#Lines 40-41 replace all negatives in 'data' with , estimate the uncertainty in the number of counts at each pixel, and define that uncertainty as 'error'
bkg_err = np.zeros(shape=(500,500))
gain_eff = 7058 #seconds
error = calc_total_error(data, bkg_err, gain_eff)

#Line 44 calculates the total number of counts/s in both the center circles and annuli around each source and propogates the uncertainty from each pixel over the entire source (note: each pixel in a drizzled image like this one has information about counts/s, not counts. You can use the observation time as an "effective gain" and multiply each data point by this gain if you desire total counts)
phot_table = aperture_photometry(data, apers, error=error)

#Lines 47-50 do the math necessary for aperture photometry. Using the annulus, and average background flux rate level is determined (counts/s in annulus divided by area of annulus), which is then multiplied by the area inside the center circle to find the total counts/s due to the background that are inside the circle. That value is subtracted from the measured flux rate inside the circle and you have an accurate estimate of the flux rate of the star itself. Line 48 adds a new column to phot_table with this information.
bkg_mean = phot_table['aperture_sum_1'] / annuli.area()
bkg_sum = bkg_mean * apertures.area()
final_sum = phot_table['aperture_sum_0'] - bkg_sum
phot_table['residual_aperture_sum'] = final_sum

#Lines 53-56 calculate the total error in the same way as the flux rate in counts/s is calculated above
err_mean = phot_table['aperture_sum_err_1'] / annuli.area()
err_sum = err_mean * apertures.area()
final_err = phot_table['aperture_sum_err_0'] - err_sum
phot_table['residual_err_sum'] = final_err

#Lines 59-62 save an untruncated text file called 'phot_table.txt' that has columns "id, xcenter pix, ycenter pix, aperture_sum_0 (counts/s in the inner circle), aperture_sum_1 (counts/s in the annulus), aperture_sum_err_0 (total uncertainty from annulus), aperture_sum_err_1 (total uncertainty in center circle), residual_aperture_sum (counts/s due to sources inside the circle), and residual_sum_err (total uncertainty in source flux rate)"
flux = phot_table['residual_aperture_sum']
flux[flux < 0] = 0
phot_table = np.array(phot_table)
np.set_printoptions(threshold=np.nan)
log = open("/Users/computationalphysics/Desktop/phot_table.txt", "w")
print(phot_table, file = log)

#Lines 65-66 bring in the tools necessary to draw an undistorted image
from astropy.visualization import LogStretch
from astropy.visualization.mpl_normalize import ImageNormalize

#Lines 69-73 show all the sources in an image by circling them in blue. Line 74 can be uncommented to show the annuli as well
"""plt.subplot(211)
plt.title('Sources in RA = {-19:41:06.6573 U -19:41:05.6944} Dec = {40:10:46.003 U 40:10:44.051}')
norm = ImageNormalize(stretch = LogStretch())
plt.imshow(data, cmap='coolwarm',origin='lower',norm=norm)"""
#apertures.plot(color='blue', lw=1.5, alpha=.5)
#annuli.plot(color='blue', lw=1.5, alpha=.5) #uncomment this line to plot the annuli
fig, ax = plt.subplots()
#Lines 77-82 create a plot that shows the flux rates and implied uncertainties for each source. Sources are numbered 1-147
plt.subplot(212)
plt.errorbar(phot_table['id'], flux, yerr=phot_table['residual_err_sum'], fmt='o', markersize=2.5, ecolor='r', barsabove=True)
plt.xlabel('Source ID')
ticks = np.arange(0,21,.1)
ax.set_xticks(ticks)
plt.ylabel('Flux (counts)')
#ax.text(2.5, 20000, 'Points 2, 3, 5, 6, 9, 10, and 11 are invalid')
ax.text(20000, 2.5, 'Points 2, 3, 5, 6, 9, 10, and 11 are invalid',
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes,
        fontsize=12)
plt.title('Fluxes of Above Sources')
X = len(phot_table['id'])
xspot = phot_table['id']
yspot = flux
for i in range (0,X):
    plt.annotate("%d" % (i+1), (xspot[i],yspot[i]))

plt.subplot(211)
norm = ImageNormalize(stretch = LogStretch())
plt.imshow(data, cmap='coolwarm',origin='lower',norm=norm)
plt.title('Sources in RA = {-19:41:06.6573 U -19:41:05.6944} Dec = {40:10:46.003 U 40:10:44.051}')
apertures.plot(color='yellow', lw=1.5, alpha=.5)
N = len(sources['xcentroid'])
xpos = sources['xcentroid']
ypos = sources['ycentroid']
for i in range (0,N):
    plt.annotate("%d" % (i+1), (xpos[i],ypos[i]))
plt.show()
