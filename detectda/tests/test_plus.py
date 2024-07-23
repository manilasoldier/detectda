from ..imgs import ImageSeriesPlus
import numpy as np
import pytest

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
last_mid = pytest.approx(1.2433755, abs=0.00001)
assert dtda_sim.midlife_coords[1][0][-1] == last_mid

