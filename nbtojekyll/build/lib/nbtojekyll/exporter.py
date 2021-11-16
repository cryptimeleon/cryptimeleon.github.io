import os

from nbconvert.exporters import MarkdownExporter
from traitlets.config import Config


class JekyllExporter(MarkdownExporter):
    """Exports notebook to Markdown such that it can be rendered using Jekyll and Mathjax

    It
        * Replaces all single dollar sings with double dollar signs for Latex rendering
        * Replaces ```Java with ´´´java
        * Creates a valid YAML Front Matter with title and table of contents and Mathjax settings
        * Extracts images and replaces image paths
        * Generates binder link text snippet
    """

    # name for use with "File -> Download" menu
    export_from_notebook = "JekyllMD"

    # path to jekyllmd template
    extra_template_basedirs = [
        os.path.join(os.path.dirname(__file__), "templates")
    ]

    # enable the jekyll preprocessors
    preprocessors = [
        "nbtojekyll.preprocessors.FrontMatterPreprocessor",
        "nbtojekyll.preprocessors.JavaMagicsPreprocessor",
        "nbtojekyll.preprocessors.LatexDelimiterPreprocessor",
        "nbtojekyll.preprocessors.ImageExtractionPreprocessor",
        "nbtojekyll.preprocessors.BinderLinkPreprocessor"
    ]

    # name of the template to use for exporting
    template_name = "jekyllmd"

    @property
    def default_config(self):
        """Default configuration"""
        config = Config({
            "FrontMatterPreprocessor": {"enabled": True},
            "JavaMagicsPreprocessor": {"enabled": True},
            "LatexDelimiterPreprocessor": {"enabled": True},
            "ImageExtractionPreprocessor": {"enabled": True},
            "BinderLinkPreprocessor": {"enabled": True}
        })
        config.merge(super().default_config)
        # we use our own magics preprocessor so we remove the default one
        config.pop("HighlightMagicsPreprocessor")
        return config

