import abc


class MetaData(object):
    def __init__(self):
        self.orig_metadata = None
        self.patient = None


class MetaDataDirector:

    def __init__(self, orig_metadata):
        self.orig_metadata = orig_metadata
        self.normalizer = None

    def construct(self, normalizer):
        self.normalizer = normalizer
        self.normalizer.save_orig_metadata(self.orig_metadata)
        self.normalizer.set_patient_name()


class AbstractMetaDataNormalizer(metaclass=abc.ABCMeta):

    def __init__(self):
        self.metadata = MetaData()
        self.orig_metadata = None

    def save_orig_metadata(self, orig_metadata):
        self.orig_metadata = orig_metadata
        self.metadata.orig_metadata = orig_metadata

    @abc.abstractmethod
    def set_patient_name(self):
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
