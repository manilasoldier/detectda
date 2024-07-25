from ..imgs import ImageSeriesPlus
import numpy as np
import pytest
from math import e, atan, pi

sim_im = np.load("test_imgs_plus.npy")

dtda_sim = ImageSeriesPlus(sim_im)
dtda_sim.fit(sigma=2)
dtda_sim.convert_to_df()
dtda_df = dtda_sim.dfs_[0]

ll1 = dtda_df[dtda_df['hom_dim']==1].iloc[-1]
assert ll1['x_coord'] == 70 and ll1['y_coord'] == 40

lifetimes1 = np.array([0.29274806235493894, 0.31731007160275015, 0.3413545354456121, 
                       0.34999902104301595, 1.0711503226171546, 2.321703449415376])

dtda_sim.get_lifetimes()
np.testing.assert_almost_equal(np.sort(dtda_sim.lifetimes[1][0])[-6:], lifetimes1, 12)

dtda_sim.get_midlife_coords()
last_mid = pytest.approx(1.2433755, abs=1e-6)
assert dtda_sim.midlife_coords[1][0][-1] == last_mid

test_im = np.array([[5, 18, 14, 24, 22], [6, 1, 12, 25, 4], [13, 19, 10, 23, 21],
                   [8, 20, 3, 2, 15], [17, 9, 7, 16, 11]])

dtda_test = ImageSeriesPlus(test_im)
dtda_test.fit(sigma=0)

dtda_test.get_pers_mag()
pm = (e**(-1)-e**(-25)) + (e**(-4)-e**(-21)) + (e**(-2)-e**(-10)) + (e**(-8)-e**(-9)) - (e**(-24)-e**(-25)) - (e**(-13)-e**(-20))
true_pers_mag = pytest.approx(pm, abs=1e-6)
assert dtda_test.pers_mag[0] == true_pers_mag

def px(arr,x,y):
    rho_xy = 0
    for (b,l) in arr:
        rho_xy += atan(0.5*l)*e**(-(1/2)*((b-x)**2+(l-y)**2))/(2*pi)
    
    return rho_xy

dtda_test.get_pers_im(3,3,dim=0)
arr = [(8, 1), (2, 8), (4, 17), (1, 24)]
true_pi = np.array([])
for y in dtda_test.lifet_bd:
    for x in dtda_test.birtt_bd:
        true_pi = np.append(true_pi, px(arr, x, y))

np.testing.assert_almost_equal(dtda_test.pis[0], true_pi, 12)