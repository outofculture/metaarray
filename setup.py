from os import path

from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    author="Luke Campagnola",
    author_email="luke.campagnola@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="N-dimensional array with metadata such as axis titles, units, and column names.",
    install_requires=["numpy", "h5df"],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="MetaArray",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    url="https://github.com/outofculture/metaarray",
    version="2.0.3",
)
