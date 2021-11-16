import re

from nbconvert.preprocessors import Preprocessor


class LatexDelimiterPreprocessor(Preprocessor):

    # stores incorrect delimiter regex patterns and the correct delimiter to replace them with
    # order of processing is important here
    delimiters = [
        # matches $$ but not \\$$. Replace with \n$$\n since we don't know whether we are at
        # beginning or end of the math block
        (re.compile(r"(?<!\\\\)\$\$"), "\n$$\n"),
        # matches $ but not \\$ and not $$ or $$$, i.e. not an escaped dollar sign or multiple
        # dollar signs. $ gets replaced by $$ since that is default Kramdown math delimiter
        (re.compile(r"(?<!\\\\)(?<!\$)\$(?!\$)"), r"$$")
    ]

    def fix_math_delimiters(self, cell):
        """
        Replaces incorrect math delimiters in the given cell by the correct ones
        """
        # only change delimiters in markdown cells
        if cell.cell_type == "markdown":
            cell.source = self.fix_markdown_delimiter(cell.source)
        return cell

    def fix_markdown_delimiter(self, md_str):
        """
        Replaces incorrect math delimiters in the given Markdown string by the correct delimiter
        """
        for regex, replacement in self.delimiters:
            # replace all occurences of the matched regex with the correct delimiter value
            md_str = regex.sub(replacement, md_str, count=0)
        return md_str

    def preprocess(self, nb, resources):
        """
        Preprocesses the notebook by replacing incorrect math delimiters by correct ones
        """
        nb.cells = [self.fix_math_delimiters(cell) for cell in nb.cells]

        return nb, resources