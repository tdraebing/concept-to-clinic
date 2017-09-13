import os
import time

import SimpleITK as sitk

from .load_image import get_image


def write_modified_dicom(filtered_image, metadata, out_path):
    writer = sitk.ImageFileWriter()
    writer.KeepOriginalImageUIDOn()

    tags_to_copy = ["0010|0010",  # Patient Name
                    "0010|0020",  # Patient ID
                    "0010|0030",  # Patient Birth Date
                    "0020|000D",  # Study Instance UID, for machine consumption
                    "0020|0010",  # Study ID, for human consumption
                    "0008|0020",  # Study Date
                    "0008|0030",  # Study Time
                    "0008|0050",  # Accession Number
                    "0008|0060"]  # Modality

    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")

    direction = filtered_image.GetDirection()
    series_tag_values = [(metadata[k] for k in tags_to_copy if
                         metadata)] + \
                        [("0008|0031", modification_time),  # Series Time
                         ("0008|0021", modification_date),  # Series Date
                         ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                         ("0020|000e", "1.2.826.0.1.3680043.2.1125." + modification_date + ".1" + modification_time), # Series Instance UID
                         ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                                                           direction[1], direction[4], direction[7]))))]  # Series Description

    for i in range(filtered_image.GetDepth()):
        image_slice = filtered_image[:, :, i]

        for tag, value in series_tag_values:
            image_slice.SetMetaData(tag, value)

        image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))  # Instance Creation Date
        image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))  # Instance Creation Time
        image_slice.SetMetaData("0020|0032", '\\'.join(
            map(str, filtered_image.TransformIndexToPhysicalPoint((0, 0, i)))))  # Image Position (Patient)
        image_slice.SetMetaData("0020,0013", str(i))  # Instance Number

        writer.SetFileName(os.path.join(out_path, str(i) + '.dcm'))
        writer.Execute(image_slice)


def crop_image(path_to_image, begin, end, output=None, output_format=None):
    """
    This function crops a dicom series in the x-, y- and z-dimension. If an output path is provided, it will save the
    new series at that location.

    Examples for how to specify cropping mask using the begin- and end-parameter:

        The given DICOM series contains images with the resolution of 512x512 pixels and 133 images
        starting at a depth of -10 mm to a depth of -340 mm. Using begin = [0, 0, -10] and end = [512, 512, -340] would
        give you back the full series. Using begin = [100, 200, -160] and end = [120, 220, -170] would give you a
        new series with 5 images of size 20x20 pixels.

    Args:
        path_to_image: String containing the path containing the DICOM-series
        begin: List containing three numbers representing the starting point for cropping. See examples above.
        end: List containing three numbers representing the starting point for cropping. See examples above.
        output: (optional) String containg the path to where to save the cropped series.

    Returns:
        A list of pydicom Dataset-objects representing the cropped series.

    """

    metadata, image = get_image(path_to_image)
    cropped_image = image[begin[0]:end[0], begin[1]:end[1], begin[2]:end[2]]

    if output:
        if not os.path.exists(output):
            os.makedirs(output)

        if not output_format:
            output_format = os.path.splitext(path_to_image)

        if output_format == '':
            write_modified_dicom(cropped_image, metadata, output)
        elif output_format in ['.mhd', '.raw']:
            filename = os.path.splitext(os.path.split(path_to_image)[-1])[0] + '_cropped' + output_format
            sitk.ImageFileWriter(cropped_image, os.path.join(output, filename))
        else:
            raise ValueError('Unknown output file format.')

    return cropped_image
