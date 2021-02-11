
import os
import pytest
import numpy as np
import nibabel as nib

from regfusion.main import vol_to_fsaverage

@pytest.fixture
def rootdir():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def data_dir(rootdir):
    return os.path.join(rootdir, 'data')


@pytest.fixture
def colin_data(data_dir):
    p = 'Colin_probMap_ants.central_sulc'
    data = {
        'input_img': f'{p}.nii.gz',
        'lh_RF_M3Z': f'lh.{p}.allSub_RF_M3Z_Colin27_norm_to_fsaverage.nii.gz', 
        'rh_RF_M3Z': f'rh.{p}.allSub_RF_M3Z_Colin27_norm_to_fsaverage.nii.gz', 
        'lh_RF_ANTs': f'lh.{p}.allSub_RF_ANTs_Colin27_orig_to_fsaverage.nii.gz', 
        'rh_RF_ANTs': f'rh.{p}.allSub_RF_ANTs_Colin27_orig_to_fsaverage.nii.gz' 
    }
    return {k: os.path.join(data_dir, v) for k, v in data.items()}


@pytest.fixture
def mni_data(data_dir):
    p = 'MNI_probMap_ants.central_sulc'
    data = {
        'input_img': f'{p}.nii.gz',
        'lh_RF_M3Z': f'lh.{p}.allSub_RF_M3Z_MNI152_norm_to_fsaverage.nii.gz', 
        'rh_RF_M3Z': f'rh.{p}.allSub_RF_M3Z_MNI152_norm_to_fsaverage.nii.gz', 
        'lh_RF_ANTs': f'lh.{p}.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz', 
        'rh_RF_ANTs': f'rh.{p}.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz' 
    }
    return {k: os.path.join(data_dir, v) for k, v in data.items()}


def test_colin_files(colin_data):
    assert all([os.path.exists(v) for k, v in colin_data.items()])


def test_mni_files(mni_data):
    assert all([os.path.exists(v) for k, v in mni_data.items()])


## Colin tests

def test_colin27_m3z(colin_data, tmpdir):

    input_img = colin_data['input_img']
    expected_lh = nib.load(colin_data['lh_RF_M3Z']).get_fdata()
    expected_rh = nib.load(colin_data['rh_RF_M3Z']).get_fdata()

    # test nifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='Colin27_norm', 
                               rf_type='RF_M3Z')
    assert np.allclose(nib.load(lh).get_fdata(), expected_lh)
    assert np.allclose(nib.load(rh).get_fdata(), expected_rh)

    # test gifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='Colin27_norm', 
                               rf_type='RF_M3Z', out_type='func.gii')
    assert np.allclose(nib.load(lh).darrays[0].data, expected_lh.ravel())
    assert np.allclose(nib.load(rh).darrays[0].data, expected_rh.ravel())


def test_colin27_ants(colin_data, tmpdir):
    
    input_img = colin_data['input_img']
    expected_lh = nib.load(colin_data['lh_RF_ANTs']).get_fdata()
    expected_rh = nib.load(colin_data['rh_RF_ANTs']).get_fdata()

    # test nifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='Colin27_orig', 
                               rf_type='RF_ANTs')
    assert np.allclose(nib.load(lh).get_fdata(), expected_lh)
    assert np.allclose(nib.load(rh).get_fdata(), expected_rh)

    # test gifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='Colin27_orig', 
                               rf_type='RF_ANTs', out_type='func.gii')
    assert np.allclose(nib.load(lh).darrays[0].data, expected_lh.ravel())
    assert np.allclose(nib.load(rh).darrays[0].data, expected_rh.ravel())

## MNI tests

def test_mni152_m3z(mni_data, tmpdir):

    input_img = mni_data['input_img']
    expected_lh = nib.load(mni_data['lh_RF_M3Z']).get_fdata()
    expected_rh = nib.load(mni_data['rh_RF_M3Z']).get_fdata()

    # test nifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='MNI152_norm', 
                               rf_type='RF_M3Z')
    assert np.allclose(nib.load(lh).get_fdata(), expected_lh)
    assert np.allclose(nib.load(rh).get_fdata(), expected_rh)

    # test gifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='MNI152_norm', 
                               rf_type='RF_M3Z', out_type='func.gii')
    assert np.allclose(nib.load(lh).darrays[0].data, expected_lh.ravel())
    assert np.allclose(nib.load(rh).darrays[0].data, expected_rh.ravel())


def test_mni152_ants(mni_data, tmpdir):
    
    input_img = mni_data['input_img']
    expected_lh = nib.load(mni_data['lh_RF_ANTs']).get_fdata()
    expected_rh = nib.load(mni_data['rh_RF_ANTs']).get_fdata()

    # test nifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='MNI152_orig', 
                               rf_type='RF_ANTs')
    assert np.allclose(nib.load(lh).get_fdata(), expected_lh)
    assert np.allclose(nib.load(rh).get_fdata(), expected_rh)

    # test gifti output
    lh, rh, = vol_to_fsaverage(input_img, tmpdir, template_type='MNI152_orig', 
                               rf_type='RF_ANTs', out_type='func.gii')
    assert np.allclose(nib.load(lh).darrays[0].data, expected_lh.ravel())
    assert np.allclose(nib.load(rh).darrays[0].data, expected_rh.ravel())