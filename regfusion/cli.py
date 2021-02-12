""" """
import argparse
import re
import io
import os
from regfusion.main import vol_to_fsaverage

def _cli_msg():

    # read in version from __init__
    path = os.path.join(os.path.dirname(__file__))
    version = re.search(
        r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        io.open(f'{path}/__init__.py', encoding='utf_8_sig').read()
        ).group(1)

    borders = '-' * 67 + '\n'
    msg = (f'Using regfusion {version}, a Python implementation of:\n{borders}' 
            'Wu J, Ngo GH, Greve DN, Li J, He T, Fischl B, Eickhoff SB, Yeo BTT.\n' 
            'Accurate nonlinear mapping between MNI volumetric and FreeSurfer \n'
            'surface coordinate systems. Human Brain Mapping 39:3793–3808, 2018.\n'
            f'{borders}')
    return msg


def _cli_parser():
    """Reads command line arguments and returns input specifications"""
    parser = argparse.ArgumentParser()
    # Original flags
    parser.add_argument('-s', type=str, metavar='input_vol',
                        help="Absolute path to input volume. Input should be "
                             "in nifti format")
    parser.add_argument('-o', type=str, metavar='output_dir',
                        help="Absolute path to output directory")
    parser.add_argument('-p', type=str, metavar='template_type', default='MNI152_orig',
                        help="Type of volumetric template used in index files. "
                             "Use MNI152_orig or Colin27_orig when -r is "
                             "RF_ANTs. Use MNI152_norm or Colin27_norm when "
                             "-r is RF_M3Z. Otherwise, an exception is raised. "
                             "Ensure that the template matches the standard "
                             "space of -i (i.e., use MNI152_* if -i is "
                             "in MNI152-space). Default: MNI152_orig")
    parser.add_argument('-r',  type=str, metavar='RF_type', default='RF_ANTs',
                        help="Type of Registration Fusion approaches used to "
                             "generate the mappings (RF_M3Z or RF_ANTs). " 
                             "RF_M3Z is recommended if data was registered " 
                             "from subject's space to the volumetric atlas " 
                             "space using FreeSurfer. RF_ANTs is recommended " 
                             "if such registrations were carried out using " 
                             "other tools, especially ANTs. Default: RF_ANTs")
    parser.add_argument('-i', type=str, metavar='interp', default='linear',
                        help="Interpolation (linear or nearest). If "
                             "-g is label.gii, then interpolation is always set "
                             "to nearest and a warning is raised. Default: "
                             "linear")
    # New flags
    parser.add_argument('-t', type=str, metavar='out_type', default='nii.gz',
                        help="File type of surface files. nii.gz is true to "
                             "the original Wu et al (2018) implementation. "
                             "Note that gifti formats, either "
                             "func.gii or label.gii, are often preferred. "
                             "Default: nii.gz")
    return parser.parse_args()


def main():
    params = vars(_cli_parser())
    print(_cli_msg())
    vol_to_fsaverage(
        input_img=params['s'], 
        out_dir=params['o'], 
        template_type=params['p'],
        rf_type=params['r'], 
        interp=params['i'], 
        out_type=params['t']
    )
