from setuptools import setup, find_packages

VERSION = '0.4.5'
DESCRIPTION = "detectda - detecting features in videos using TDA"
LONG_DESCRIPTION = "detectda - a cubical persistent homology package for the detection and hypothesis testing of features in greyscale videos"

setup(
	name="detectda",
	version = VERSION,
	author = "Andrew M. Thomas",
	author_email = "<me@andrewmthomas.com>",
	description = DESCRIPTION,
	long_description = LONG_DESCRIPTION,
	packages=find_packages(),
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
		'console_scripts': [
			'identify_polygon = detectda.idpo:identify_polygon'	
		]	
	}
)
