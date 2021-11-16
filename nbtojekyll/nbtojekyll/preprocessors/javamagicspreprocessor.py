from nbconvert.preprocessors import HighlightMagicsPreprocessor


class JavaMagicsPreprocessor(HighlightMagicsPreprocessor):

    def which_magic_language(self, source):
        """
        When a cell uses another language through a magic extension,
        the other language is returned.
        If no language magic is detected, this function returns java.

        :param source: Source code of the cell to highlight
        """
        magic_language = super().which_magic_language(source)
        if magic_language is None:
            # we assume java in this case
            return "java"