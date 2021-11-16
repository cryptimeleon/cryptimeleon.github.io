from nbconvert.preprocessors import Preprocessor
from traitlets import Unicode, Integer

binder_note_prefix = """\n\n---\n*Note:*\nYou can also check this page out in an
interactive Jupyter notebook by clicking the badge below:\n\n
[![Binder](https://mybinder.org/badge_logo.svg)]("""
binder_note_suffix = """)\n\n---\n"""


class BinderLinkPreprocessor(Preprocessor):

    binder_link = Unicode(
        "",  # default is to not insert binder badge
        help="""Full link to the Jupyter notebook on Binder. Specifiying this argument will 
        induce addition of a note at the end of the first section where the user can access the 
        Binder link."""
    ).tag(config=True)

    binder_link_cell = Integer(
        0,  # default cell is first one
        help="Index of cell at whose end to insert the binder link badge. Indexing starts at 0."
    ).tag(config=True)

    def preprocess(self, nb, resources):
        """Adds a binder link to execute the Jupyter notebook in an interactive environment."""
        # get the repository path
        if self.binder_link != "" and len(nb.cells) > self.binder_link_cell:
            self.log.debug("Binder link specified as '%s'", str(resources["binder_link"]))
            # insert at end of specified cell
            nb.cells[self.binder_link_cell].source += \
                binder_note_prefix + self.binder_link + binder_note_suffix
        else:
            self.log.debug("No binder link specified. Not inserting it")

        return nb, resources