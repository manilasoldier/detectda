import numpy as np
from gudhi import CubicalComplex
from shapely.geometry import Point, Polygon
from skimage import filters

def getxy_col(arr, nrows):
	"Returns (x,y) coordinates from column-major representation"
	y = (arr % nrows).astype(int)
	x = ((arr-y)/nrows).astype(int)
	return x,y

def degp_totp(arr, p=1, inf=False):
	"Note that if inf==True, this overwrites the chosen value of p"
	if p < 1:
		raise ValueError("p must be >= 1")
		
	if inf:
		return np.max(arr)
	else: 
		return np.sum(arr**p)

def get_be(arr):
    """
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
    out: dictionary of index array, boolean array, rejection threshold index
        array of indices of hypotheses that are rejected via BH procedure, and 
        boolean array of whether or not hypothesis is rejected. R
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
    "Sums adjacent blocks of m frames"
    ran = int(np.floor(len(arr)/m-1)+1)
    block_arr = np.stack([np.sum(np.rint(arr[i*m:(i*m+m)]/div), axis=0) for i in range(ran)])
    return block_arr

def alps(arr):
	"Get the ALPS statistic of an array of values, not all zero"
	arr = np.sort(arr)
	sums = np.array([np.sum(arr <= y) for y in np.unique(arr)][::-1])
	arr = np.append([0], arr)
	integral = 0
	for i, s in enumerate(sums):
		integral += (arr[i+1]-arr[i])*np.log(s)

	return integral

def pers_entr(arr, neg=True):
	"Gets persistence (shannon) entropy of an array of values, not all zero"
	L_sum = np.sum(arr)
	Lmod = arr/L_sum
	if neg:
		a = 1
	else:
		a = -1

	return a*np.sum(Lmod*np.log(Lmod))

def persmoo(im, polygon=None, sigma=None):
    #throughout this, infinite death becomes max pixel value...
    if sigma==None:
        pass	
    else:
        im = filters.gaussian(im, sigma=sigma, preserve_range=True)
        
    cu_comp = CubicalComplex(top_dimensional_cells=im) 
    cu_comp.compute_persistence(homology_coeff_field=2)
    cu_pers_ = cu_comp.persistence()
    cu_pers = np.array([(d, pers[0], pers[1]) for d, pers in cu_pers_])
    nr, nc = im.shape
    
    #reassign infinite death pixels
    cu_pers[cu_pers==np.inf] = np.max(im)
    
    #get locations of cells...
    cu_pers_pairs_ = cu_comp.cofaces_of_persistence_pairs()
    cu_pers_pair0 = cu_pers_pairs_[0][0] #regular persistence pairs of dim-0
    cu_pers_pair1 = cu_pers_pairs_[0][1] ##regular persistence pairs of dim-1
    ess_feat0 = cu_pers_pairs_[1][0] #retrieves 'essential feature of dim-0', i.e. component of inf persistence
    
    ess_featx, ess_featy = getxy_col(ess_feat0, nr)
    x_coords0, y_coords0 = getxy_col(cu_pers_pair0, nr)
    x_coords1, y_coords1 = getxy_col(cu_pers_pair1, nr)

    x_pos0 = np.append(x_coords0[:,0], ess_featx) #x coords of positive cells for dim-0, local minima
    y_pos0 = np.append(y_coords0[:,0], ess_featy) #y coords of positive cells for dim-0, local minima
    cu_pos0 = np.stack([x_pos0, y_pos0], axis=1)
    
    #concatenate x,y coords of negative cells for dim-1, local maxima
    cu_pos1 = np.stack([x_coords1[:,1], y_coords1[:,1]], axis=1)
    
    return cu_pers
    """
    3/11/23 NEED TO CREATE THIS FUNCTION
    SEE ALSO detectda_persmooTEST
    """

def fitsmoo(im, polygon=None, sigma=None, max_death_pixel_int=True):        
	"""
	Smooths, then fits 0-dimensional cubical persistence on an image. 
	Returns information on:
		1) Location of positive cells, i.e. local minima (cu_pos, or index-0 and index-1 columns)
		3) Lifetime information (cu_totpers, or index-2 column)
		4) Whether or not a positive cell lies within the polygon (cu_ex_inpoly, or index-3 column)
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
	"""
	cu_pos:         #(x,y) coordinates of positive cells (which create components)
	cu_totpers:     #persistence d-b of each row in cu_pers. Infinite barcode set to max of all barcodes
	cu_ex_inpoly:   #row indices of positive cells located within specified polygon
	"""