from scipy import fftpack as ftp
from scipy import ndimage as ndi
import scipy as sp
import Image
import math
from scipy import signal as sig


def enhance(frames,blur_sigma,pyramid_levels,level_scale,fps,alpha,passband_lower,passband_upper,lambda_c):
	pyramid=vid_laplacian(frames,pyramid_levels,level_scale,blur_sigma,fps)
	filtered_pyramid=temporal_filt(pyramid,fps,passband_lower,passband_upper)
	
	#amplified_signal=amplify_signal(filtered_pyramid,alpha)
	#return collapse_vid_pyr((amplified_signal+(100-alpha)*sp.array(pyramid))/100,level_scale,blur_sigma)
	return collapse_vid_pyr(sp.array(filtered_pyramid)*.5,level_scale,blur_sigma)
	
#=====================================================================================================#
def im_filt(image, sig, mode='gaussian'):
	'''apply indicated filter type with gaussian by defalut'''
	
	#for color images
	if len(sp.shape(image))==3:
		assert sp.shape(image)[-1]==3, "invalid color image"
		im_filtered=sp.zeros(sp.shape(image))
		
		for ch in range(sp.shape(image)[-1]):
			img=image[:,:,ch]
			im = ndi.filters.gaussian_filter(img,sig)
			im_filtered[:,:,ch]=im
		return im_filtered

	elif len(sp.shape(image))==2:
		im_filtered=ndi.filters.gaussian_filter(image,sig)
		return im_filtered

	raise Exception, "Invalid image content"
#=====================================================================================================#
def vid_laplacian(vid,levels,downscale,sig,frmps):
	'''Takes in a video sequence, decomposes it into frames, and then creates a Laplacian
		pyramid for the entire sequence.'''

	sp_bands=[]

	for frame in vid:
		
		temp_pyr=pyr_laplacian(frame,levels,downscale,sig)
 		if len(sp_bands)==0:
			sp_bands=[[] for i in range(len(temp_pyr))]
		for i,band in enumerate(temp_pyr):
			sp_bands[i].append(band)		
			
	return sp_bands
#=====================================================================================================#
def pyr_laplacian(image,layers,downscale,sig):
	'''constructs the laplacian pyramid of the image'''

	spatial_bands=[]
	layer=0
	rows = image.shape[0]
	cols = image.shape[1]
	dim_three = 0
	if len(sp.shape(image))==3:
		dim_three=3

	smoothed_image=im_filt(image,sig)
	spatial_bands.append(image-smoothed_image)

	for layer in range(layers-2):

		out_rows = int(math.ceil(rows / float(downscale)))
		out_cols = int(math.ceil(cols / float(downscale)))

		resized_image = sp.misc.imresize(smoothed_image,(out_rows,out_cols,dim_three),interp='cubic')
		smoothed_image = im_filt(resized_image,sig)

		prev_rows = rows
		prev_cols = cols
		rows = resized_image.shape[0]
		cols = resized_image.shape[1]

		if prev_rows == rows and prev_cols == cols:
			break
		
		spatial_bands.append(resized_image-smoothed_image)

	spatial_bands.append(smoothed_image)
	
	return sp.array(spatial_bands)

#=====================================================================================================#
def temporal_filt(sp_bands,fps,lower,upper):
	'''This will produce the fourier transform of each spatial frequency band along 
		its temporal dimension and apply an ideal bandpass filter with passband between 
		lower and upper.'''

	def chop_freqs(band):
		#import ipdb;ipdb.set_trace()
		fourier = ftp.fft(band,axis=0)
		freq_bins = ftp.fftfreq(sp.shape(band)[0],d=1.0/fps)
		lower_index = sp.argmin(abs(freq_bins-lower))
		upper_index =sp.argmin(abs(freq_bins-upper))
		#import ipdb;ipdb.set_trace()
		fourier[2:]*=30
		fourier[2:lower_index]*=0
		fourier[upper_index:-upper_index]*=0
		if lower_index != 0:
			fourier[-lower_index:]*=0
		#fourier=sp.array(fourier)

		return sp.real(ftp.ifft(fourier, axis=0))

	def buttersworth_bandpass(band):
		b,a = sp.signal.butter(5,[lower/fps,upper/fps],btype='bandpass')
		return sp.signal.lfilter(b, a, band, axis=0)
	
	return sp.array([chop_freqs(band) for band in sp_bands])
	

#=====================================================================================================#	
def amplify_signal(bands,alpha):
	bands=sp.array(bands)
	#bands[-2]*=alpha
	#bands[-1]*=alpha
	#bands[-2:]*=0
	#import ipdb;ipdb.set_trace()
	
	
	return bands*alpha
#=====================================================================================================#
def collapse_pyr(pyr,upscale,sig):
	'''Collapses spatial pyramid'''
	#reversing order so lowest resolution comes first
	pyr=pyr.tolist()
	pyr.reverse()
	pyr=sp.array(pyr)
	curr=None

	if sig==None:
		sig = 2*upscale/6.0

	for i,res in enumerate(pyr[:-1]):
		if curr!=None:
			res+=curr
		out_rows=sp.shape(pyr[i+1])[0]
		out_cols=sp.shape(pyr[i+1])[1]

		if len(sp.shape(res))==3 and sp.shape(res)[-1]==3:
			res=sp.misc.imresize(res,(out_rows,out_cols,3),interp='cubic')
		else:
			res=sp.misc.imresize(res,(out_rows,out_cols),interp='cubic')
		curr=im_filt(res,sig)

	return curr+pyr[-1]

#=====================================================================================================#
def collapse_vid_pyr(vpyr,scale,sig):
	'''Applies collapse_pyr for each frame in a video sequence.'''
	collapsed_vids=[]

	vpyr=sp.array(vpyr)

	for frm in range(sp.shape(vpyr)[1]):

		collapsed_vids.append(collapse_pyr(vpyr[:,frm],scale,sig))

	return collapsed_vids
