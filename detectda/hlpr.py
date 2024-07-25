import numpy as np
from gudhi import CubicalComplex
from shapely.geometry import Point
from skimage import filters

def pg0(arr):
    """
    Calculate the proportion of the entire array which is at least as much as the first element.
    
    Parameters
    ----------
    arr : array_like
        Input array consists of numerical values.

    Returns
    -------
    prop : double
        The aforementioned proportion. 
    """
    try:
        prop = np.mean(arr >= arr[0])
    except TypeError:
        prop = np.mean(np.array(arr) >= arr[0])
        
    return prop

def getxy_col(arr, nrows):
    """
    Returns (x,y) image coordinates from column-major representation

    Parameters
    ----------
    arr : ndarray of shape (dim,)
        Should be a 1d numpy array
    nrows : int
        The number of rows in the 2d array. Should be factor of len(arr)

    Returns
    -------
    x : int
        The x-coordinate from column-major representation. Note that x-coordinate (for an image)
        corresponds to the column of the matrix
    y : int
        The y-coordinate from column-major representation. Note that y-coordinate (for an image)
        corresponds to the row of the matrix
    """
    assert isinstance(arr, np.ndarray), "Array must be numpy ndarray"
    y = (arr % nrows).astype(int)
    x = ((arr-y)/nrows).astype(int)
    return x,y
        

def std_video(video, flip=False):
    """
    Returns a video where each frame is standardized to have mean 0 pixel intensity with 
    standard deviation 1.

    Parameters
    ----------
    video : ndarray
        An array of shape (frames, rows, columns).
    flip : bool.
        Whether or not to invert the pixels of the video. The default is False.

    Returns
    -------
    ndarray
        The frame-standardized video of shape (frames, rows, columns).

    """
    v_mean = np.mean(video, axis=(1,2))
    v_std = np.std(video, axis=(1,2))
    v_means=np.transpose(np.tile(v_mean, (video.shape[1], video.shape[2],1)), (2,0,1))
    v_stds=np.transpose(np.tile(v_std, (video.shape[1], video.shape[2],1)), (2,0,1))
    return (-1)**(flip)*(video-v_means)/(v_stds)

def degp_totp(arr, p=1, inf=False):
    """
    Calculate degree-p total persistence from array of lifetimes.
    
    Parameters
    ----------
    arr: array_like
        Should be an array of persistence lifetimes, with nonnegative entries
    p : double, optional
        Exponent for degree p total lifetime. The default is 1.
    inf : bool, optional
        Whether or not to calculate infinity norm. The default is False.

    Raises
    ------
    ValueError
        Raises error if p less than 1

    Returns
    -------
    double
        The degree-p total persistence. 
        
    Notes
    ------
    The degree-p total (0-dimensional) persistence is specified as:
        
    .. math:: L_p(A(I)) := \sum_{(b,d) \in PD_0} (d-b)^p.
    
    If inf==True, this overwrites the chosen value of p.
    
    """
    if p < 1:
        raise ValueError("p must be >= 1")
    if inf:
        return np.max(arr)
    else: 
        return np.sum(arr**p)
    
def weight_func(arr):
    """
    Weight function for persistence image using defaults from Obayashi, Hiraoka, and Kimura (2018).

    Parameters
    ----------
    arr : array_like
        Should be an array of persistence lifetimes, with nonnegative entries

    Returns
    -------
    ndarray
        Array of weights corresponding to the given persistence lifetimes.

    """
    try:
        return np.arctan(0.5*(arr[:,1]))
    except IndexError:
        return np.arctan(0.5*(arr[1]))
    
def calc_close(pd, diffs, prox_arr, val=1):
    """
    Calculates the nearest point in the persistence diagram 

    Parameters
    ----------
    pd : ndarray of shape (n_barcodes, 2)
        A persistence diagram in (birth, death) coordinates. 
        Note that n_barcodes is the number of barcodes
    diffs : list/tuple of two elements
        Corresponds to the distance between elements of grid discretization, such as in 
        birtt_bd and lifet_bd in the gen_pers_im method of the ImageSeriesPlus class.
    prox_arr : ndarray of shape (m, 2)
        M observations in (birth, lifetime) coordinates corresponding to elements
        of the grid discretization used in calculation of the persistence image.
    val : float, optional
         The default is 1.

    Returns
    -------
    proxs : list
        List of all generators in the persistence diagram pd that lie in the Voronoi cell of 
        one of the elements of prox_arr. This is indicated with a non-zero entry in proxs.
    """
    proxs = []
    #Takes a pd with 
    for gen in pd:
        prox = 0
        for loc in prox_arr:
            #calculate whether or not a given point belongs to the voronoi cell 
            nv = max(abs(gen[1]-gen[0]-loc[1])/diffs[0], abs(gen[0]-loc[0])/diffs[1])
            #print(nv)
            if nv <= 1/2: 
                prox = val
        proxs += [prox]
    return proxs

