from joblib import Parallel, delayed
from . import imgs
from . import hlpr as _dh
import numpy as np
from sklearn.utils.validation import check_is_fitted
import scipy.stats as stat

class VacuumSeries(imgs.ImageSeries):
    """
    Functionality to generate vacuum region videos for multiple hypothesis testing...
    """
    def __init__(self, vacuum_video, observed_ImageSeries, 
                 parametric=True, div=1, n_jobs=None):
        super().__init__(vacuum_video, None, div=div, n_jobs=n_jobs)
    
        #Need to check that this works the way I'm intending it to       
        if not isinstance(observed_ImageSeries, imgs.ImageSeries):
            raise ValueError("Argument must be of class Image Series")
            
        self.observed_ImageSeries = observed_ImageSeries
        self.parametric = parametric
		
    def fit(self):
        """
        Fits the Poisson mle for the vacuum region if parametric==True
        
        Else it fits the empirical probability mass function.
        """
        emp_vals = np.ndarray.astype(self.vacuum_video.flatten(), "int64")
        bin_vals = np.bincount(emp_vals)
        self.probs_ = bin_vals/np.sum(bin_vals)
        self.vals_ = np.arange(len(bin_vals))
        self.mle_ = np.sum(self.probs_ * self.vals_)
    
    def kolm_dist(self):
        """
        Check how far the empirical distribution of vacuum values is from Poisson 
        with parameter equal to mle, in terms of the Kolmogorov distance
        """
        check_is_fitted(self)
        emp_dist = stat.rv_discrete(values=(self.vals_, self.probs_))
        self.ks_dist = np.max([np.abs(emp_dist.cdf(k)-stat.poisson.cdf(k, self.mle_))
                               for k in range(np.min(self.vals_), np.max(self.vals_)+1)])

    def gen_image(self):
        check_is_fitted(self)
        if self.parametric:
            self.noise_video = np.random.poisson(self.mle_, size=self.size)
        else:
            self.noise_video = np.random.choice(self.vals_, size=self.size, p=self.probs_)
            
    def transform(self, n, func="pers_entr", seed=0):
        check_is_fitted(self.observed_ImageSeries)
        np.random.seed(seed)
        if func not in ("pers_entr", "alps", "degp_totp"):
            raise ValueError("func must be pers_entr, alps, or degp_totp")
        
        def proc_diag():
            return eval("_dh."+func)(_dh.fitsmoo(self.gen_image(), 
                                                 polygon = self.observed_ImageSeries.polygon,
                                                 sigma = self.observed_ImageSeries.sigma_,
                                                 max_death_pixel_int= 
                                                 self.observed_ImageSeries.max_death_pixel_int_)[:,2])
        
        self.mc_vals = Parallel(n_jobs = self.n_jobs)(delayed(proc_diag) for i in range(n))
        self.obs_vals = eval("self.observed_ImageSeries.get_"+func+"()")
        self.p_vals = np.fromiter((_dh.pg0(np.insert(self.mc_vals, 0, val)) for val in self.obs_vals))
        
    def plot(self):
        """
        Implement plotting method as in the paper.
        """
        pass
        
        
        
            
        
