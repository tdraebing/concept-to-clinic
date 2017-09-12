
class InvalidDicomSeriesException(Exception):
    """Exception that is raised when the given folder does not contain dcm-files.
    """

    def __init__(self, *args):
        if not args:
            args = ('The specified path does not contain dcm-files. Please ensure that '
                    'the path points to a folder containing a DICOM-series.', )
        Exception.__init__(self, *args)


class UnknownFileTypeException(Exception):
    """Exception that is raised when the extension of the given file path is unknown.
    """

    def __init__(self, *args):
        if not args:
            args = ('The file extension is unknown.', )
        Exception.__init__(self, *args)


class InvalidImageException(Exception):
    """Exception that is raised, when loading the image fails due to corrupt files.
    """

    def __init__(self, *args):
        if not args:
            args = ('The image could not be loaded. Please check image integrity.', )
        Exception.__init__(self, *args)
