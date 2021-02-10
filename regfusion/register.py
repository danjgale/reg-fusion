
import os
import re
import numpy as np
from scipy.interpolate import interpn
import nibabel as nib
from nilearn._utils import check_niimg


def _ras_to_vox(ras, affine):
    # get translation column vector
    trans = affine[:3, [3]]
    x = ras - np.tile(trans, (1, ras.shape[1]))
    return np.linalg.inv(affine[:3, :3]) @ x 
    

def project_hemisphere(img, hemi_map, interp='linear'):

    data = img.get_fdata()  
    
    if len(img.shape) == 3:
        nvols = 1
    else:
        nvols = img.shape[3]
    
    num_vertices = 163842
    ras = np.loadtxt(hemi_map)
    vox_coords = _ras_to_vox(ras[:, :num_vertices], img.affine)
    mat_coords = vox_coords

    volgrid = [np.arange(data.shape[i]) for i in range(3)]
    proj_data = np.zeros((nvols, num_vertices))
    for i in range(nvols):
        proj_data[i] = interpn(volgrid, data[:, :, :, 0], mat_coords.T, 
                               method=interp)

    return proj_data


# def project_volume(img, out_dir, map_dir, freesurfer_dir, 
#                    template_type='MNI152_orig', num_sub=0, rf_type='RF_ANTs', 
#                    interp='linear'):
    
#     with open(os.path.join(freesurfer_dir, 'build-stamp.txt', 'r')) as f:
#         print('Using Freesurfer verion', 
#               re.findall(r'\d\.\d\.\d', f.readline())[0]) 

#     img = _check_img(img)
    
#     pass


def nifti_to_gifti(img, gifti_type):
    img = _check_img(img)
    img_array = img.get_fdata()

    # gifti type parameters. Forcing the datatype to float/int 32 ensures
    # compatibility with HCP surfaces
    if gifti_type == 'label':
        intent_code = 'NIFTI_INTENT_ESTIMATE'
        datatype = 'NIFTI_TYPE_FLOAT32'
        img_array = img_array.astype(np.float32)
    elif gifti_type == 'func':
        intent_code = 'NIFTI_INTENT_LABEL'
        datatype = 'NIFTI_TYPE_INT32'
        img_array = img_array.astype(np.int32)
    else:
        raise ValueError("`gifti_type` must be 'label' or 'func'")
    
    darray = nib.gifti.GiftiDataArray(img_array.squeeze(), intent=intent_code, 
                                      datatype=datatype)
    return nib.gifti.GiftiImage(darrays=[darray])


if __name__ == '__main__':
    pass
    

    

