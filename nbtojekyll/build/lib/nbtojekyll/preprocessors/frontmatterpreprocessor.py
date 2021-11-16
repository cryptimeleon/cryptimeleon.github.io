from nbconvert.preprocessors import Preprocessor
from traitlets import Bool, Unicode


class FrontMatterPreprocessor(Preprocessor):
    """Preprocessor to add Jekyll metadata"""

    enable_toc = Bool(False).tag(config=True)
    enable_mathjax = Bool(False).tag(config=True)
    title = Unicode(
        "",
        help="Title of the Markdown page as given in the YAML Front Matter"
    ).tag(config=True)

    def preprocess(self, nb, resources):
        """Preprocess notebook

        Adds Jekyll metadata for YAML Front Matter.

        Args:
            nb (NotebookNode): Notebook being converted.
            resources (dict): Additional resources used by preprocessors and filters.
        Returns:
            NotebookNode: Modified notebook.
            dict: Modified resources dictionary.
        """
        metadata = {}
        metadata.update({"title": self.title})
        if self.enable_toc:
            metadata.update({"toc": "true"})
        if self.enable_mathjax:
            metadata.update({"mathjax": "true"})
        resources["metadata"]["jekyll"] = metadata

        return nb, resources