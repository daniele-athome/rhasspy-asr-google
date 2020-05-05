"""Setup for rhasspyasr_google"""
import os

import setuptools

this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), "r") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r") as requirements_file:
    requirements = requirements_file.read().splitlines()

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()


class BinaryDistribution(setuptools.Distribution):
    """Enable packaging of binary artifacts."""

    # pylint: disable=R0201
    def has_ext_modules(self, _):
        """Will have binary artifacts."""
        return True


setuptools.setup(
    name="rhasspy-asr-google",
    version=version,
    author="Daniele Ricci",
    author_email="daniele@casaricci.it",
    url="https://github.com/daniele-athome/rhasspy-asr-google",
    packages=setuptools.find_packages(),
    package_data={
        "rhasspyasr_google": [
            "py.typed",
        ]
    },
    dist_class=BinaryDistribution,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)
