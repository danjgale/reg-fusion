
import os
import warnings
import numpy as np
from scipy.interpolate import interpn
import nibabel as nib
from nilearn._utils import check_niimg


def _set_img_prefix(img):
    """Extract filename of input image and handle edge cases"""
    if isinstance(img, nib.nifti1.Nifti1Image):
        if img.get_filename() is None:
            # sometimes arises if performing operations with nibabel or nilearn
            prefix = ''
            warnings.warn('input img has no associated filename')
        else:
            prefix = os.path.basename(img.get_filename())
    elif isinstance(img, str):
        prefix = os.path.basename(img)
    else:
        raise ValueError('img must str or instance of '
                         'nibabel.nifti1.Nifti1Image')

    # strip file extension if not empty
    if prefix != '':
        if prefix.endswith('.nii.gz'):
            prefix = prefix[:-7]
        elif prefix.endswith('.nii'):
            prefix = prefix[:-4]
        else:
            raise ValueError('img must be a NIfTI image ending in either '
                             '.nii.gz or .nii')

    return prefix


def _to_gifti(x, gifti_type):
    """Save x to correct gifti image type"""
    # Forcing the datatype to float/int 32 ensures compatibility with HCP 
    # surfaces
    if gifti_type == 'func.gii':
        intent_code = 'NIFTI_INTENT_ESTIMATE'
        datatype = 'NIFTI_TYPE_FLOAT32'
        img_array = x.astype(np.float32)
    elif gifti_type == 'label.gii':
        intent_code = 'NIFTI_INTENT_LABEL'
        datatype = 'NIFTI_TYPE_INT32'
        img_array = x.astype(np.int32)
    else:
        raise ValueError("`gifti_type` must be 'label' or 'func'")
    
    darray = nib.gifti.GiftiDataArray(img_array.squeeze(), intent=intent_code, 
                                      datatype=datatype)
    return nib.gifti.GiftiImage(darrays=[darray])


def _ras_to_vox(ras, affine):
    """Covert RAS to voxels coordinates"""
    trans = affine[:3, [3]] # retain as column vector
    x = ras - np.tile(trans, (1, ras.shape[1]))
    return np.linalg.inv(affine[:3, :3]) @ x 
    

def _project_data(x, affine, ras, interp='linear'):
    """Project data onto fsaverage hemisphere surface based on the provided 
    map
    """
    coords = _ras_to_vox(ras, affine)
    volgrid = [np.arange(x.shape[i]) for i in range(3)]
    
    if len(x.shape) == 3:
        proj_data = np.zeros((1, ras.shape[1]))
        proj_data[0] = interpn(volgrid, x, coords.T, method=interp)
    elif len(x.shape) == 4:
        # project each volume in 4d image
        n_vols = x.shape[3]
        proj_data = np.zeros((n_vols, ras.shape[1]))
        for i in range(n_vols):
            proj_data[i] = interpn(volgrid, x[:, :, :, i], coords.T, 
                                   method=interp)
    else:
        raise ValueError('x must be have dim of 3 or 4')
    return proj_data


def vol_to_fsaverage(input_img, out_dir, template_type='MNI152_orig', 
                     rf_type='RF_ANTs', interp='linear', out_type='nii.gz'):
    """Project volumetric data in standard space (MNI152 or Colin27) to 
    fsaverage 

    Parameters
    ----------
    input_img : niimg-like
        Input image in standard space (i.e. MNI152 or Colin27)
    out_dir : str
        Path to output directory (does not need to already exist)
    template_type : {'MNI152_orig', 'Colin27_orig', 'MNI152_norm', 'Colin27_norm'}
        Type of volumetric template used in index files. Use 'MNI152_orig' or 
        'Colin27_orig' when `rf_type` is `RF_ANTs`. Use 'MNI152_norm' or 
        'Colin27_norm' when `rf_type` is 'RF_M3Z'. An exception is raised if 
        `template_type` does not correspond to the correct `rf_type`. Ensure 
        that the template matches the standard space of `input_img` (i.e., 
        use MNI152_* if `input_img` is in MNI152-space). By default 
        'MNI152_orig'.
    rf_type : {'RF_ANTs', 'RF_M3Z'}
        Type of Registration Fusion approaches used to generate the mappings.
        RF-M3Z is recommended if data was registered from subject's space to 
        the volumetric atlas space using FreeSurfer. RF-ANTs is recommended if 
        such registrations were carried out using other tools, especially 
        ANTs. By default 'RF_ANTs'
    interp : {'linear', 'nearest'}, optional
        Interpolation approach. If `out_type` is 'label.gii', then interpolation 
        is always set to 'nearest'. By default 'linear'
    out_type : {'nii.gz, 'func.gii', 'label.gii'}, optional
        File type of surface files. Default is 'nii.gz', which is true to the 
        original Wu et al (2018) implementation. However, note that gifti 
        formats, either 'func.gii' or 'label.gii', are often preferred in many 
        applications.

    Parameters
    ----------
    str, str
        Absolute paths to left and right hemisphere output files, respectively
    """
    prefix = _set_img_prefix(input_img)
    if prefix == '':
        warnings.warn('prefix is empty will not be included in output files')

    img = check_niimg(input_img)

    # check if correct template and rf_type are used
    if rf_type == 'RF_ANTs':
        accepted_temp_types = ['MNI152_orig', 'Colin27_orig']
    elif rf_type == 'RF_M3Z':
        accepted_temp_types = ['MNI152_norm', 'Colin27_norm']
    else:
        raise ValueError("rf_type must be 'RF_ANTs' or 'RF_M3Z'")

    if template_type not in accepted_temp_types:
        raise ValueError('template_type must be one of '
                         f'{accepted_temp_types} when using rf_type={rf_type}')

    # handle out type 
    accepted_out_types = ['nii.gz', 'label.gii', 'func.gii']
    if out_type not in accepted_out_types:
            raise ValueError(f"out_type must be one of {accepted_out_types}")
    if (out_type == 'label.gii') and (interp != 'nearest'):
        interp = 'nearest'
        warnings.warn("interp set to 'nearest' with out_type 'label.gii'")

    # get specified mapping file
    map_dir = os.path.join(os.path.dirname(__file__), 'mappings')
    mapping = f'.avgMapping_allSub_{rf_type}_{template_type}_to_fsaverage.txt'

    os.makedirs(out_dir, exist_ok=True)
    outs = []
    for hemi in ['lh', 'rh']:
        # project hemisphere
        ras = np.loadtxt(os.path.join(map_dir, hemi + mapping))
        projected = _project_data(img.get_fdata(), img.affine, ras, interp)
    
        if out_type == 'nii.gz':
            # set nifti exactly like original Wu et al MATLAB version
            projected = np.expand_dims(projected.T, 2)
            out_img = nib.Nifti1Image(projected.astype(np.float), img.affine)
        elif out_type in accepted_out_types[1:]:
            out_img = _to_gifti(projected, out_type)

        out = os.path.join(out_dir, 
                           f"{hemi}.{prefix}{mapping.replace('txt', out_type)}")
        nib.save(out_img, out)
        outs.append(os.path.abspath(out))
    
    return outs[0], outs[1]