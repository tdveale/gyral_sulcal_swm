# Methodology for NODDI and Curvature-based Investigation of Superficial White Matter in Young-Onset Alzheimer’s disease

Preprocessing information and code used to generate superficial white matter measures and curvature based segmentations.

## MRI Acquisition
Structural MRI sequences included 3D MPRAGE T1w volumetric MRI and 3D T2w volumetric MRI on a Siemens Trio TIM scanner using a 32 channel head coil. The diffusion MRI (dMRI) sequences was a multi-shell sequence optimised for NODDI (64, 32, and 8 diffusion-weighted directions at b=2000, b=700, and b=300 s/mm<sup>2</sup>; 14 interleaved b=0 s/mm<sup>2</sup>; voxel size 2.5 mm isotropic; TR/TE = 7000/92 ms). Field mappings were acquired to correct for susceptibility artefacts.

## Image Preprocessing

### Structural
Structural processing involved cortical reconstruction using FreeSurfer 6.0 (http://surfer.nmr.mgh.harvard.edu/), using both T1w and T2w images. The T1w image was skull-stripped using a brain mask from Geodesic Information Flow (GIF)<sup>1</sup>.

### Diffusion MRI
dMRI processing involved skull-stripping with a total intracranial volume mask using SPM12<sup>2</sup>, motion and eddy-current correction<sup>3</sup> and susceptibility correction using a combined approach of phase unwrapping and registration<sup>4</sup>. NODDI was fit using Accelerated Microstructural Imaging via Convex Optimisation (AMICO)<sup>5</sup>.

### SWM Extraction
NODDI metrics were registered and resampled onto the FreeSurfer T1w image with cubic interpolation using NiftyReg<sup>6</sup>. Due to the relatively low spatial resolution of dMRI sequences, NODDI metrics were sampled across the GM/WM boundary to better understand changes that could occur from neighbouring tissue types. NDI and ODI were sampled at 1mm (GM), 0mm (GM/WM boundary), -1mm (SWM) and -2mm (SWM/DWM) from the FreeSurfer WM surface.

Sampled NODDI metrics were then parcellated into cortical ROIs according to which FreeSurfer ROI’s each vertex was assigned to. Twelve a priori ROIs were chosen based on temporal, occipital and parietal regions affected in both clinical phenotypes within the YOAD group (tAD and PCA) <sup>7</sup>: entorhinal, superior temporal, fusiform, lateral occipital, middle temporal, posterior cingulate, inferior parietal, parahippocampal, cuneus, inferior temporal, precuneus and superior parietal cortices. Three ROIs less affected in tAD and PCA were also chosen: precentral, postcentral and paracentral cortices.

### Statistical Analysis

#### Whole ROI Analysis
For each NODDI metric in each ROI, the transition from GM (1mm) to SWM/DWM (-2mm) was modelled using a linear mixed effect (LME) model. The same model formula was used for each ROI and NODDI metric combination.

NDI or ODI was modelled using distance, group, distance-squared, distance x group, distance-squared x group and cortical thickness (fixed effects) while allowing the intercept and slope for each participant to vary (random effects). Independent variance of random effects between groups was allowed. Distance in the LME models were defined as the distance from the 1mm point (i.e. GM). Distance-squared was used as non-linear trends were observed when plotting the data. Average marginal effects (AME) between groups, at each distance point, were calculated from predicted values of LME models. AMEs represent the change in NODDI metric in the YOAD group with respect to controls, while holding other fixed effects constant. Multiple comparisons were corrected using for FDR across 15 ROIs.


#### Gyral Crown, Sulcal Wall and Sulcal Fundi Analysis
Four ROI measures at the depth of -1mm (SWM) were chosen to explore the effects of curvature-based sub-regions on NODDI metrics (ROIs: inferior parietal, middle temporal, precuneus and post central). These were split into gyral crowns, sulcal walls and sulcal fundi based on curvature values from FreeSurfer previously used in the literature<sup>8</sup> (gyral crowns < 33rd percentile; sulcal wall 33rd >= and =< 66th percentile; sulcal fundi > 66th percentile). See ```extract_gyri_sulci.py``` for code on extracting sub-regions. Due to unbalanced groups, linear mixed effect models were used to model changes in NDI or ODI across sub-regions of an ROI in each group, with each participant added as a random effect.

## References
1. Cardoso, M. J., Modat, M., Wolz, R., Melbourne, A., Cash, D., Rueckert, D., & Ourselin, S. (2015). Geodesic Information Flows: Spatially-Variant Graphs and Their Application to Segmentation and Fusion. IEEE Transactions on Medical Imaging, 34(9), 1976–1988. https://doi.org/10.1109/TMI.2015.2418298
2. Malone, I. B., Leung, K. K., Clegg, S., Barnes, J., Whitwell, J. L., Ashburner, J., ... Ridgway, G. R. (2015). Accurate automatic estimation of total intracranial volume: A nuisance variable with less nuisance. NeuroImage, 104, 366–372. https://doi.org/10.1016/j.neuroimage.2014.09.034
3. Andersson, J. L. R., & Sotiropoulos, S. N. (2016). An integrated approach to correction for off- resonance effects and subject movement in diffusion MR imaging. NeuroImage, 125, 1063– 1078. https://doi.org/10.1016/j.neuroimage.2015.10.019
4. Daga, P., Pendse, T., Modat, M., White, M., Mancini, L., Winston, G. P., ... Ourselin, S. (2014). Susceptibility artefact correction using dynamic graph cuts: Application to neurosurgery.
5. Daducci, A., Canales-Rodríguez, E. J., Zhang, H., Dyrby, T. B., Alexander, D. C., & Thiran, J. P. (2015). Accelerated Microstructure Imaging via Convex Optimization (AMICO) from diffusion MRI data. NeuroImage, 105, 32–44. https://doi.org/10.1016/j.neuroimage.2014.10.026
6. http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg
7. Firth, N. C., Primativo, S., Marinescu, R. V., Shakespeare, T. J., Suarez-Gonzalez, A., Lehmann, M., ... & Slattery, C. F. (2019). Longitudinal neuroanatomical and cognitive progression of posterior cortical atrophy. Brain, 142(7), 2082-2095.
8. Schilling, K., Gao, Y., Janve, V., Stepniewska, I., Landman, B. A., & Anderson, A. W. (2017). Confirmation of a gyral bias in diffusion MRI fiber tractography. Human Brain Mapping, 39(3),1–18. https://doi.org/10.1002/hbm.23936
