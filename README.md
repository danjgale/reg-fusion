# reg-fusion

This is a Python implementation of [Wu et al (2018)'s registration fusion methods](https://onlinelibrary.wiley.com/doi/full/10.1002/hbm.24213) to project MRI data from standard volumetric coordinates, either MNI152 or Colin27, to Freesurfer's fsaverage. This is already [available in the MATLAB-based version](https://github.com/ThomasYeoLab/CBIG/tree/master/stable_projects/registration/Wu2017_RegistrationFusion) provided by *Wu et al*, which works really well out of the box! However, given Python's increasing stake in neuroimaging analysis, a pure Python version may be useful. 

A huge thank you to *Wu et al* for making excellent tool available! If you use this package, **please cite the original**:

Wu J, Ngo GH, Greve DN, Li J, He T, Fischl B, Eickhoff SB, Yeo BTT. [**Accurate nonlinear mapping between MNI volumetric and FreeSurfer surface coordinate systems**](http://people.csail.mit.edu/ythomas/publications/2018VolSurfMapping-HBM.pdf), *Human Brain Mapping* 39:3793–3808, 2018.

## Installation


## Command-line interface

Registration fusion can be ran on the command-line using `regfusion`. The flags correspond to the original implemenation, with the exception of `-t`, which is specific to `regfusion` (see Notes).  

```
usage: regfusion [-h] [-s input_vol] [-o output_dir] [-p template_type] [-r RF_type] [-i interp] [-t out_type]

optional arguments:
  -h, --help        show this help message and exit
  -s input_vol      Absolute path to input volume. Input should be in nifti format
  -o output_dir     Absolute path to output directory
  -p template_type  Type of volumetric template used in index files. Use MNI152_orig or Colin27_orig when -r is RF_ANTs. Use MNI152_norm or Colin27_norm when
                    -r is RF_M3Z. Otherwise, an exception is raised. Ensure that the template matches the standard space of -i (i.e., use MNI152_* if -i is
                    in MNI152-space). Default: MNI152_orig
  -r RF_type        Type of Registration Fusion approaches used to generate the mappings (RF_M3Z or RF_ANTs). RF_M3Z is recommended if data was registered
                    from subject's space to the volumetric atlas space using FreeSurfer. RF_ANTs is recommended if such registrations were carried out using
                    other tools, especially ANTs. Default: RF_ANTs
  -i interp         Interpolation (linear or nearest). If -g is label.gii, then interpolation is always set to nearest and a warning is raised. Default:
                    linear
  -t out_type       File type of surface files. nii.gz is true to the original Wu et al (2018) implementation. Note that gifti formats, either func.gii or
                    label.gii, are often preferred. Default: nii.gz
```

### Examples

For example, the default RF-ANTs implementation (preferred) with MNI data would be: 
```
regfusion -i mni_input.nii.gz -o output
```
True to the original implementation, two surface files (one each hemisphere) are saved to the output directory, `-o`, with the RF method and template embedded in the file names:
```
output/
  lh.mni_input.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz
  rh.mni_input.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz
```

It may be preferred to generate GIfTI files instead of the default NIfTI:
```
regfusion -i mni_input.nii.gz -o output -t func.gii
```
The output, which will have the appropriate GIfTI file extensions:
```
output/
  lh.mni_input.allSub_RF_ANTs_MNI152_orig_to_fsaverage.func.gii
  rh.mni_input.allSub_RF_ANTs_MNI152_orig_to_fsaverage.func.gii
```

Should you wish to project a binary mask (e.g., to display a region of interest), you may consider setting the output type, `-t`, to `label.gii`. In this case, interpolation, `-i`, will always be set to `nearest` to retain the original voxel values/labels. If not explicitly set with `-i`, interpolation will be overwritten to `nearest` and warning is raised. 

For example:
```
regfusion -i mni_input.nii.gz -o output -t label.gii
```

And finally, the RF-M3Z method can be used if that is preferred:
```
regfusion -i mni_input.nii.gz -r RF_M3Z -o output
```

## Python API

The CLI simply calls the main underlying function, `vol_to_fsaverage`. This function can imported directly in Python. In addition to saving the files to `out_dir`, the absolute file paths of the left and right surface files are returned. 

```
vol_to_fsaverage(input_img, out_dir, template_type='MNI152_orig', 
                 rf_type='RF_ANTs', interp='linear', out_type='nii.gz'):

    Project volumetric data in standard space (MNI152 or Colin27) to 
    fsaverage 

    Parameters
    ----------
    input_img : niimg-like
        Input image in standard space (i.e. MNI152 or Colin27)
    out_dir : str
        Path to output directory (does not need to already exist)
    template_type : {'MNI152_orig', 'Colin27_orig', 'MNI152_norm', 'Colin27_norm'}
        Type of volumetric template used in index files. Use 'MNI152_orig' or 
        'Colin27_orig' when `rf_type` is 'RF_ANTs'. Use 'MNI152_norm' or 
        'Colin27_norm' when `rf_type` is 'RF_M3Z'. Otherwise, an exception is 
        raised. Ensure that the template matches the standard space of 
        `input_img` (i.e., use MNI152_* if `input_img` is in MNI152-space). By 
        default 'MNI152_orig'.
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
        original Wu et al (2018) implementation. Note that gifti 
        formats, either 'func.gii' or 'label.gii', are often preferred.

    Returns
    ----------
    str, str
        Absolute paths to left and right hemisphere output files, respectively
```

The equivalent command for the first CLI example (i.e. the default RF_ANTs with MNI data):

```python
from regfusion import vol_to_fsaverage

lh, rh = vol_to_fsaverage('mni_input.nii.gz', 'output')
```

## Notes

`regfusion` implements the same two registration fusion approaches as the original MATLAB version by *Wu et al* (see `tests/` for validations). However, there are some differences in the API:
- `regfusion` does not have the `-n` flag that determines the number of subjects used to create the average mapping. That is because the standalone scripts of the MATLAB versions only uses all 1490 subjects, and thus `regfusion` does too 
- `regfusion` does not have the `-m` flag because no MATLAB is required
- `regfusion` does not have the `-f` flag because, technically, Freesurfer is not required. However, it is strongly recommended to get a freely available Freesurfer license because we are ultimately projecting to Freesurfer's fsaverage
- Unlike the original MATLAB version, `regfusion` has a `-t` flag (`out_type` in `vol_to_fsaverage`; see above for description). The original MATLAB version outputs NIfTI images (`regfusion` default), but this option lets `regfusion` output to GIfTIs, which are generally preferred for surface files. Users are encouraged to set `-t`/`out_type` to one of the GIfTI output types if they find that GIfTIs are more suitable for their needs

Some useful things to know:
- *Wu et al* show that`RF_ANTs` is generally the better approaches of the two, which is why it is the default in `regfusion`. `RF_M3Z` seems best-suited if the normalization was performed via Freesurfer.
- As *Wu et al* emphasize, the *actual* best practice here avoid projecting standard volumetric coordinates (e.g., MNI) to fsaverage altogether. Alternatives include performing all you analyses in subject/native volumetric coordinates and projecting that data to fsaverage, based on Freesurfer's `recon-all`. Or, perform analyses directly in fsaverage after running `recon-all`. Projecting data from one standard coordinates space to another is loses precision at each step (see *Wu et al* for details). Neverthless, people do this all the time and these registration fusion approaches ensure that these projections are as accurate as possible.
- Relating to the previous point: If you do project from MNI/Colin coordinates to fsaverage, it's probably a wise idea to find a way to still show your data in volume-space too (e.g., as supplementary figures/material).     

## References

Wu J, Ngo GH, Greve DN, Li J, He T, Fischl B, Eickhoff SB, Yeo BTT. [**Accurate nonlinear mapping between MNI volumetric and FreeSurfer surface coordinate systems**](http://people.csail.mit.edu/ythomas/publications/2018VolSurfMapping-HBM.pdf), *Human Brain Mapping* 39:3793–3808, 2018.