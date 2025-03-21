from setuptools import setup
import codecs

DESCRIPTION = "detectda - detecting features in videos using TDA"
with codecs.open("DESCRIPTION.md", encoding="utf-8-sig") as f:
    LONG_DESCRIPTION = f.read()
LONG_DESCRIPTION_TYPE = "text/markdown"
URL = "https://detectda.readthedocs.io/en/latest/"
VERSION = {}
with open("detectda/_version.py") as fp:
    exec(fp.read(), VERSION)

setup(
	name="detectda",
	version = VERSION['__version__'],
	author = "Andrew M. Thomas",
	author_email = "<me@andrewmthomas.com>",
	description = DESCRIPTION,
	long_description = LONG_DESCRIPTION,
        long_description_content_type = LONG_DESCRIPTION_TYPE,
        url = URL,
	packages=['detectda', 'detectda.tests'],
        package_data={"detectda.tests": ["test_imgs_plus.npy", "test_video.pkl",  "test_video_vacuum.pkl", "test_video.tif"]}, 
	install_requires=[
		'gudhi >= 3.8.0',
		'shapely >= 2.0.1',
		'joblib >= 1.3.2',
		'scikit-image >= 0.21.0',
		'scikit-learn >= 0.23.1',
		'numpy >= 1.24',
		'tqdm >= 4.64.0',
                'pandas >= 1.3.0',
		'matplotlib >= 3.7.2',
		'opencv-python >= 4.10.0',
                'scipy >= 1.10.1',
		'imagecodecs >= 2021.8.26'
	],
	keywords = ['tda', 'cubical', 'image processing'],
	classifiers = [
		'Operating System :: MacOS',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python'
	],
	entry_points={
		'console_scripts': [
			'identify_polygon = detectda.idpo:identify_polygon'	
		]	
	}
)
