from shapely.geometry import Polygon
import numpy as np
import pickle
from tqdm import tqdm
import sys
from skimage import io, color
import matplotlib
import cv2

class _click_event:
	def __init__(self, img): 
		self.img = img.copy() #so original image isn't modified with polylines information.
		
		#intializes an empty array for our polygon
		self.pts = np.empty([0,2], dtype='uint32')
		
		#this doesn't do anything
		self.color = (255, 255, 0)

		#sets the thickness of the lines of the polygon
		self.thickness = 2

	def upon_click(self, event, x, y, flags, params):
		# checking for left mouse clicks
		if event == cv2.EVENT_LBUTTONDOWN:
			print(x, ' ', y)
			self.pts = np.append(self.pts, [[x,y]], 0)
			isClosed = False

			img2 = cv2.polylines(self.img, [self.pts],
			      isClosed, self.color, self.thickness)
			cv2.imshow('image', img2)
            
		elif event == cv2.EVENT_RBUTTONDOWN:
			isClosed = True
			img2 = cv2.polylines(self.img, [self.pts],
						    isClosed, self.color, self.thickness)
			cv2.imshow('image', img2)

	def crop_poly(self, buff=10):
		"""
	    Crops the video to the x and y coordinates of the polygon, with buffer.
		
		Note that this buffer is present when choosing a vacuum region as well.
        """
		y,x = self.img.shape
		xmin, xmax = (np.min(self.pts[:,0]), np.max(self.pts[:,0]))
		ymin, ymax = (np.min(self.pts[:,1]), np.max(self.pts[:,1]))
		
		### new_bounds created so that buffered bounding rectangle of 
		### chosen polygon does not exceed original dimensions
		self.new_bounds_x = (max(xmin-buff, 0), min(xmax+buff, x))
		self.new_bounds_y = (max(ymin-buff, 0), min(ymax+buff, y))
		self.pts = self.pts-np.repeat([[self.new_bounds_x[0], self.new_bounds_y[0]]], len(self.pts), 0)
	    
	def get_poly(self):
		return Polygon(self.pts)

def identify_polygon():	
    """
	Takes as input a greyscale video or a color image.
	"""
    matplotlib.use("TkAgg")
    while True:
        file_name = input("File name>>>")
        if file_name.lower() == "quit":
            sys.exit()		
        try:
            video = io.imread(file_name)
            break
        except FileNotFoundError:
            print("File not found, please try again")

    if video.shape[2] == 3:
        sv = color.rgb2gray(video)
        two_d = True
    elif video.shape[2] == 4:
        sv = color.rgb2gray(color.rgba2rgb(video))
        two_d = True
    else:
        two_d = False
        vids, rows, cols = video.shape
        sv = np.empty([rows, cols], 'uint32')
        for ij in tqdm(range(rows*cols), desc="Summing image"):
            i, j = (ij // cols, ij % cols)
            sv[i, j] = np.sum(video[:,i,j])	
        
    #summed_video converted to 'uint8' tsype for cv2 purposes
    summed_video = np.rint(sv/np.max(sv)*255).astype('uint8')				
    click_it = _click_event(summed_video)
    cv2.imshow('image', click_it.img)
    cv2.setMouseCallback('image', click_it.upon_click)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    click_it.crop_poly()
    xmin, xmax = click_it.new_bounds_x
    ymin, ymax = click_it.new_bounds_y
    bounds = {'x': (xmin, xmax), 'y': (ymin, ymax)}
    
    if two_d:
        video = sv[ymin:ymax, xmin:xmax]
    else:
        video = video[:, ymin:ymax, xmin:xmax]
        
        
    polygon = click_it.get_poly()
    output_dict = {'video': video, 'polygon': polygon, 'bounds': bounds}
    savefile_ = input('Save pickle object>>>')
    savefile = savefile_+".pkl"
    F = open(savefile, 'wb')
    pickle.dump(output_dict, F)
    F.close()	
