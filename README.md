For detecting and hypothesis testing of greyscale videos using cubical persistent homology.

As of 8/15/22, hypothesis testing functionality has not yet been implemented. Functionality on Windows machines cannot be guaranteed.

To use the identify_polygon script, run the script in the command line (after running python setup.py install, or similar). Enter the name of your .tif video (such as test_video.tif). Then right-click to select the boundaries of your polygon. Double-click to connectthe polygon together and press any key (such as "space" or "enter") to exit and save. Then you will name a .pkl file (you do not need to add the .pkl at the end) corresponding to your video (such as test_video.pkl). Finally, the file test_video.pkl (or whatever you have called it) contains the cropped video (according to the boundaries of your polygon) as well as the polygonal region of interest. You will then be able to usethis information to process your video with the persistent entropy or ALPS statistic---see "detectda demo.ipynb".
