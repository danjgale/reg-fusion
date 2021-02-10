
import os
import re
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

    # gifti type parameters. Forcing the datatype to float/int 32 ensures
    # compatibility with HCP surfaces
    if gifti_type == 'label':
        intent_code = 'NIFTI_INTENT_ESTIMATE'
        datatype = 'NIFTI_TYPE_FLOAT32'
        img_array = x.astype(np.float32)
    elif gifti_type == 'func':
        intent_code = 'NIFTI_INTENT_LABEL'
        datatype = 'NIFTI_TYPE_INT32'
        img_array = x.astype(np.int32)
    else:
        raise ValueError("`gifti_type` must be 'label' or 'func'")
    
    darray = nib.gifti.GiftiDataArray(img_array.squeeze(), intent=intent_code, 
                                      datatype=datatype)
    return nib.gifti.GiftiImage(darrays=[darray])


def _ras_to_vox(ras, affine):
    trans = affine[:3, [3]] # retain as column vector
    x = ras - np.tile(trans, (1, ras.shape[1]))
    return np.linalg.inv(affine[:3, :3]) @ x 
    

def _project_data(x, affine, ras, interp='linear'):
    """Project data onto hemisphere surface based on the provided map"""
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


def project_volume(img, out_dir, template_type='MNI152_orig', 
                   rf_type='RF_ANTs', interp='linear', gifti_type='func'):

    prefix = _set_img_prefix(img)
    if prefix == '':
        warnings.warn('prefix is empty will not be included in output files')

    img = check_niimg(img)

    # check if correct template and rf type are used
    if rf_type == 'RF_ANTs':
        accepted_temp_types = ['MNI152_orig', 'Colin27_orig']
    elif rf_type == 'RF_M3Z':
        accepted_temp_types = ['MNI152_norm', 'Colin27_norm']
    else:
        raise ValueError("rf_type must be 'RF_ANTs' or 'RF_M3Z'")

    if template_type not in accepted_temp_types:
        raise ValueError('template_type must be one of '
                         f'{accepted_temp_types} when using rf_type={rf_type}')

    # handle gifti type 
    if gifti_type not in ['label', 'func', None]:
            raise ValueError("gifti_type must be 'label' or 'func'")

    if (gifti_type == 'label') and (interp != 'nearest'):
        interp = 'nearest'
        warnings.warn("interp set to 'nearest' with gifti_type 'label'")

    map_dir = os.path.join(os.path.dirname(__file__), 'mappings')
    mapping = f'.avgMapping_allSub_{rf_type}_{template_type}_to_fsaverage.txt'

    os.makedirs(out_dir, exist_ok=True)
    for hemi in ['lh', 'rh']:
        ras = np.loadtxt(os.path.join(map_dir, hemi + mapping))
        projected = _project_data(img.get_fdata(), img.affine, ras, interp)
        projected = np.expand_dims(projected.T, 2)

        out_file = f"{hemi}.{prefix}{mapping.replace('txt', '')}"
        
        # # save nifti (exactly like original matlab version)
        out_niimg = nib.Nifti1Image(projected, ras)
        nib.save(out_niimg, os.path.join(out_dir, out_file + '.nii.gz'))
    
        if gifti_type:
            out_giimg = _to_gifti(projected, gifti_type)
            nib.save(out_giimg, 
                     os.path.join(out_dir, out_file + f'{gifti_type}.gii'))


if __name__ == '__main__':
    pass
