from ..imgs import ImageSeriesPickle
from ..hypo import VacuumSeries
import pickle

def test_hypo():
    impol = ImageSeriesPickle('detectda/tests/test_video.pkl', div=32)
    impol.fit(sigma=4)
    impol.get_alps()
    
    G = open('detectda/tests/test_video_vacuum.pkl', 'rb')
    tv_vacuum = pickle.load(G)['video']
    
    impol_vac = VacuumSeries(tv_vacuum, observed_ImageSeries=impol, div=32, n_jobs=4)
    impol_vac.fit(convert_to_int=True)
    impol_vac.transform(499, "alps")
    
    impol_vac.plot_hypo()
    
def test_hypo2():
    impol = ImageSeriesPickle('detectda/tests/test_video.pkl', div=32)
    impol.fit(sigma=4)
    impol.get_degp_totp()
    
    G = open('detectda/tests/test_video_vacuum.pkl', 'rb')
    tv_vacuum = pickle.load(G)['video']
    
    impol_vac = VacuumSeries(tv_vacuum, observed_ImageSeries=impol, div=32, n_jobs=4)
    impol_vac.fit(convert_to_int=True)
    impol_vac.transform(499, "degp_totp")
    
    impol_vac.plot_hypo()
    
def test_hypo3():
    impol = ImageSeriesPickle('detectda/tests/test_video.pkl', div=32)
    impol.fit(sigma=4)
    impol.get_pers_entr(neg=False)
    
    G = open('detectda/tests/test_video_vacuum.pkl', 'rb')
    tv_vacuum = pickle.load(G)['video']
    
    impol_vac = VacuumSeries(tv_vacuum, observed_ImageSeries=impol, div=32, n_jobs=4)
    impol_vac.fit(convert_to_int=True)
    impol_vac.transform(499, "pers_entr")
    
    impol_vac.plot_hypo()    