from setuptools import setup, find_packages

VERSION = '0.4.3'
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
		'shapely >= 2.0.1',
		'joblib',
		'scikit-image',
		'scikit-learn >= 0.23.1',
		'numpy',
		'tqdm',
        'pandas',
		'matplotlib',
		'opencv-contrib-python',
        'scipy'
	],
	keywords = ['tda', 'cubical', 'image processing'],
	classifiers = [
		'Operating System :: MacOS',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python'
	],
	entry_points={
		'gui_scripts': [
			'identify_polygon = detectda.idpo:identify_polygon'	
		]	
	}
)
