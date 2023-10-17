from joblib import Parallel, delayed
from . import imgs
from . import hlpr as _dh
import numpy as np
from sklearn.utils.validation import check_is_fitted
import matplotlib.pyplot as plt
import scipy.stats as stat

class VacuumSeries(imgs.ImageSeries):
    """
    Functionality to generate vacuum region videos for multiple hypothesis testing.
    """
    def __init__(self, vacuum_video, observed_ImageSeries, 
                 parametric=True, div=1, n_jobs=None):
        super().__init__(vacuum_video, None, div=div, n_jobs=n_jobs)
    
        if not isinstance(observed_ImageSeries, imgs.ImageSeries):
            raise TypeError("Argument must be of class Image Series")
         
        self.observed_ImageSeries = observed_ImageSeries
        #last two elements of array corresponding to the shape
        self.size = self.observed_ImageSeries.video.shape[-2:] 
        self.parametric = parametric

    def fit(self, convert_to_int=False):
        """
        Fits the Poisson mle for the vacuum region if parametric==True
        
        Else, it fits the empirical probability mass function.
        """
        if convert_to_int:
            emp_vals = np.ndarray.astype(self.video.flatten(), "int64")
        else:
            if self.video.dtype.kind != "i":
                raise TypeError("Vacuum video must be of signed integer data type. If you would like to convert \
                                to signed integer data type, rerun self.fit with convert_to_int=True")
            else:
                emp_vals = self.video.flatten()
        
        bin_vals = np.bincount(emp_vals)
        self.n_ = len(emp_vals)
        self.probs_ = bin_vals/np.sum(bin_vals)
        self.vals_ = np.arange(len(bin_vals))
        self.mle_ = np.sum(self.probs_ * self.vals_)
    
    def kolm_dist(self):
        """
        Check how far the empirical distribution of vacuum values is from Poisson 
        with parameter equal to mle, in terms of the Kolmogorov distance
        
        Uses the DKW inequality with the tight constant = 2 for Poisson testing.
        """
        check_is_fitted(self)
        emp_dist = stat.rv_discrete(values=(self.vals_, self.probs_))
        ks_dist = np.max([np.abs(emp_dist.cdf(k)-stat.poisson.cdf(k, self.mle_))
                               for k in range(np.min(self.vals_), np.max(self.vals_)+1)])
        p_val = 2*np.exp(-2*self.n_*ks_dist**2)
        self.ks_test = {'p_val': p_val, 'ks_dist': ks_dist}
        print(self.ks_test)

    def gen_images(self, n):
        "Generate and return a random image according to estimated null distribution"
        check_is_fitted(self)
        if self.parametric:
            return np.random.poisson(self.mle_, size=(n, *self.size))
        else:
            return np.random.choice(self.vals_, size=(n, *self.size), p=self.probs_)
            
    def transform(self, n, func="pers_entr", seed=0, alpha=0.05, conservative=True):
        """
        Collects p-values and rejections for based off n Monte Carlo simulations...
        """
        check_is_fitted(self.observed_ImageSeries)
        np.random.seed(seed)
        if func not in ("pers_entr", "alps", "degp_totp"):
            raise ValueError("func must be pers_entr, alps, or degp_totp")
        
        self.images = self.gen_images(n)
        def proc_diag(x):
            y = _dh.fitsmoo(x, polygon = self.observed_ImageSeries.polygon,
                           sigma = self.observed_ImageSeries.sigma_,
                           max_death_pixel_int=self.observed_ImageSeries.max_death_pixel_int_)
            return eval("_dh."+func)(y[y[:,3].astype(bool),2]) #make sure columns inside polygon are chosen...
        
        self.mc_vals = Parallel(n_jobs = self.n_jobs)(delayed(proc_diag)(im) for im in self.images)
        eval("self.observed_ImageSeries.get_"+func)()
        self.obs_vals = eval("self.observed_ImageSeries."+func)
        self.__pvals = np.fromiter((_dh.pg0(np.insert(self.mc_vals, 0, val)) for val in self.obs_vals), float)
        self.func = func
        
        #Here add in the rejections from the BH procedure
        #See Catalysis Nanoparticles Multiple Testing.ipynb
        self.reject_dict = _dh.calc_reject(self.__pvals, self.obs_vals, alpha=alpha, conservative=conservative)
        self.alpha=alpha
        
    def adjust_alpha(self, alpha, conservative=True):
        """
        Adjust p-values based on a different alpha value.

        """
        self.reject_dict = _dh.calc_reject(self.__pvals, self.obs_vals, alpha=alpha, conservative=conservative)
        self.alpha=alpha
       
    def plot_hypo(self):
        """
        Plots hypothesis testing sequence. 
        """
        begins, ends = _dh.get_be(self.reject_dict["reject_bool"])
        if self.func == "pers_entr":
            plt.plot(-self.obs_vals, lw=0.7, color="black")
            plt.scatter(x=self.reject_dict["reject_ind"], y=-self.obs_vals[self.reject_dict["reject_ind"]], 
                        color="red", s=2)
            
            ####Note this plot becomes really bad when there are ties...
            if self.reject_dict["reject_thr_ind"]==None:
                print("No hypotheses were rejected.")
            else:
                plt.axhline(y=-self.obs_vals[self.reject_dict["reject_thr_ind"]], color="black", linestyle="dashed", linewidth=0.75)
            
            plt.hlines(y=-np.repeat(np.max(self.obs_vals)+0.1, len(begins)), xmin=begins, xmax=ends, color="black")
            #should adjust this 0.1 to be different based on scale...
            plt.xlabel(r'$k$')
            plt.ylabel(r'$H(A(I_{k}))$')
            plt.title("Persistent entropy across frames")
        
        else:
            plt.plot(self.obs_vals, lw=0.7, color="black")
            plt.scatter(x=self.reject_dict["reject_ind"], y=self.obs_vals[self.reject_dict["reject_ind"]], 
                        color="red", s=2)
            
            ####Note this plot becomes really bad when there are ties...
            if self.reject_dict["reject_thr_ind"]==None:
                print("No hypotheses were rejected.")
            else:
                plt.axhline(y=self.obs_vals[self.reject_dict["reject_thr_ind"]], color="black", linestyle="dashed", linewidth=0.75)
            
            plt.hlines(y=np.repeat(np.max(self.obs_vals)+0.1, len(begins)), xmin=begins, xmax=ends, color="black")
            #should adjust this 0.1 to be different based on scale...
            plt.xlabel(r'$k$')
            if self.func == "alps":
                plt.ylabel(r'$\Delta(A(I_{k}))$')
                plt.title("ALPS statistic across frames")
            elif self.func == "degp_totp":
                plt.ylabel(r'$L_1(A(I_{k}))$')
                plt.title("Lifetime sum across frames")
        
        
            
        
