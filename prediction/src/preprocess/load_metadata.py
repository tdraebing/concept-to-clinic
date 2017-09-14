import abc
import os
import warnings

import SimpleITK as sitk


class MetaData(object):
    """
    Object to encapsulate the parsed metadata.
    """
    def __init__(self):
        self.uid = None         # String containing an identifier for the image series
        self.ndims = None       # Integer conatining the number of dimensions
        self.shape = None       # Tuple containing 3 integers stating the number of pixels/voxels in each dimension (x, y, z)
        self.spacing = None     # Tuple containing 3 floats stating the spacing of pixels/voxels in each dimension (x, y, z)


class MetaDataDirector:
    """
    Class that organizes the build-process of the MetaData-object.
    """

    def __init__(self, path):
        self.image_path = path
        self.normalizer = None

    def construct(self, normalizer):
        self.normalizer = normalizer
        self.normalizer.retrieve_orig_metadata(self.image_path)
        try:
            self.normalizer.set_uid()
        except:
            warnings.warn("Could not find the UID for the image.", UserWarning)

        try:
            self.normalizer.set_ndims()
        except:
            warnings.warn("Could not parse the number of dimensions of the image.", UserWarning)

        try:
            self.normalizer.set_shape()
        except:
            warnings.warn("Could not parse the shape of the image.", UserWarning)

        try:
            self.normalizer.set_spacing()
        except:
            warnings.warn("Could not parse the voxel spacing of the image.", UserWarning)


class AbstractMetaDataNormalizer(metaclass=abc.ABCMeta):
    """
    Abstract representation of a builder for MetaData from image files.
    """

    def __init__(self):
        self.metadata = MetaData()
        self.orig_metadata = None

    @abc.abstractmethod
    def retrieve_orig_metadata(self, path):
        pass

    @abc.abstractmethod
    def set_uid(self):
        pass

    @abc.abstractmethod
    def set_ndims(self):
        pass

    @abc.abstractmethod
    def set_shape(self):
        pass

    @abc.abstractmethod
    def set_spacing(self):
        pass


class DCMNormalizer(AbstractMetaDataNormalizer):
    """
    Extracts metadata from DICOM-files and parses the information into the MetaData-object.
    """

    def retrieve_orig_metadata(self, path):
        """
        This function reads the original metadata.

        Args:
            path: (String) The path to a DICOM-series or file.

        Returns:
        """
        files = []
        if os.path.isdir(path):
            files = [os.path.join(path, f) for f in os.listdir(path) if
                     os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1] == '.dcm']
        elif os.path.splitext(path) in ['.dcm']:
            files = [path]

        if len(files) == 0:
            raise ValueError("Could not find a valid DICOM-files.")

        self.orig_metadata = []

        for file in files:
            try:
                reader = sitk.ImageFileReader()
                reader.LoadPrivateTagsOn()
                reader.SetFileName(file)
                image = reader.Execute()
                tags = image.GetMetaDataKeys()
                self.orig_metadata.append({k: image.GetMetaData(k) for k in tags})
            except:
                warnings.warn("Could not load metadata for {}. The DICOM-series might not be valid.".format(file),
                              UserWarning)

    def set_uid(self):
        self.metadata.uid = self.orig_metadata[0]['0020|000e']

    def set_ndims(self):
        self.metadata.ndims = 0
        self.metadata.ndims += 1 if int(self.orig_metadata[0]['0028|0010']) > 0 else 0
        self.metadata.ndims += 1 if int(self.orig_metadata[0]['0028|0011']) > 0 else 0
        self.metadata.ndims += 1 if len(self.orig_metadata) > 1 else 0

    def set_shape(self):
        self.metadata.shape = (int(self.orig_metadata[0]['0028|0010']),
                               int(self.orig_metadata[0]['0028|0011']),
                               len(self.orig_metadata))

    def set_spacing(self):
        spacing_xy = self.orig_metadata[0]['0028|0030'].split('\\')
        self.metadata.spacing = (float(spacing_xy[0]),
                                 float(spacing_xy[1]),
                                 float(self.orig_metadata[0]['0018|0050']))


class MHDNormalizer(AbstractMetaDataNormalizer):
    """
    Extracts metadata from an mhd-file and parses the information into the MetaData-object.
    """

    def retrieve_orig_metadata(self, path):
        """
        This function reads the original metadata.

        Args:
            path: (String) The path to a mhd-file.

        Returns:
        """
        self.orig_metadata = {}

        if os.path.splitext(path)[1] == '.raw':
            path = os.path.splitext(path)[0] + '.mhd'

        if os.path.splitext(path)[1] != '.mhd':
            raise ValueError('Given path does not point to a mhd- or raw-file.')

        try:
            with open(path, 'r') as f:
                for line in f:
                    k, v = line.strip().split(' = ')
                    self.orig_metadata[k] = v
        except IOError as e:
            raise IOError('Could not open the header (mhd) file: {}'.format(e))

    def set_uid(self):
        self.metadata.uid = os.path.splitext(self.orig_metadata['ElementDataFile'])[0]

    def set_ndims(self):
        self.metadata.ndims = int(self.orig_metadata['NDims'])

    def set_shape(self):
        self.metadata.shape = tuple([int(x) for x in self.orig_metadata['DimSize'].split(' ')])

    def set_spacing(self):
        self.metadata.spacing = tuple([float(x) for x in self.orig_metadata['ElementSpacing'].split(' ')])


def load_metadata(path):
    """
    This function chooses the correct metadata-parser for the file type in the given path.
    Args:
        path: (String) Path to a CT-scan image(-series).

    Returns: A dictionary containing the parsed metadata.

    """
    if os.path.splitext(path) in ['.dcm', '']:
        normalizer = DCMNormalizer()
    elif os.path.splitext(path) in ['.mhd', '.raw']:
        normalizer = MHDNormalizer()
    else:
        raise ValueError("Unknown file type.")

    director = MetaDataDirector(path)
    director.construct(normalizer)

    return normalizer.metadata.__dict__
