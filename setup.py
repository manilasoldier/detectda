from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = "detectda - detecting features in videos using TDA"
LONG_DESCRIPTION = "detectda - a cubical persistent homology package for the detection and hypothesis testing of features in greyscale videos"

setup(
	name="detectda",
	version = VERSION,
	author = "Andrew M. Thomas",
	author_email = "<me@andrewmthomas.com>",
	description = DESCRIPTION,
	long_description = LONG_DESCRIPTION,
	package=find_packages(),
	install_requires=[
		'gudhi',
		'shapely',
		'joblib',
		'skimage',
		'sci-kit-learn >= 0.23.1',
		'numpy',
		'tqdm',
		'matplotlib',
		'cv2'
	],
	keywords = ['tda', 'cubical'],
	classifiers = [
		'Operating System :: MacOS :: MacOS X',
		'Programming Language :: Python'
	]
)
