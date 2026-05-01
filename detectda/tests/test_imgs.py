from ..imgs import ImageSeriesPickle, ImageSeries
import numpy as np
from shapely import Polygon
from skimage import filters

pe = np.array([4.90758802, 4.84366615, 4.79672213, 4.9310114 , 4.86296057,
       4.88156392, 4.75650802, 4.79145051, 4.79556931, 4.88714277,
       4.91586817, 4.86077775, 4.89945409, 4.83364701, 4.80827412,
       4.89387421, 4.92383635, 4.77162152, 4.67953168, 4.89484772,
       4.92423715, 4.89481176, 4.82375763, 4.82896582, 4.87950407,
       4.95514917, 4.872495  , 4.79101853, 4.88146947, 4.90137013,
       4.91472007, 4.85819532, 4.90140569, 4.81243429, 4.79725316,
       4.85590564, 4.81138296, 4.85232681, 4.82383763, 4.91760363,
       4.82611144])

alps = np.array([2.59794337, 2.48579956, 2.4367223 , 2.38327375, 2.34691756,
       2.36258826, 2.42022348, 2.515211  , 2.46416331, 2.27978552,
       2.33809275, 2.58168346, 2.42894871, 2.69966709, 2.67129198,
       2.4283771 , 2.39576331, 2.48852051, 2.52603836, 2.57998083,
       2.3526314 , 2.53882635, 2.60256853, 2.5431527 , 2.78627166,
       2.13978055, 2.41729655, 2.67569573, 2.40065213, 2.38203093,
       2.22547545, 2.21417171, 2.38299514, 2.68615962, 2.63722442,
       2.43138252, 2.72322118, 2.54168007, 2.64198983, 2.67092905,
       2.57721082])

def test_ps():
    impol = ImageSeriesPickle('detectda/tests/test_video.pkl', div=32, n_jobs=None)
    impol.fit(sigma=2)
    impol.get_pers_entr(neg=False)
    impol.get_alps()
    np.testing.assert_almost_equal(impol.alps, alps, 7)
    np.testing.assert_almost_equal(impol.pers_entr, pe, 7)

test_poly2 = Polygon([[1, 20], [10, 20], [10, 30], [1, 30]])
test_im2 = np.full((51, 51), 1)
test_im2[25,5] = 0 
test_im2[25,6] = 0
test_im2[25,45] = 0.5
test_im2 = np.round(filters.gaussian(test_im2,1, preserve_range=True),1)
test_im2[25,6] = 0.8

def test_poly():
    test_dtda2 = ImageSeries(test_im2, test_poly2)
    test_dtda2.fit(sigma=0)
    test_dtda2.plot_im(0)
