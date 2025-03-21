# Changelog

## v0.5.4 (3/20/2025)

## Added

- proc_pers_im method for ImageSeriesPlus to process "significant" betas according to bclr as in Thomas et al (2025)
- plot_pi_sig method for ImageSeriesPlus to plot PD points corresponding to these "significant" betas on the image

## Fixed

- calc_close had incorrect indexing
- Issue with plot_im frame argument
- how ImageSeriesPlus dealth with infinite values in calculating PH

## Changed

- Removed underscore following 'self.dfs_' as this is an attribute meant to be viewed

## v0.5.3 (8/30/2024)

## Fixed 

- Issue with incorrect calculation with PD thresholding
- get_cc had a problem with conditional logic that has been fixed
- Plot_im for ImageSeriesPlus now displays correct values

## v0.5.2 (8/1/2024)

### Added

- ALPS plots (cf. Crozier et. al, 2024)
- Modified README.md

### Fixed

- Versioning issue

## v0.5.0 (7/25/2024)

### Added

- Plotting functionality for ImageSeriesPlus class
- Easy dimension information for get_lifetimes and get_midlife_coords
- A method for deriving persistence images from the images themselves
- Helper function for getting the connected component of a point

### Fixed

- Fixed issue that was occurring with ImageSeriesPlus class and the locations of the persistence pairs
- Error is raised if a video with a trivial image is given.

## v0.4.6 (6/17/2024)

### Fixed

- Added in imagecodecs package as a requirement to fix an existing issue
- Updated package to display versioning more dynamically

