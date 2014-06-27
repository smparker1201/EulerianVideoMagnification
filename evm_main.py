import vid_io as vio
import evm 

if __name__=='__main__':


	blur_sigma=4

	pyramid_levels=5
	level_scale=2
	fps=10
	alpha=0
	passband_lower=.001
	passband_upper=5
	lambda_c=2

	frames = vio.vid_to_frames('test_vid/babysleeping_source.wmv', fps)
	
	frames = evm.enhance(frames,blur_sigma,pyramid_levels,level_scale,fps,alpha,passband_lower,passband_upper,lambda_c)

	vio.frames_to_vid(frames,fps)
