# python-dist-demo

## Introduction

Open science involves sharing of code, and Python is a popular language for that code.  Scientists may be reluctant, though, to try shared Python code when doing so involves many installation steps, like installing [Conda](https://docs.conda.io/en/latest/), installing packages, installing other packages with [Pip](https://pypi.org/project/pip/), possibly resolving package conflicts, etc.

An appealing alternative is to "bundle" the Python code and its dependencies into a single executable that can be downloaded from the "Releases" section of a GitHub site.  This project is a test bed for working out the detals of such an approach.  This project is called a "demo" rather than a "test" just in case any of the tools involved implicitly assume that items with names including "test" are parts of an internal test suite.

[This article](https://www.infoworld.com/article/3656628/6-ways-to-package-python-apps-for-re-use.html) gives an overview of some systems for bundling Python code and dependencies for release.  Based on this article, the systems tested in this project are:

* [PyInstaller](https://pyinstaller.org/en/stable/)
* [Nuitka](https://nuitka.net/)

Nuitka is the more ambitious system, converting the Python code into C code that is compiled with optimization.  As such, it has a higher risk of producing an output executable that does not behavior exactly the same as the input Python code.

Note that these systems do not create a single executable that can run on any platform.  It is necessary to perform the executable creation separately on macOS, Windows and Linux.

## Distributing Executables

To distribute executables, include them in the ["Releases" section of the GitHub site](https://github.com/JaneliaSciComp/python-dist-demo/releases) for the source code.  Releases cannot include directories (folders), which is the real format of a macOS app bundle.  So a macOS app must be compressed into a single "zipped" file by right-clicking on it and choosing the "Compress" item from the pop-up menu.

A Windows executable is a single file, so it can be added to a GitHub release directly, but it will be smaller (and thus faster to download) if it is compressed to a zipped file, too.  Right-click on the Windows executable, choose "Send to" and then "Compressed (zipped) folder".

There seems to be no way to _add_ executables (binaries) to a release that has been published, so be careful to assemble all the pieces of the release before publishing it.  Releasing executables for multiple platforms at once usually requires using multiple computers, so use the followwing approach:
1. On one computer&mdash;say, a macOS system&mdash;start creating the release.  Follow the directions in the [GitHub documetation on releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), which involves defining a new tag to be applied to the repository.
2. Add the zipped macOS executable by dragging it to the draft release's input area labeled, "Attach binaries by dropping them here or selecting them."
3. Instead of pressing "Publish release", press "Save draft" so it will be available for further editing.
4. On the other computer&mdash;say, a Windows system&mdash;visit the GitHub site's "Releases" section and find the draft release.
5. Resume editing the draft release by pressing the pencil icon.
6. Add the zipped Windows executable to the "Binaries" section of the draft release by dragging it to the "Attach binaries..." area.
7. Finally, press the "Publish release" button to make the release public now that it is fully assembled.

A user then downloads an executable from the release and uncompresses it.  On Windows, uncompressing simply involves right-clicking on the zipped file and choosing "Extract" from the pop-up menu (that option may be in a submenu, "7-Zip" for example).

On macOS, downloading and using the executable requires extra steps due to Apple's security measures.
1. When downloading, the web browser may display a message saying the zip file "is not commonly downloaded and may be dangerous."  Press the  `⌃` (up chevron) symbol and choose "Keep".
2. The zip file now appears in the `Downloads` folder.  Double click on the zip file to decompress it.
3. _Control_-click on the decompressed executable (.app file) and choose "Open" from the pop-up menu.
4. A dialog will appear, saying the app "can't be opened because Apple cannot check it for malicious software."
5. Choose the "Open" option from this dialog.
6. The executable should now be ready for use.

The macOS user can avoid these extra steps if the developer is willing to pay (roughly $100 per year) to join the [Apple Developer Program](https://developer.apple.com/programs).  Members of this program can apply _code signing_ to an executable so it will pass Apple's security measures automatically.  Apple expects that the typical way to apply code signing is through the [Xcode](https://developer.apple.com/xcode) development environment, but developers bundling Python scripts may well not work that way, and can use the following alternative approach:
1. [Log in](https://developer.apple.com/account) to an Apple Developer Program account.
2. Go to the page for [creating a new certification](https://developer.apple.com/account/resources/certificates/add).
3. Under "Software", choose "Developer ID Application:
This certificate is used to code sign your app for distribution outside of the Mac App Store," and press "Continue".
4. Under "Select a Developer ID Certificate Intermediary", choose a "Profile Type" of "G2 Sub-CA (Xcode 11.4.1 or later)".
5. Click "Learn more" to [create a certificate signing request](https://developer.apple.com/help/account/create-certificates/create-a-certificate-signing-request).
5. Follow the steps, noting that the `Certificate Assistant` that is mentioned is accessible through the `Keychain Access` application, in its menu also called "Keychain Access", right next to the Apple menu in the main menu bar.
6. Two files will be created: `CertificateSigningRequest.certSigningRequest` and `developerID_application.cer`.  Double-click the _second_, the `.cer` file.
7. Add `developerID_application.cer` to the `Login` keychain (adding it to `Local items` may cause an `Error: -25294`)
8. Back in the main `Keychain Access` application window, a new item should appear in the `Certificates` tab.  If it is red, with an error message, try [downloading the "Developer ID - G2 (Expiring 09/17/2031 00:00:00 UTC)" certificate](https://www.apple.com/certificateauthority) and double-clicking to install _it_ in the keychain.
9. In a shell, execute:

        $ security find-identity -v -p codesigning

    The result will be something like:
    
          1) C83C...5335 "Developer ID Application: ... (...)"
            1 valid identities found

    The long hexidecimal identifier (e.g., `C83C...5335`) is the _code signing identity_, which can be used with Nuitka's `--macos-sign-identity` option, as [described below](#nuitka).

## Running Executables

For systems without a user interface, a user will run the executable from a command-line shell.  On macOS, doing so involves reaching down into the app bundle as follows:

```
$ example.app/Contents/MacOS/example -arg1 -arg2
```
If the user moves the app to the standard location, the command would be the following:
```
$ /Applications/example.app/Contents/MacOS/example -arg1 -arg2
```

On Windows, running the executable is simpler:
```
$ example.exe -arg1 -arg2
```
It becomes somewhat more complicated if the user moves the executable to the standard location, `C:\Program Files`, because the path then involves spaces.  When using the basic Command Prompt application as the shell, spaces are handled by simply adding quotes:
```
$ "C:\Program Files\Example\example.exe" -arg1 -arg2
```
In PowerShell, a `.` (dot) must precede the executable path to run it:
```
$ . "C:\Program Files\Example\example.exe" -arg1 -arg2
```

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

#### MacOS

Nuitka on macOS needs the same Conda set up that PyInstaller needs (i.e., getting NumPy from conda-forge), to avoid problems with "mkl":

    $ conda create --name python-dist-demo python=3.10
    $ conda activate python-dist-demo
    $ conda install -c conda-forge numpy
    $ conda install h5py
    $ python -m pip install nuitka

Nuitka then needs special arguments to create a standard macOS "application", which is really directory hierarchy with a special structure:

    $ cd python-dist-demo/demo1
    $ python -m nuitka --standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION demo1.py

The `--include-data-files` argument is necessary for Nuitka to copy the `VERSION` file into the final bundle.  Note from the output of the demo, below, that where the `VERSION` file is different when running in a bundled executable and when running as a standard Python script; see the code for details.

When using macOS code signing, as [described above](#distributing-executables), add the `--macos-sign-identity=C83C...5335` argument, where `C83C...5335` is the code signing identity found with the `security find-identity` command:

    $ python -m nuitka --standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION --macos-sign-identity=C83C...5335 demo1.py

On macOS, run this demo as follows:

    $ demo1.app/Contents/MacOS/demo1 -i path/to/example.h5j
    Checking for 'python-dist-demo/demo1/demo1.app/Contents/VERSION'
    Checking for 'python-dist-demo/demo1/demo1.app/Contents/MacOS/VERSION'
    Version 1.0.0
    Using input file: path/to/example.h5j
    H5J dimensions: 1210, 566, 174

It starts up slowly the first time it is run, but quickly on all subsequent runs, making it quite usable in general.  This example is simple, but there are no signs of errors due to the compilation performed by Nuitka.

#### Windows

On Windows, getting NumPy from conda-forge is not needed (in fact, it does not seem to work), so it can be installed implicitly as a dependency for H5py.  To make a single executable, use Nuitka's `--onefile` argument instead of `--standalone`, and continue to use `--include-data-files`:

    $ conda create --name python-dist-demo python=3.10
    $ conda activate python-dist-demo
    $ conda install h5py
    $ python -m pip install nuitka
    $ cd python-dist-demo/demo1
    $ python -m nuitka --onefile --include-data-files=../VERSION=VERSION demo1.py

Run this demo on Windows as follows:

    $ demo1.exe -i path\to\example.h5j
    Checking for 'C:\Users\X\AppData\Local\Temp\VERSION'
    Checking for 'C:\Users\X\AppData\Local\Temp\onefile_21180_133207798981204030\VERSION'
    Version 1.0.0
    Using input file: path\to\example.h5j
    H5J dimensions: 1210, 566, 174

Performance on Windows does not seem quite as good as on macOS, but still, it is better than PyInstaller.

#### Linux

On Linux (Ubuntu 20.04, at least) two additional packages are needed: libpython-static and patchelf.

    $ conda create --name python-dist-demo python=3.10
    $ conda activate python-dist-demo
    $ conda install h5py libpython-static patchelf
    $ python -m pip install nuitka
    $ cd python-dist-demo/demo1
    $ python -m nuitka --onefile --include-data-files=../VERSION=VERSION demo1.py

Run this demo on Linux as follows:

    $ ./demo1.bin -i path\to\example.h5j
    Checking for '/tmp/VERSION'
    Checking for '/tmp/onefile_2083980_1686061142_611326/VERSION'
    Version 1.0.0
    Using input file: path\to\example.h5j
    H5J dimensions: 1210, 566, 174

On Windows and Linux, the `--onefile` option makes compilation take a long time.  On all platforms, the executables are rather large.

## Demo 2

_What to try next_?
* _Some actualy NumPy functionality on the data in a H5J file_?
* [_Blender as a Python module_](https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html)?