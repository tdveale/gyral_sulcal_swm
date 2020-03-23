# import libraries
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from nibabel import freesurfer as nfs
import numpy as np

# Arguments
__description__ = '''
This script takes ?h.curv and ?h.aparc.annot files and creates masks for gyral crowns, sulcal walls and sulcal fundi.
If the annot option is specified, then gyral crown, sulcal wall and sulcal fundi masks will be created within each ROI.
If the annot and metric options are specified, then mean gyral crown, sulcal wall and sulcal fundi measure will be extracted, 
for each ROI, for the input metric (i.e. DWI data resampled on WM surface using mri_vol2surf, but could be another modality).
'''

# collect inputs
parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                        description=__description__)


parser.add_argument('-c', '--curv',
                    help='Path to curvature file. Must be 1 hemisphere only (i.e. ~/brains/s01/surf/lh.curv)',
                    required=True)
parser.add_argument('-a', '--annot',
                    help='Path to aparc annot file (cortical ROIs). Must be 1 hemisphere only '
                         '(i.e. ~/brains/s01/label/lh.aparc.annot)',
                    required=False)
parser.add_argument('-m', '--metric',
                    help='File containing metric to average across gyral crown/sulcal wall/sulcal fundi within '
                         'each ROI. Currently must be a .mgz or .mgh file (i.e. swm sampled data)',
                    required=False)
parser.add_argument('-r', '--rois',
                    help='List of ROIs to use. If not specified, default from SWM work will be used.',
                    required=False)
parser.add_argument('-o', '--output_csv',
                    help='Filepath and filename to save the mean and SD of crowns, walls and sulci for input metric.'
                         'Default output path is in the metric folder.',
                    required=False)
parser.add_argument('-s', '--save_data',
                    help='Save the raw vertices data. NOT YET IMPLEMENTED',
                    required=False)
args = parser.parse_args()

plotting = True

# get file basename
curv_root = args.curv.split('.')[0]

# read curvature in - read_morph function reads files such as ?h.curv and ?h.thickness
curv = nfs.read_morph_data(args.curv)

# find vertices that represent gyral crown (<33rd percentile), sulcal wall (34-66th percentile)
# and sulcal fundi (>66th percentile)
crown_vert = curv < np.percentile(curv, 33)
wall_vert = (curv >= np.percentile(curv, 33)) & (curv <= np.percentile(curv, 66))
sulc_vert = curv > np.percentile(curv, 66)

# write these masks to new morphology files
nfs.write_morph_data(curv_root + '.' + 'gyral_crown', crown_vert)
nfs.write_morph_data(curv_root + '.' + 'sulcal_wall', wall_vert)
nfs.write_morph_data(curv_root + '.' + 'sulcal_fundi', sulc_vert)

# combine these into one array
gyral_wall_sulc = np.zeros(curv.shape)
gyral_wall_sulc[curv < np.percentile(curv, 33)] = 1
gyral_wall_sulc[(curv >= np.percentile(curv, 33)) & (curv <= np.percentile(curv, 66))] = 2
gyral_wall_sulc[curv > np.percentile(curv, 66)] = 3
# write combined crown/wall/sulc to new morphology file (view all at once)
nfs.write_morph_data(curv_root + '.' + 'crown_wall_sulc', gyral_wall_sulc)


