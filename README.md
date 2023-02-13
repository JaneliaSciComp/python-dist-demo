# python-dist-demo

## Introduction

Open science involves sharing of code, and Python is a popular language for that code.  However, scientists may be reluctant to try shared Python code when doing so involves many installation steps, like installing [Conda](https://docs.conda.io/en/latest/), installing packages, installing other packages with [Pip](https://pypi.org/project/pip/), possibly resolving package conflicts, etc.

An appealing alternative is to "bundle" the Python code and its dependencies into a single executable that can be downloaded from the "Releases" section of a GitHub site.  This project is a test bed for working out the detals of such an approach.  This project is called a "demo" rather than a "test" just in case any of the tools involved implicitly assume that items with names including "test" are parts of an internal test suite.

[This article](https://www.infoworld.com/article/3656628/6-ways-to-package-python-apps-for-re-use.html) gives an overview of some systems for bundling Python code and dependencies for release.  Based on this article, the systems tested in this project are:

* [PyInstaller](https://pyinstaller.org/en/stable/)
* [Nuitka](https://nuitka.net/)

Nuitka is the more ambitious system, converting the Python code into C code that is compiled with optimization.  As such, it has a higher risk of producing an output executable that does not behavior exactly the same as the input Python code.

Note that these systems do not create a single executable that can run on any platform.  It is necessary to perform the executable creation separately on macOS, Windows and Linux.

## Demo 1

The first demo uses [h5py](https://www.h5py.org/) to parse the metadata from the HDF5 part of a volume data set in [H5J format](https://github.com/JaneliaSciComp/workstation/blob/master/docs/H5JFileFormat.md).  Example H5J files can be found [here](https://github.com/JaneliaSciComp/web-h5j-loader#test-data).

This demo also outputs the contents of a `VERSION` file that is part of the GitHub repo, but not a Python dependency per se.

Without bundling, run it as follows:

    $ conda create --name python-dist-demo
    $ conda activate python-dist-demo
    $ conda install h5py
    $ cd python-dist-demo/demo1
    $ python demo1.py -i path/to/example.h5j
    Checking for 'python-dist-demo/VERSION'
    Version 1.0.0
    Using input file: path/to/example.h5j
    H5J dimensions: 1210, 566, 174

### PyInstaller

To use PyInstaller on Windows, Conda can be set up as described above.

On macOS, however, Conda must be [set up differently](https://github.com/pyinstaller/pyinstaller/issues/2270#issuecomment-385219881), or PyInstaller will fail when trying to process the h5py dependency on NumPy, with an error mentioning "mkl": 

    $ conda create --name python-dist-demo python=3.10
    $ conda activate python-dist-demo
    $ conda install -c conda-forge numpy
    $ conda install h5py

The actual running of PyInstaller is the same on Windows and macOS:

    $ cd python-dist-demo/demo1
    $ pyinstaller demo1.py --onefile

PyInstaller does produce a working executable.  But it starts up _very_ slowly every time it is run, so PyInstaller does not seem like a good solution.

### Nuitka

Nuitka on macOS needs the same Conda set up that PyInstaller needs, to avoid problems with "mkl":

    $ conda create --name python-dist-demo python=3.10
    $ conda activate python-dist-demo
    $ conda install -c conda-forge numpy
    $ conda install h5py

Nuitka then needs special arguments to create a standard macOS "application", which is really directory hierarchy with a special structure:

    $ cd python-dist-demo/demo1
    $ python -m nuitka --standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION demo1.py

The `--include-data-files` argument is necessary for Nuitka to copy the `VERSION` file into the final bundle.  Note from the output of the demo, below, that where the `VERSION` file is different when running in a bundled executable and when running as a standard Python script; see the code for details.

On macOS, run this demo as follows:

    $ demo1.app/Contents/MacOS/demo1 -i path/to/example.h5j
    Checking for 'python-dist-demo/demo1/demo1.app/Contents/VERSION'
    Checking for 'python-dist-demo/demo1/demo1.app/Contents/MacOS/VERSION'
    Version 1.0.0
    Using input file: path/to/example.h5j
    H5J dimensions: 1210, 566, 174

It starts up slowly the first time it is run, but quickly on all subsequent runs, making it quite usable in general.  This example is simple, but there are no signs of errors due to the compilation performed by Nuitka.

On Windows, Nuitka needs the `--include-data-files` argument again:

    $ cd python-dist-demo/demo1
    $ python -m nuitka --onefile --include-data-files=../VERSION=VERSION demo1.py

On Windows, run this demo as follows:

    $ demo1.exe -i path\to\example.h5j
    Checking for 'C:\Users\X\AppData\Local\Temp\VERSION'
    Checking for 'C:\Users\X\AppData\Local\Temp\onefile_21180_133207798981204030\VERSION'
    Version 1.0.0
    Using input file: path\to\example.h5j
    H5J dimensions: 1210, 566, 174

Performance on Windows does not seem quite as good as on macOS, but still, it is better than PyInstaller.

On both macOS and Windows, the executables are rather large.
