import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    x.strip() for x
    in open('requirements.txt').readlines() if not x.startswith('#')]

setuptools.setup(
    name="consulservicefinder",
    version="0.0.1",
    author="Prins Wu",
    author_email="prinswu@gmail.com",
    keywords="consul microservice",
    description="Find service from Consul",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrinsWu/consulservicefinder",
    python_requires=">=3",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
