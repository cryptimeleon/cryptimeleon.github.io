# nbtojekyll
Converts Jupyter Java notebooks to Markdown that can be rendered using Jekyll, Kramdown, and Mathjax.

Developed specifically for the [Cryptimeleon documentation](https://github.com/cryptimeleon/cryptimeleon.github.io).
Some defaults may be tailored towards that.

Inspired by the [jekyllnb](https://github.com/klane/jekyllnb) library.

## Features

- Converts single dollar signs $ to double dollar signs $$ as required by Kramdown for correct 
  Latex rendering. Also inserts newlines before and after existing $$ to support math blocks.
    
- \`\`\`Java is converted to \`\`\`java to allow for correct syntax highlighting

- Extraction of images included in the notebook

- Automatic addition of a YAML Front Matter with title, table of contents, and Mathjax 2 settings.
  Settings can be specified via command line arguments.
  Table of contents and title settings are specific to the 
  [Minimal Mistakes theme](https://mmistakes.github.io/minimal-mistakes/).

- Automatic insertion of a Binder link into the Markdown document for interactive execution of the 
  Jupyter notebook.

## Quickstart

Python 3 is required for installation. You will also need Jupyter and nbconvert for usage.

### Installation

The library is currently not hosted on PyPI, so you will have to install it locally.
To do that, clone this repository, open a terminal with working directory in this repository's
root folder and execute
```bash
python -m pip install --upgrade --force-reinstall --no-deps --no-cache-dir .
```
This will install the library for the Python version given by your `python` executable.
The rest of the arguments are to ensure that the package is reinstalled even if the version number
stays the same.

### Usage

There are two ways to use nbtojekyll: Via nbconvert or directly.

To use via nbconvert, simply specify `jekyllmd` as the format to export to (via nbconvert's `--to`)
parameter. However, this does not support image extraction.

Direct usage follows this template:
```bash
jupyter nbtojekyll <ARGUMENTS>
```
nbtojekyll uses nbconvert under the hood and therefore supports all the commandline arguments that
nbconvert supports.

The only change from nbconvert is that the output directory of the converted file is now relative 
to the current working directory, instead of to the notebook being converted.

It additionally adds the following optional command line arguments:

- `--enable-toc`: If specified, the `toc` attribute in the YAML Front Matter of the converted 
  markdown file will be set to `true`, meaning table of contents will be added. 
  The default is to not enable table of contents. This settings is specific to the 
  [Minimal Mistakes theme](https://mmistakes.github.io/minimal-mistakes/), meaning it may not
  have any effect without it or another theme that supports the `toc` attribute.
  
- `--enable-mathjax`: If specified, the `mathjax` attribute in the YAML Front Matter of the 
  converted markdown file will be set to `true`, meaning Mathjax LaTex rendering will be enabled.
  The default is to not enable Mathjax LaTex rendering.
  This setting only has an effect if the Mathjax 2 library is included in your Jekyll page.
  
- `--md-title TITLE`: If specified the `title` attribute in the YAML Front Matter of the
  converted markdown file will be set to TITLE. If not specified, the first header may be used
  as title. The `title` attribute is specific to the   
  [Minimal Mistakes theme](https://mmistakes.github.io/minimal-mistakes/), meaning it may not
  have any effect without it or another theme that supports the `title` attribute.

- `--site-dir SITE_DIR`: If specified, SITE_DIR should be the path to the root of the Jekyll site
  to which the converted notebook belongs. This path is used to construct the paths where the
  extracted images will be stored on your local filesystem. Default is the current working directory
  when executing nbtojekyll.
  
- `--image-dir IMAGE_DIR`: If specified, IMAGE_DIR should be the path where the extracted images 
  should be stored relative to the Jekyll site root path, that is, the path given by `--site-dir`. 
  The path MUST be given without a leading directory separator. 
  Default is the current working directory when executing nbtojekyll.
  
- `--binder-link BINDER_LINK`: If specified, BINDER_LINK should be the Binder URL that can be 
  visited to check out the notebook interactively. The conversion script will then insert a 
  clickable badge at the end of where was the first cell of the converted Jupyter notebook.
  If you don't like this position, you can move it manually after conversion.
  
- `--binder-link-cell CELL_INDEX`: If specified, CELL_INDEX should be the index of the notebook
  cell at the end of which the Binder badge should be inserted. Indexing starts at 0.
  Default is 0, that is the first cell.
  If you would like a position that is not at the end of any notebook cell, you either have
  split up your cells more or manually move the binder link after conversion.
