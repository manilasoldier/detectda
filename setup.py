from setuptools import setup, find_packages
import codecs

DESCRIPTION = "detectda - detecting features in videos using TDA"
with codecs.open("README.md", encoding="utf-8-sig") as f:
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
	packages=find_packages(where='detectda'),
        package_dir={"": "detectda"},
        package_data={"tests": ["test_imgs_plus.npy", "test_video.pkl",  "test_video_vacuum.pkl", "test_video.tif"]},
	install_requires=[
		'gudhi >= 3.6.0',
		'shapely >= 2.0.1',
		'joblib',
		'scikit-image >= 0.21.0',
		'scikit-learn >= 0.23.1',
		'numpy >= 1.24',
		'tqdm',
        'pandas',
		'matplotlib',
		'opencv-python',
        'scipy',
		'imagecodecs'
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