if args.annot:
    # read_annot function reads .annot freesurfer files
    annot = nfs.read_annot(args.annot)

    # state each ROI
    if args.rois:
        apriori_rois = args.rois
    else:
        apriori_rois = ["entorhinal", "postcentral", "superiortemporal", "fusiform", "lateraloccipital",
                          "middletemporal", "posteriorcingulate", "inferiorparietal", "parahippocampal",
                          "precentral", "cuneus", "inferiortemporal", "paracentral", "precuneus",
                          "superiorparietal"]
        print('Using default ROIs: ' + str(apriori_rois))

    # find indices of apriori rois (label values)
    indx = [np.where(np.array(annot[2]) == i)[0][0] for i in apriori_rois]

    # get rois with crown, wall and sulcal masks all in nested dictionary
    roi_dict = {}
    for i in range(0, len(apriori_rois)):
        roi_dict[apriori_rois[i]] = {}
        # store roi index from annot file
        roi_dict[apriori_rois[i]]['roi_index'] = indx[i]
        # get individual masks for that roi
        roi_dict[apriori_rois[i]]['crown_mask'] = (curv < np.percentile(curv, 33)) & (annot[0] == indx[i])
        roi_dict[apriori_rois[i]]['wall_mask'] = (curv >= np.percentile(curv, 33)) & \
                                                  (curv <= np.percentile(curv, 66)) & (annot[0] == indx[i])
        roi_dict[apriori_rois[i]]['sulcus_mask'] = (curv > np.percentile(curv, 66)) & (annot[0] == indx[i])

        # combine all masks within the roi
        i_gyral_wall_sulc = np.zeros(curv.shape)
        i_gyral_wall_sulc[(curv < np.percentile(curv, 33)) &
                        (annot[0] == indx[i])] = 1
        i_gyral_wall_sulc[(curv >= np.percentile(curv, 33)) & (curv <= np.percentile(curv, 66)) &
                        (annot[0] == indx[i])] = 2
        i_gyral_wall_sulc[(curv > np.percentile(curv, 66)) &
                        (annot[0] == indx[i])] = 3
        roi_dict[apriori_rois[i]]['crown_wall_sulc'] = i_gyral_wall_sulc

    # to just view one ROI for figures etc
    # a = roi_dict['superiortemporal']['crown_wall_sulc']
    # nfs.write_morph_data(curv_root + '.' + 'crown_wall_sulc_suptemporal', a)

    # get crown/wall/sulci measures of input metric within in ROI
    if args.metric:
        import os
        from collections import OrderedDict
        import pandas as pd
        # load in swm .mgz and reshape to get in same dimensions as curv
        metric_obj = nfs.mghformat.load(args.metric)
        metric_data = metric_obj.get_data()
        metric_data = metric_data.flatten()
        # use roi crown, wall and sulc masks to get these values within each roi
        # create list of dictionaries then output into pandas dataframe
        roi_list = []
        for i_roi, i_gws in roi_dict.iteritems():
            i_dict = OrderedDict()
            i_dict['File'] = args.metric
            i_dict['Region'] = i_roi
            # Get mean and standard deviations of metric in crown, wall and sulci of current ROI
            i_dict['Crown_mean'] = np.mean(metric_data[roi_dict[i_roi]['crown_mask']])
            i_dict['Crown_sd'] = np.std(metric_data[roi_dict[i_roi]['crown_mask']])
            i_dict['Wall_mean'] = np.mean(metric_data[roi_dict[i_roi]['wall_mask']])
            i_dict['Wall_sd'] = np.std(metric_data[roi_dict[i_roi]['wall_mask']])
            i_dict['Sulcus_mean'] = np.mean(metric_data[roi_dict[i_roi]['sulcus_mask']])
            i_dict['Sulcus_sd'] = np.std(metric_data[roi_dict[i_roi]['sulcus_mask']])
            # append this ROI dictionary to list
            roi_list.append(i_dict)

        # output to a csv file
        roi_gws_df = pd.DataFrame(roi_list)
        if args.output_csv:
            roi_gws_df.to_csv(args.output_csv, index=False)
        else:
            output_csv = os.path.splitext(args.metric)[0] + '_gyral_wall_sulcal_metrics.csv'
            roi_gws_df.to_csv(output_csv, index=False)


# plotting for histogram
if plotting:
    import matplotlib.pyplot as plt
    # double check plots
    plt.figure(0)
    plt.hist(curv, 1000, color='b')
    plt.axvline(x=np.percentile(curv, 33), color='r')
    plt.axvline(x=np.percentile(curv, 66), color='r')
    plt.ylabel('Num Vertices')
    plt.xlabel('Curvature')
    plt.title('Curvature with 33rd and 66th Percentiles')
    plt.savefig(curv_root + '.histogram_curvature.png', format='png', dpi=1000)

    if args.metric:
        # plot DTI/NODDI values against curvature here or export them all as csv file
        plt.figure(1)
        plt.scatter(curv, metric_data)
        plt.savefig(os.path.splitext(args.metric)[0] + '_curv_vs_metric.png', format='png', dpi=1000)