def get_cc(point, bin_im):
    """
    Gets the connected component in the image bin_im containing the element "point".
    
    Parameters
    ----------
    point : list/tuple of 2 elements
        (x,y) coordinate point for image matrix
    bin_im : array_like
        Boolean array.

    Returns
    -------
    cc : list of lists
        list of elements in connected component containing point.

    """
    af = 1
    cc = [point]
    check_cc = [point]
    while af > 0:
        a = 0
        check_cc2 = []
        for pt in check_cc:
            for i in [-1, 1]:
                pt1 = [pt[0]+i, pt[1]]
                pt2 = [pt[0], pt[1]+i]
                if bin_im[pt[1], pt[0]+i] and pt1 not in cc:
                    cc = cc+[pt1]
                    check_cc2 = check_cc2+[pt1]
                    a += 1
                elif bin_im[pt[1]+i, pt[0]] and pt2 not in cc:
                    cc = cc+[pt2]
                    check_cc2 = check_cc2+[pt2]
                    a += 1
        af = a
        check_cc = check_cc2
    return cc

def get_be(arr):
    """
    Gets beginnings and ends of `True` sequences in Boolean arrays.
    
    Parameters
    ----------
    arr : array_like
        Boolean array

    Returns
    -------
    out: 2-tuple
      Tuple consisting of two arrays. Index-0 array consists of beginning of "True" sequences,
      and Index-1 array consists of ends of "True" sequences.

    """
    begins = []
    ends = []
    before = False
    for x in range(len(arr)):
        if before==False and arr[x]==True:
            begins.append(x)
            before=True
            if x==(len(arr)-1):
                ends.append(x)
        elif before==True and arr[x]==False:
            ends.append(x-1)
            before=False
        elif before==True and x==(len(arr)-1):
            ends.append(x)

    return (np.array(begins), np.array(ends))
    
def calc_reject(arr, val_arr, alpha=0.05, conservative=True):
    """
    Returns dictionary of index array, boolean array, rejection threshold index 
    array of indices of hypotheses that are rejected via BH procedure, and 
    boolean array of whether or not hypothesis is rejected. 
    
    Parameters
    ----------
    arr : array_like
        Array of probabilities (p-values) between 0 and 1.
    val_arr: array_like
        Array of values to break ties in p-values.
    alpha : value between 0 and 1, optional
        Signficance level for BH procedure. The default is 0.05.
    conservative: default = True
        Dictates whether or not conservative BH procedure is used. 

    Returns
    -------
    out: dict
        Dictionary containing information listed above. 
    """
    if alpha <= 0:
        raise ValueError("alpha must be > 0")
    
    N = len(arr)
    k = np.arange(1, N+1)
    if conservative:
        CN = np.sum(1/k)
    else:
        CN = 1
        
    li = k*alpha/(CN*N)
    
    arr_argsort = np.argsort(-val_arr)
    arr_sort = arr[arr_argsort]
    try:
        rej_max = np.where(arr_sort <= li)[0][-1] #largest element to reject
        return {"reject_ind": np.where(arr <= arr_sort[rej_max])[0], 
                "reject_bool": (arr <= arr_sort[rej_max]),
                "reject_thr_ind": arr_argsort[rej_max]}
    except IndexError:
        return {"reject_ind": [], 
                "reject_bool": np.repeat(False, len(arr)),
                "reject_thr_ind": None}
        
    
def block_sum(arr, m, div=1):
    """
    Sums adjacent blocks of m frames.
    """
    
    ran = int(np.floor(len(arr)/m-1)+1)
    block_arr = np.stack([np.sum(np.rint(arr[i*m:(i*m+m)]/div), axis=0) for i in range(ran)])
    return block_arr

