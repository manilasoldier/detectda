from joblib import Parallel, delayed
from sklearn.utils.validation import check_is_fitted
from . import hlpr as _dh
import numpy as np
import pickle
import time

#See the following link for information on how to process series of persistence diagrams using GUDHI: https://giotto-ai.github.io/gtda-docs/0.5.1/_modules/gtda/homology/cubical.html#CubicalPersistence.transform

class ImageSeries:
    """
    Reads in an image series (video), either a single or multiple frames. 

    May optionally specify polygonally region, held constant across frames,
    in which to select specific generators in persistent homology.
    """
    def __init__(self, video, polygon=None, div=1, n_jobs=None):
        """
        The argument 'div', if not equal to 1, divides each pixel by div
        and rounds to the nearest integer. 

        The argument n_jobs specifies how many jobs preferred for the 
        parallel backend. 
        """
        if video.ndim == 2:
            video = np.expand_dims(video, axis=0)    
        elif video.ndim != 3: 
            raise ValueError("Need to initialize with array of 2 or 3 dimensions")
        
        if div==1:
            self.video = video        
        else: 
            self.video = np.rint(video/div)
        
        self.degp_totp = {}
        self.polygon = polygon
        self.div = div
        self.n_jobs = n_jobs
    
    def fit(self, sigma=None, max_death_pixel_int=True, print_time=True):
        """
        Fit method for ImageSeries object.

        Optional Gaussian smoothing with sigma parameter.

        The argument max_death_pixel_int controls whether or not 
        the maximum death time is the largest pixel value (within an image),
        or the largest finite death time (within an image).
        """
        if print_time:
            tic=time.perf_counter()        
        self.diags_ = Parallel(n_jobs = self.n_jobs)(delayed(_dh.fitsmoo)(im, self.polygon, sigma, 
                                max_death_pixel_int) for im in self.video)    
        if print_time:
            toc=time.perf_counter()
            print(f"Video processed in {toc - tic:0.4f} seconds")
        
        self.sigma_=sigma
        self.max_death_pixel_int_=max_death_pixel_int
        return self
    
    def get_degp_totp(self, p=1, inf=False):
        "Get degree-p total persistence of each image frame from fitted object."
        check_is_fitted(self)
        dgtp = np.fromiter((_dh.degp_totp(x[:,2], p, inf) for x in self.diags_), float)
        if inf:
            self.degp_totp['inf'] = dgtp
        else:
            self.degp_totp[str(p)] = dgtp

    def get_pers_entr(self, neg=True):    
        """
        Get persistent entropy of each image frame from fitted object. For hypothesis testing
        purposes, the default is negative of the entropy
        """
        check_is_fitted(self)
        self.pers_entr = np.fromiter((_dh.pers_entr(x[:,2], neg) for x in self.diags_), float)
    
    def get_alps(self):
        "Get ALPS statistic of each image frame from fitted object."
        check_is_fitted(self)
        self.alps = np.fromiter((_dh.alps(x[:,2]) for x in self.diags_), float)  
        
    def plot(self, seq):
        """
        Plot a time series of degp_totp, pers_entr, or alps...
        """
        pass
        


class ImageSeriesPickle(ImageSeries):
    """
    Designed for use with output of identify_polygon script
    """
    def __init__(self, file_path, div=1, n_jobs=None):
        file = open(file_path, 'rb')
        data = pickle.load(file)
        super().__init__(data['video'], data['polygon'], div, n_jobs)
        file.close()
                
