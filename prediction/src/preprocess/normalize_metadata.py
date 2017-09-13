import abc


class MetaData(object):
    def __init__(self):
        self.uid = None         # String containing an identifier for the image series
        self.ndims = None       # Integer conatining the number of dimensions
        self.shape = None       # Tuple containing 3 integers stating the number of pixels/voxels in each dimension (x, y, z)
        self.spacing = None     # Tuple containing 3 floats stating the spacing of pixels/voxels in each dimension (x, y, z)


class MetaDataDirector:

    def __init__(self, path):
        self.image_path = path
        self.normalizer = None

    def construct(self, normalizer):
        self.normalizer = normalizer
        self.normalizer.save_orig_metadata(self.orig_metadata)
        self.normalizer.set_patient_name()


class AbstractMetaDataNormalizer(metaclass=abc.ABCMeta):

    def __init__(self):
        self.metadata = MetaData()

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

    def set_patient_name(self):
        self.metadata.patient = self.orig_metadata.patient_name


class MHDNormalizer(AbstractMetaDataNormalizer):

    def set_patient_name(self):
        self.metadata.patient = self.orig_metadata.patient_name


def normalize_metadata(orig_metadata, file_type):
    if file_type in ["dcm"]:
        normalizer = DCMNormalizer()
    elif file_type in ["mhd"]:
        normalizer = MHDNormalizer()
    else:
        raise ValueError("Unknown file type.")

    director = MetaDataDirector(orig_metadata)
    director.construct(normalizer)

    return normalizer.metadata