def alps(arr):
	"""
    Get the ALPS statistic of an array of values, not all zero.
    """
    
	arr = np.sort(arr)
	sums = np.array([np.sum(arr <= y) for y in np.unique(arr)][::-1])
	arr = np.append([0], arr)
	integral = 0
	for i, s in enumerate(sums):
		integral += (arr[i+1]-arr[i])*np.log(s)

	return integral

def pers_entr(arr, neg=True):
	"""
    Gets persistence (shannon) entropy of an array of values, not all zero.
    """
    
	L_sum = np.sum(arr)
	Lmod = arr/L_sum
	if neg:
		a = 1
	else:
		a = -1

	return a*np.sum(Lmod*np.log(Lmod))

def pd_thresh_calc(diag, minv, maxv, dim="both", otsu=True):
    """
    Calculates best persistence preserving threshold as described in Chung and Day (2018).

    Parameters
    ----------
    diag : ndarray of shape (n_samples, 6)
        Persistence diagram object a la the output of the persmoo function
    minv : float
        Minimum threshold to consider.
    maxv : float
        Maximum threshold to consider.
    dim : str or int, optional
        Integer 0 or 1 corresponds to thresholding only based on dimension 0 and 1 persistence features.
        The default is "both", corresponding to both dimensions 0 and 1. 

    Returns
    -------
    float
        The best topology- and geometry-preserving threshold

    """
    if dim=="both":
        sub_diag = diag
    elif isinstance(dim, int):
        select = (diag[:, 2]==dim)
        sub_diag = diag[select,:]

    thrs_ = np.unique(sub_diag[:, [3,4]])
    thrs = thrs_[np.logical_and(thrs_ > minv, thrs_ < maxv)]
    
    Phi_t = []
    for thr in thrs:
        
        orig = np.logical_and(sub_diag[:, 3] <= thr, sub_diag[:, 4] > thr)
        minus = (sub_diag[:, 4] <= thr)
        plus = (sub_diag[:, 3] > thr)
        
        #Augmenting the persistence diagram in the case of emptiness
        if len(orig) >= 1:
            Phi_orig = (1/(np.sum(orig)+1))*np.sum((sub_diag[orig, 4]-thr)*(thr-sub_diag[orig, 3]))
        else:
            Phi_orig = (maxv-minv)
        
        if len(minus) >= 1:
            Phi_minus = np.sum((thr-sub_diag[minus, 4])/(sub_diag[minus, 4]-sub_diag[minus, 3]))
        else:
            Phi_minus = 1
            
        if len(plus) >= 1:
            Phi_plus = np.sum((sub_diag[plus, 3]-thr)/(sub_diag[plus, 4]-sub_diag[plus, 3]))
        else:
            Phi_plus = 1
            
        Phi_t.append(Phi_orig*Phi_minus*Phi_plus)
    
    return thrs[np.argmax(Phi_t)]

