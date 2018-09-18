from setuptools import setup

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="consulservicefinder",
    version="0.0.1",
    author="Prins Wu",
    author_email="prinswu@gmail.com",
    description="Find service from Consul",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrinsWu/consulservicefinder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
