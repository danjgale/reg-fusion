
import argparse

def _cli_parser():
    """Reads command line arguments and returns input specifications"""
    parser = argparse.ArgumentParser()
    # Original flags
    parser.add_argument('-s', type=str, metavar='input_vol',
                        help="Absolute path to input volume. Input should be "
                             "in nifti format")
    parser.add_argument('-o', type=str, metavar='output_dir',
                        help="Absolute path to output directory.")
    parser.add_argument('-p', type=str, metavar='template_type', 
                        help="Type of volumetric template used in index files "
                             "creation. Use 'MNI152_norm' or 'Colin27_norm' for "
                             "RF-M3Z MNI152-to-fsaverage or "
                             "Colin27-to-fsaverage mappings, 'MNI152_orig' or "
                             "'Colin27_orig' for the respective RF-ANTs "
                             "mappings.\n"
                             "[ default: MNI152_orig ]")
    parser.add_argument('-n', type=int, metavar='num_of_sub',
                        help="Number of subjects used in creating the average "
                             "mapping. For example, setting '-n 50' means the "
                             "mapping used was averaged across 50 subjects. "
                             "Setting this to 0 will make the script use the "
                             "mapping averaged across all subjects.\n"
	                         "[ default: 0 ]")
    parser.add_argument('-r',  type=str, metavar='RF_type',
                        help="Type of Registration Fusion approaches used to "
                             "generate the mappings (RF_M3Z or RF_ANTs). " 
                             "RF-M3Z is recommended if data was registered " 
                             "from subject's space to the volumetric atlas " 
                             "space using FreeSurfer. RF-ANTs is recommended " 
                             "if such registrations were carried out using " 
                             "other tools, especially ANTs.\n"
                             "[ default: RF_ANTs ]")
    parser.add_argument('-d', type=str, metavar='map_dir',
                        help="Absolute path to mapping directory. The mappings "
                             "are the average mappings generated in Registration "
                             "Fusion approaches. The average mapping using all "
                             "GSP subjects are used by default.\n"
                             "[ default: $WARP_DIR ]")
    parser.add_argument('-i', type=str, metavar='interp', 
                        help="Interpolation (linear or nearest)\n"
                             "[ default: linear ]")
    parser.add_argument('-f', type=str, metavar='freesurfer_dir', 
                        help="Absolute path to FreeSurfer directory (this "
                             "will overwrite the default \$FREESUFER_HOME). "
                             "This setting may affect the version of FreeSurfer "
                             "is called, but not the version of the "
                             "warps/mappings used.")
    # New flags
    parser.add_argument('-t', type=str, metavar='out_type',
                        help="File types of the output surface files. Can "
                             "either be 'nifti' or 'gifti'. The original "
                             "registration fusion package outputs NIfTI, "
                             "'nii.gz', but in most cases GIfTI, either " 
                             "'func.gii' or 'label.gii' may be more applicable. "
                             "If 'label.gii' is selected, interpolation is "
                             "forced to 'nearest' and a warning is raised.\n"
                             "[ default: nii.gz ]")
    return parser.parse_args()


def main():
    params = vars(_cli_parser())