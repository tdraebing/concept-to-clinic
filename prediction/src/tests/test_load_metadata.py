import os

import SimpleITK as sitk
import numpy as np
import pytest

from ..preprocess import load_image as ld
from ..preprocess import load_metadata as lm


@pytest.fixture
def test_files():
    mock_img_nda = np.random.randint(0, 255, (10, 10, 3))
    mock_img = sitk.GetImageFromArray(mock_img_nda)
    sitk.WriteImage(mock_img, '../images/test.raw')

    mock_header = [
        "ObjectType = Image\n",
        "NDims = 3\n",
        "BinaryData = True\n",
        "BinaryDataByteOrderMSB = False\n",
        "CompressedData = False\n",
        "TransformMatrix = 1 0 0 0 1 0 0 0 1\n",
        "Offset = -199.30000000000001 -220 -394.5\n",
        "CenterOfRotation = 0 0 0\n",
        "AnatomicalOrientation = RAI\n",
        "ElementSpacing = 0.859375 0.859375 2.5\n",
        "DimSize = 512 512 143\n",
        "ElementType = MET_SHORT\n",
        "ElementDataFile = 1.3.6.1.4.1.14519.5.2.1.6279.6001.102681962408431413578140925249.raw"
    ]
    with open('../images/test.mhd', 'w+')as f:
        f.writelines(mock_header)

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

def test_MetaData():
    assert isinstance(lm.MetaData(), object)


def test_AbstractMetaDataNormalizer():
    with pytest.raises(NotImplementedError):
        lm.AbstractMetaDataNormalizer()


def test_load_metadata(test_files):
    for _, img in test_files['valid']:
        assert isinstance(ld.get_image(img), dict)
