# Based on https://gist.github.com/sglyon/5687b8455a0107afc6f4c60b5f313670
import os
from binascii import a2b_base64

from nbconvert.preprocessors import Preprocessor
from traitlets import Unicode, Set


class ImageExtractionPreprocessor(Preprocessor):
    """
    Extracts .png and .jpg images from the notebook
    """

    output_filename_template = Unicode(
        "{notebook_name}_attach_{cell_index}_{name}"
    ).tag(config=True)

    extract_output_types = Set(
        {"image/png", "image/jpeg"}
    ).tag(config=True)

    image_dir = Unicode(
        ".",  # default is current working directory when executing script
        help="""Directory in which to place extracted images. Root is the Jekyll site directory.
        For example, 'assets/images'. Path should not start with a '/'!
        """
    ).tag(config=True)

    site_dir = Unicode(
        ".",  # default is current working directory when executing script
        help="The root directory of the Jekyll site."
    ).tag(config=True)

    def preprocess_cell(self, cell, resources, cell_index):
        """
        Extracts images from given cell.
        """
        self.log.debug("Image dir '%s'", str(resources["image_dir"]))
        self.log.debug("Site dir '%s'", str(resources["site_dir"]))
        self.log.debug(
            "Extracted images will be stored in '%s'",
            os.path.normpath(os.path.join(resources["site_dir"], resources["image_dir"]))
        )

        if not isinstance(resources["outputs"], dict):
            resources["outputs"] = {}

        # loop over all attachments and extract supported output types
        for name, attach in cell.get("attachments", {}).items():
            for mime, data in attach.items():
                if mime not in self.extract_output_types:
                    continue

                data = a2b_base64(data)

                filename = self.output_filename_template.format(
                    notebook_name=resources["metadata"]["name"],
                    cell_index=cell_index,
                    name=name
                )

                # filename for storage on filesystem is different
                storage_filename = os.path.normpath(
                    os.path.join(self.site_dir, self.image_dir, filename)
                )

                # image can be retrieved via resources dictionary
                # this is used by nbconvert to actually store the output to filesystem
                resources["outputs"][storage_filename] = data

                # Correct link in cell source
                # Link needs to be based on the Jekyll site directory as root
                filename = os.path.normpath(
                    os.path.join("/", self.image_dir, filename)
                )
                attach_str = "attachment:" + name
                if attach_str in cell.source:
                    cell.source = cell.source.replace(attach_str, filename)

        return cell, resources