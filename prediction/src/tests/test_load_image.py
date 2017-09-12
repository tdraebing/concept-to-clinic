import os

import SimpleITK as sitk
import numpy as np
import pytest

from ..preprocess import load_image as ld
from ..preprocess import errors


@pytest.fixture
def test_files():
    mock_img_nda = np.random.randint(0, 255, (10, 10, 3))
    mock_img = sitk.GetImageFromArray(mock_img_nda)
    sitk.WriteImage(mock_img, '../images/test.mhd')
    sitk.WriteImage(mock_img, '../images/test.raw')
    open('../images/not_an_image.mhd', 'w+')
    open('../images/not_an_image.txt', 'w+')
    dicom_file = '../images/LIDC-IDRI-0001/1.3.6.1.4.1.14519.5.2.1.6279.6001.298806137288633453246975630178/' \
                 '1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192/-95.000000.dcm'
    yield {'valid': {'dicom_series': dicom_file,
                     'mhd': '../images/test.mhd',
                     'raw': '../images/test.raw',
                     'dcm': os.path.split(dicom_file)[0]},
           'invalid': {'invalid_series': '../images',
                       'invalid_mhd': '../images/not_an_image.mhd',
                       'not_an_image': '../images/not_an_image.txt'}}
    os.remove('../images/test.mhd')
    os.remove('../images/test.raw')
    os.remove('../images/not_an_image.mhd')
    os.remove('../images/not_an_image.txt')


def test_read_dicom_series(test_files):
    image = ld.read_dicom_series(test_files['valid']['dicom_series'])

    assert isinstance(image, sitk.Image)
    assert image.GetSize[0] > 0

    with pytest.raises(errors.InvalidDicomSeriesException):
        ld.read_dicom_series(test_files['invalid']['invalid_series'])


def test_read_raw_file(test_files):
    image = ld.read_raw_file(test_files['valid']['mhd'])

    assert isinstance(image, sitk.Image)
    assert image.GetSize == (10, 10, 3)

    with pytest.raises(errors.UnknownFileTypeException):
        ld.read_raw_file(test_files['invalid']['not_an_image'])

    with pytest.raises(errors.InvalidImageException):
        ld.read_raw_file(test_files['invalid']['ninavlid_mhd'])


def test_get_image(test_files):
    for _, img in test_files['valid']:
        assert isinstance(ld.get_image(img), sitk.Image)

    with pytest.raises(ValueError):
        ld.get_image(1)


def test_load_image(test_files):
    img_arr = ld.load_image(test_files['valid']['mhd'])
    assert isinstance(img_arr, sitk.Image)

    valid_preprocess = lambda x: x
    img_arr = ld.load_image(test_files['valid']['mhd'], valid_preprocess)
    assert isinstance(img_arr, sitk.Image)

    with pytest.raises(TypeError):
        invalid_preprocess = lambda x: 'no array'
        ld.load_image(test_files['valid']['mhd'], invalid_preprocess)
