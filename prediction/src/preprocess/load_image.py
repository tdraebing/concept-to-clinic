import os
from glob import glob

import numpy as np
import SimpleITK as sitk

from .errors import *


def get_metadata(image):
        metadata_keys = image.GetMetaDataKeys()
        metadata = {}
        for key in metadata_keys:
            metadata[key] = image.GetMetaData(key)
        return metadata


def read_dicom_series(path):
    """
    Takes a path to a folder containing a DICOM series and reads into a SimpleITK image.

    Args:
        path: (String) path to a folder containing a DICOM series (multiple *.dcm-files)

    Returns: (SimpleITK.Image) A SimpleITK.Image object containing the image series.

    """
    try:
        reader = sitk.ImageSeriesReader()
        filenamesDICOM = reader.GetGDCMSeriesFileNames(path)
        reader.SetFileNames(filenamesDICOM)
        image = reader.Execute()
        return image, get_metadata(image)
    except:
        raise InvalidDicomSeriesException()


def read_raw_file(path):
    """
    Takes a path to a *.mhd- or *.raw-file and reads it into a SimpleITK image.

    Args:
        path: (String) path to a folder containing a *.mhd- or *.raw-file

    Returns: (SimpleITK.Image) A SimpleITK.Image object containing the image.

    """
    try:
        image = sitk.ReadImage(path)
    except:
        extension = os.path.splitext(path)
        if extension not in ['.raw', '.mhd', '.dcm']:
            raise UnknownFileTypeException()
        else:
            raise InvalidImageException()

    return image, get_metadata(image)


def get_image(path):
    """
    Takes a path and decides how to read the image in the path.

    Args:
        path: (String) path to a folder containing an image.

    Returns: (SimpleITK.Image) A SimpleITK.Image object containing the image.

    """
    if os.path.isfile(path):
        try:
            return read_raw_file(path)
        except Exception as e:
            raise e
    elif os.path.isdir(path):
        return read_dicom_series(path)
    else:
        raise ValueError('Given path is not a valid path.')


def load_image(path, preprocess=None):
    """Function that orchestrates the loading of dicom datafiles of a dicom series into a numpy-array.

    Args:
        path (str): contains the path to the folder containing the dcm-files of a series or a *.mhd- or *.raw-file.
        preprocess (callable[list[DICOM], ndarray] -> ndarray): A python function or method
            aimed at preprocessing CT-scan images.

    Returns:
        numpy-array containing the 3D-representation of the DICOM-series
    """

    image, metadata = get_image(path)
    voxel_data = sitk.GetArrayFromImage(image)

    if preprocess is not None:
        voxel_data = preprocess(image, voxel_data)
        print(type(voxel_data))
        if not isinstance(voxel_data, np.ndarray):
            raise TypeError('The signature of preprocess must be ' +
                            'callable[list[DICOM], ndarray] -> ndarray')

    return voxel_data
