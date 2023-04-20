from joblib import Parallel, delayed
from sklearn.utils.validation import check_is_fitted
from skimage import filters
from . import hlpr as _dh
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import time

#See the following link for information on how to process series of persistence diagrams using GUDHI: https://giotto-ai.github.io/gtda-docs/0.5.1/_modules/gtda/homology/cubical.html#CubicalPersistence.transform

class VidPol:
    def __init__(self, video, polygon=None, div=1, n_jobs=None):
        if video.ndim == 2:
            video = np.expand_dims(video, axis=0)    
        elif video.ndim != 3: 
            raise ValueError("Need to initialize with array of 2 or 3 dimensions")
        
        if div==1:
            self.video = video     
        elif div <= 0:
            raise ValueError("div argument cannot be 0 or less")
        else: 
            self.video = np.rint(video/div)
        
        self.polygon = polygon
        self.div = div
        self.n_jobs = n_jobs
        

class ImageSeries(VidPol):
    """
    Reads in an image series (video), either a single or multiple frames. 

    May optionally specify polygonally region, held constant across frames,
    in which to select specific generators in persistent homology.

    Parameters
    ----------
    video : array_like
            Image series. Index on axis=0 represents the frame index, unless a single image (2d array) is provided. 
    polygon : shapely.Polygon, optional, default is ``None``
            Polygonal region outside of which positive cells of 0th persistent homology will be excluded. 
    div : positive int/float, optional, default is ``1``.
            In nanoparticle imaging process, pixel intensities are often registered as something close to a(div), 
            so dividing by div and rounding to nearest integer will give pixel intensities that conform more strongly 
            to common parametric assumptions.
    n_jobs : int or None, optional, default is ``None``
            The number of jobs to use for the computation. ``None`` means 1 unless
            in a :obj:`joblib.parallel_backend` context. ``-1`` means using all
            processors.
    """
    def __init__(self, video, polygon=None, div=1, n_jobs=None):
        super().__init__(video, None, div=div, n_jobs=n_jobs)
        self.degp_totp = {}
    
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
        dgtp = np.fromiter((_dh.degp_totp(x[x[:,3].astype(np.bool),2], p, inf) for x in self.diags_), float)
        if inf:
            self.degp_totp['inf'] = dgtp
        else:
            self.degp_totp[str(p)] = dgtp

    #.astype(np.bool) is a quick fix and needs to remedied...
    def get_pers_entr(self, neg=True):    
        """
        Get persistent entropy of each image frame from fitted object. For hypothesis testing
        purposes, the default is negative of the entropy
        """
        check_is_fitted(self)
        self.pers_entr = np.fromiter((_dh.pers_entr(x[x[:,3].astype(np.bool),2], neg) for x in self.diags_), float)
    
    def get_alps(self):
        "Get ALPS statistic of each image frame from fitted object."
        check_is_fitted(self)
        self.alps = np.fromiter((_dh.alps(x[x[:,3].astype(np.bool),2]) for x in self.diags_), float)  
        
        
    def plot_im(self, frame, plot_poly=True, plot_pts=True, smooth=True, thr=None, **kwargs):
        """
        Plot an individual frame in the video, with or without the polygonal region superimposed
        """
        
        imd = self.diags_[frame]
        if smooth:
            plim = filters.gaussian(self.video[frame], sigma=self.sigma_, preserve_range=True)
        else:
            plim = self.video[frame]
        
        which_plt = imd[:, 3].astype(bool)
        if thr==None:
            pass
        else:
            over_thr = (imd[:, 2] > thr) #just right over the threshold, not as a proportion...
            which_plt = np.logical_and(over_thr, which_plt)
            
        if plot_pts:
            plt0 = plt.scatter(
                x = imd[which_plt, 0],
                y = imd[which_plt, 1],
				c = imd[which_plt, 2],
				cmap = "autumn",
                **kwargs
			)
            plt.imshow(plim, cmap="gray")
            plt.colorbar(plt0)	
        else:
            plt.imshow(plim, cmap="gray")
			 
        try:
            if plot_poly:
                xs, ys = list(zip(*self.polygon.exterior.coords)) #'unzip' exterior coordinates of a polygon for plotting
                plt.plot(xs,ys, color="cyan")
        except AttributeError:
            print("Must set plot_poly to False if polygon not specified")    


class ImageSeriesPlus(VidPol):
    """
    Reads in an image series (video), either a single or multiple frames. 

    May optionally specify polygonal region, held constant across frames,
    in which to select specific generators in persistent homology. Similar to ImageSeries,
    but with enhanced functionality for utilizing BOTH 0- and 1-dimensional persistent homology.
    """
    def __init__(self, video, polygon=None, div=1, n_jobs=None):
        super().__init__(video, None, div=div, n_jobs=n_jobs)
    
    def fit(self, sigma=None, print_time=True, verbose=0):
            """
            Fit method for ImageSeriesPlus object.

            Optional Gaussian smoothing with sigma parameter.

            The argument max_death_pixel_int controls whether or not 
            the maximum death time is the largest pixel value (within an image),
            or the largest finite death time (within an image).
            """
            if print_time:
                tic=time.perf_counter()        
            self.diags_ = Parallel(n_jobs = self.n_jobs, verbose=verbose)(
                                    delayed(_dh.persmoo)(im, self.polygon, sigma) 
                                    for im in self.video)    
            if print_time:
                toc=time.perf_counter()
                print(f"Video processed in {toc - tic:0.4f} seconds")
            
            self.sigma_=sigma
            return self
        
    def convert_to_df(self):
        check_is_fitted(self)
        col_names = ["x_coord", "y_coord", "hom_dim", "birth", "death", "in_poly"]
        self.dfs_ = [pd.DataFrame(x, columns=col_names) for x in self.diags_]
    
    def get_lifetimes(self):
        check_is_fitted(self)
        self.lifetimes = [x[:,4]-x[:,3] for x in self.diags_]
    
    def get_midlife_coords(self):
        check_is_fitted(self)
        self.midlife_coords = [(x[:,4]+x[:,3])/2 for x in self.diags_]
        
    def get_pers_mag(self):
        check_is_fitted(self)
        self.pers_mag = [np.sum((-1)**(x[:,2])*(np.exp(-x[:,3])-np.exp(-x[:,4]))) for x in self.diags_]
    
    def get_pers_stats(self):
        """
        Get persistence statistics for each image, according to `Topological approaches to skin disease analysis`, along with 
            persistent entropy and ALPS statistics, constituting an embedding into 32-dimensional Euclidean space.
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
                
