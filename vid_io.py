import os
import scipy as sp
from shutil import rmtree as rmdir
from evm import adjust_intensity

#=====================================================================================================#
def vid_to_frames(vid,fps):

	rmdir('temp_ims')
	os.mkdir('temp_ims')
	os.system('avconv -i '+vid+' -r '+str(fps)+'  temp_ims/input%04d.png')
	vid_frames=os.listdir('temp_ims');vid_frames.sort()
	frames=[sp.misc.imread('temp_ims/'+frm) for frm in vid_frames]
	#import ipdb;ipdb.set_trace()
	#rmdir('temp_ims')

	return frames
#=====================================================================================================#
def frames_to_vid(frames,fps):
	
	#os.mkdirs('temp_ims')
	for i,frame in enumerate(frames):
		#sp.misc.imshow(frame)
		ind="%05d"%i
		
		sp.misc.imsave('temp_ims/outputt'+ind+'.png',frame)
		im=sp.misc.imread('temp_ims/outputt'+ind+'.png')
		enhanced=adjust_intensity(im,1,1,1.5,255.0,1,1,1)
		sp.misc.imsave('temp_ims/output'+ind+'.png',enhanced)

	os.system('avconv -f image2 -r '+str(fps)+' -i temp_ims/output%05d.png -crf 1 output.avi')
	os.system('gnome-open output.avi')

	#rmdir('temp_ims')
