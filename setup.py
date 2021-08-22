import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ankistats",
    version="0.1.1",
    description="Python package to make it easier to analyse an anki database.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nogira/anki-stats",
    author="nogira",
    license="MIT",
    packages=["ankistats"],
    include_package_data=True,
    install_requires=["pandas", "matplotlib"]
)