def persmoo(im, polygon=None, sigma=None):
    """
    Smooths, then fits 0 and 1-dimensional cubical persistence on an image. Returns other important information as well.
    
    Parameters
    ----------
    im : individual image, i.e. two-dimensional array
        Greyscale image on which sublevelset homology will be calculated.
    polygon : Shapely.Polygon object, optional
        Not necessary, only if one wants to restrict region to focus on. The default is None.
    sigma : smoothing parameter sigma, optional
        Smoothing parameter sigma for Gaussian filter. The default is None.

    Returns
    -------
    cu_tot : ndarray
        Array with positional and homology information, as follows:
        cu_pos:         #(x,y) coordinates of positive/negative cells (which create components/destroy loops)
        cu_pers:        #(dimension, birth, death)...
        cu_ex_inpoly:   #row indices of positive/negative cells located within specified polygon
    """
    #throughout this, infinite death becomes max pixel value...
    if sigma==None:
        pass	
    else:
        im = filters.gaussian(im, sigma=sigma, preserve_range=True)
    
    cu_comp = CubicalComplex(top_dimensional_cells=im) 
    cu_comp.compute_persistence(homology_coeff_field=2)
    cu_comp.persistence()
    
    #this step is necessary to get the ordering of the negative/positive cells correct
    cu_pers0 = cu_comp.persistence_intervals_in_dimension(0)
    cu_pers1 = cu_comp.persistence_intervals_in_dimension(1)
    
    dims = np.concatenate((np.repeat(1, cu_pers1.shape[0]), np.repeat(0, cu_pers0.shape[0])))
    cu_pers_ = np.r_[cu_pers1, cu_pers0]
    cu_pers = np.c_[dims, cu_pers_]
    nr, nc = im.shape
    
    #reassign infinite death pixels
    cu_pers[cu_pers==np.inf] = np.max(im)
    
    #get locations of cells...
    cu_pers_pairs_ = cu_comp.cofaces_of_persistence_pairs()
    
    #retrieves 'essential feature of dim-0', i.e. component of inf persistence
    ess_feat0 = cu_pers_pairs_[1][0]
    ess_featx, ess_featy = getxy_col(ess_feat0, nr)
    #this is to account for the specific cases when their is no 1st homology or no non-infinite generators of H_0
    if len(cu_pers_pairs_[0]) == 0:
        cu_pos = np.array([ess_featx, ess_featy]).T
    else:
        cu_pers_pair0 = cu_pers_pairs_[0][0] #regular persistence pairs of dim-0
        x_coords0, y_coords0 = getxy_col(cu_pers_pair0, nr)
        x_pos0 = np.append(x_coords0[:,0], ess_featx) #x coords of positive cells for dim-0, local minima
        y_pos0 = np.append(y_coords0[:,0], ess_featy) #y coords of positive cells for dim-0, local minima
        cu_pos0 = np.stack([x_pos0, y_pos0], axis=1)
        
        if len(cu_pers_pairs_[0]) == 2:
            cu_pers_pair1 = cu_pers_pairs_[0][1] ##regular persistence pairs of dim-1
            x_coords1, y_coords1 = getxy_col(cu_pers_pair1, nr)
            #concatenate x,y coords of negative cells for dim-1, local maxima
            cu_pos1 = np.stack([x_coords1[:,1], y_coords1[:,1]], axis=1)
            cu_pos = np.r_[cu_pos1, cu_pos0]
        else:
            cu_pos = cu_pos0
    
    if polygon==None:
    	    cu_ex_inpoly=np.repeat(True, len(cu_pers))
    else:
    	    pers_pts = (Point(x,y) for x,y in zip(cu_pos[:,0], cu_pos[:,1]))
    	    cu_ex_inpoly = [polygon.contains(pt) for pt in pers_pts]
    
    cu_tot = np.c_[cu_pos, cu_pers, cu_ex_inpoly]
    return cu_tot

def fitsmoo(im, polygon=None, sigma=None, max_death_pixel_int=True):        
	"""
	Smooths, then fits 0-dimensional cubical persistence on an image. 
	Returns information on:
		1) Location of positive cells, i.e. local minima (cu_pos, or index-0 and index-1 columns)
		2) Lifetime information (cu_totpers, or index-2 column)
		3) Whether or not a positive cell lies within the polygon (cu_ex_inpoly, or index-3 column)
	"""
    
	if sigma==None:
		pass	
	else:
		im = filters.gaussian(im, sigma=sigma, preserve_range=True)
	
	cu_comp = CubicalComplex(top_dimensional_cells=im)
	cu_comp.compute_persistence(homology_coeff_field=2)
	cu_pers = cu_comp.persistence_intervals_in_dimension(0)
	nr, nc = im.shape

	cu_pers_pairs_ = cu_comp.cofaces_of_persistence_pairs()
	cu_pers_pair0 = cu_pers_pairs_[0][0] #regular persistence pairs of dim-0
	ess_feat0 = cu_pers_pairs_[1][0] #retrieves 'essential feature of dim-0', i.e. component of inf persistence

	ess_featx, ess_featy = getxy_col(ess_feat0, nr)
	x_coords, y_coords = getxy_col(cu_pers_pair0, nr)

	x_pos = np.append(x_coords[:,0], ess_featx) #x coords of positive cells
	y_pos = np.append(y_coords[:,0], ess_featy) #y coords of positive cells
	cu_pos = np.stack([x_pos, y_pos], axis=1)

	#Now calculate whether each point is within our specified polygon
	if polygon==None:
		cu_ex_inpoly=np.repeat(True, len(cu_pers))
	else:
		pers_pts = (Point(x,y) for x,y in zip(x_pos, y_pos))
		cu_ex_inpoly = [polygon.contains(pt) for pt in pers_pts]

	if max_death_pixel_int==True:
		cu_pers[-1, 1] = np.max(im)
	else:
		cu_pers[-1, 1] = np.max(cu_pers[:-1, 1])

	cu_totpers = cu_pers[:,1]-cu_pers[:,0]
	return np.c_[cu_pos, cu_totpers, cu_ex_inpoly]
