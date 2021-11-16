import setuptools

setuptools.setup(
    name="nbtojekyll",
    version="0.0.1",
    author="Raphael Heitjohann",
    description="Converts Jupyter Java Notebooks to Markdown renderable in Jekyll and with "
                "Mathjax support",
    url="https://github.com/rheitjoh/nbtojekyll",
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    packages=["nbtojekyll", "nbtojekyll.preprocessors"],
    include_package_data=True,
    entry_points={
        "nbconvert.exporters": [
            "jekyllmd = nbtojekyll:JekyllExporter"
        ],
        "console_scripts": [
            "jupyter-nbtojekyll = nbtojekyll.nbtojekyll:NBToJekyll.launch_instance"
        ]
    }
)
