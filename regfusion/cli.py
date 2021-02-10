""" """
import argparse
from regfusion.main import vol_to_fsaverage

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
                        help= "Type of volumetric template used in index files. "
                              "Use 'MNI152_orig' or 'Colin27_orig' when "
                              "`rf_type` is `RF_ANTs`. Use 'MNI152_norm' or "
                             "'Colin27_norm' when `rf_type` is 'RF_M3Z'. An "
                             "exception is raised if `template_type` does not "
                             "correspond to the correct `rf_type`. Ensure that "
                             "the template matches the standard space of "
                             "`input_img` (i.e., use MNI152_* if `input_img` "
                             "is in MNI152-space) Default: MNI152_orig ")
    parser.add_argument('-r',  type=str, metavar='RF_type',
                        help="Type of Registration Fusion approaches used to "
                             "generate the mappings (RF_M3Z or RF_ANTs). " 
                             "RF_M3Z is recommended if data was registered " 
                             "from subject's space to the volumetric atlas " 
                             "space using FreeSurfer. RF_ANTs is recommended " 
                             "if such registrations were carried out using " 
                             "other tools, especially ANTs. Default: RF_ANTs")
    parser.add_argument('-i', type=str, metavar='interp', 
                        help="Interpolation (linear or nearest). If "
                             "-g is label, then interpolation is always set "
                             "to nearest and a warning is raised. Default: "
                             "linear")
    # New flags
    parser.add_argument('-g', type=str, metavar='gifti_type',
                        help="File types of the output gifti files (func or "
                             "label). Default: func ")
    return parser.parse_args()


def main():
    params = vars(_cli_parser())
    
    vol_to_fsaverage(
        input_img=params['s'], 
        out_dir=params['o'], 
        template_type=params['p'],
        rf_type=params['r'], 
        interp=params['i'], 
        gifti_type=['g']
    )
