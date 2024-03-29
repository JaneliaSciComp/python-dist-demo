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

Linux executables can be zipped, too, for consistency, but doing so does not seem to make them much smaller.

To release executables for all platforms at once requires some coordination across multiple computers.  Here is an approach that works:
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

The macOS user can avoid these extra steps if the developer is willing to pay (roughly $100 per year) to join the [Apple Developer Program](https://developer.apple.com/programs).  Members of this program can apply _code signing_ and _notarization_ to an executable so it will pass Apple's security measures automatically.  Apple expects that the typical way to apply code signing and notarization is through the [Xcode](https://developer.apple.com/xcode) development environment, but developers bundling Python scripts may well not work that way, and can use the following alternative approach:
1. [Log in](https://developer.apple.com/account) to an Apple Developer Program account.
2. Go to the page for [creating a new certification](https://developer.apple.com/account/resources/certificates/add).
3. Under "Software", choose "Developer ID Application:
This certificate is used to code sign your app for distribution outside of the Mac App Store," and press "Continue".
4. Under "Select a Developer ID Certificate Intermediary", choose a "Profile Type" of "G2 Sub-CA (Xcode 11.4.1 or later)".
5. Click "Learn more" to [create a certificate signing request](https://developer.apple.com/help/account/create-certificates/create-a-certificate-signing-request).
6. Follow the steps, noting that the `Certificate Assistant` that is mentioned is accessible through the `Keychain Access` application, in its menu also called "Keychain Access", right next to the Apple menu in the main menu bar.
7. Two files will be created: `CertificateSigningRequest.certSigningRequest` and `developerID_application.cer`.  Double-click the _second_, the `.cer` file.
8. Add `developerID_application.cer` to the `Login` keychain (adding it to `Local items` may cause an `Error: -25294`)
9. Back in the main `Keychain Access` application window, a new item should appear in the `Certificates` tab.  If it is red, with an error message, try [downloading the "Developer ID - G2 (Expiring 09/17/2031 00:00:00 UTC)" certificate](https://www.apple.com/certificateauthority) and double-clicking to install _it_ in the keychain.
10. In a shell, execute:

        $ security find-identity -v -p codesigning

    The result will be something like:
    
          1) C83C...5335 "Developer ID Application: ... (...)"
            1 valid identities found

    The long hexidecimal identifier (e.g., `C83C...5335`) is the _code signing identity_, which can be used with Nuitka's `--macos-sign-identity` option, as [described below](#nuitka).
11. Build the executable (e.g., using Nuitka) with code signing and hardening.
12. To prepare for notarization, create an _app-specific password_ using the steps [described here](https://support.apple.com/en-us/HT204397). Doing so associates a name in the keychain with an automatically generated password. What is needed in the subsequent steps is the password and not the name, so be sure to keep a record of the password (which will have a form like `abcd-efgh-ijkl-mnop`).
13. As further preparation, look up the _Team ID_ for the Apple Developer Program account as [described here](https://developer.apple.com/help/account/manage-your-team/locate-your-team-id/).
14. Compress the built `.app` file into a `.zip` file by right-clicking on it in the Finder and choosing "Compress".
15. Submit the `.zip` file for notarization with the command:

        $ xcrun notarytool submit <.zip file> --apple-id "<email for Apple Developer Program account>" --team-id <Team ID> --password <app-specific password> --wait

    A prompt will appear for the app-specific password; respond with the password from step 12.  Then messages like the following will appear:

        Submission ID received
        id: e5d1...2028
        Successfully uploaded file33.6 MB of 33.6 MB)    
        id: e5d1...2028
        path: ...zip
        Waiting for processing to complete.

16. After a delay (which might be only a few seconds) a completion notice should appear:

        Current status: Accepted...........
        Processing complete
        id: e5d1...2028
        status: Accepted

    The `.zip` file is now ready to be shared.

17. To avoid entering `--apple-id` and `--team-id` and responding to the password prompt, these credentials can be saved in the keychain. See [this discussion](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow) of `xcrun notarytool store-credentials`.

18. To diagnose problems with code signing or notarization, try the following command:

        $ spctl -a -t exec -vv <.app file>

(Note that the old approach to notarization, using `xcrun altool`, is deprecated, and will stop working in November, 2023.)

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

## Demo 1: HDF5/H5J

The first demo uses [h5py](https://www.h5py.org/) to parse the metadata from the HDF5 part of a volume data set in [H5J format](https://github.com/JaneliaSciComp/workstation/blob/master/docs/H5JFileFormat.md).  Example H5J files can be found [here](https://github.com/JaneliaSciComp/web-h5j-loader#test-data).

This demo also outputs the contents of a `VERSION` file that is part of the GitHub repo, but not a Python dependency per se.

Without bundling, run it as follows:

    $ conda create --name python-dist-demo-1
    $ conda activate python-dist-demo-1
    $ conda install h5py
    $ cd python-dist-demo/demo1
    $ python demo1.py -i path/to/example.h5j
    Checking for 'python-dist-demo/VERSION'
    Version 1.0.0
    Using input file: path/to/example.h5j
    H5J dimensions: 1210, 566, 174

### PyInstaller

To use PyInstaller on Windows, Conda can be set up as described above.

On macOS, however, Conda must be [set up differently](https://github.com/pyinstaller/pyinstaller/issues/2270#issuecomment-385219881)&mdash;i.e., installed from the conda-forge channel&mdash;or PyInstaller will fail when trying to process the h5py dependency on NumPy, with an error mentioning "mkl": 

    $ conda create --name python-dist-demo-1 python=3.10
    $ conda activate python-dist-demo-1
    $ python -m pip install PyInstaller
    $ conda install -c conda-forge numpy
    $ conda install h5py

The actual running of PyInstaller on macOS is:

    $ cd python-dist-demo/demo1
    $ pyinstaller --windowed demo1.py

On Windows and Linux use:

    $ pyinstaller --onefile demo1.py

PyInstaller does produce a working executable.  But it starts up _very_ slowly every time it is run, so PyInstaller does not seem like a good solution.

### Nuitka

#### MacOS

Nuitka on macOS needs the same Conda set up that PyInstaller needs (i.e., getting NumPy from the conda-forge channel), to avoid problems with "mkl":

    $ conda create --name python-dist-demo-1 python=3.10
    $ conda activate python-dist-demo-1
    $ conda install -c conda-forge numpy
    $ conda install h5py
    $ python -m pip install nuitka

Nuitka then needs special arguments to create a standard macOS "application", which is really directory hierarchy with a special structure:

    $ cd python-dist-demo/demo1
    $ python -m nuitka --standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION demo1.py

The `--include-data-files` argument is necessary for Nuitka to copy the `VERSION` file into the final bundle.  Note from the output of the demo, below, that where the `VERSION` file is different when running in a bundled executable and when running as a standard Python script; see the code for details.

When using macOS code signing and notarization, as [described above](#distributing-executables), add the `--macos-sign-notarization` and  `--macos-sign-identity=C83C...5335` arguments, where `C83C...5335` is the code signing identity found with the `security find-identity` command:

    $ python -m nuitka --standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION --macos-sign-notarization --macos-sign-identity=C83C...5335 demo1.py

On macOS, run this demo as follows:

    $ demo1.app/Contents/MacOS/demo1 -i path/to/example.h5j
    Checking for 'python-dist-demo/demo1/demo1.app/Contents/VERSION'
    Checking for 'python-dist-demo/demo1/demo1.app/Contents/MacOS/VERSION'
    Version 1.0.0
    Using input file: path/to/example.h5j
    H5J dimensions: 1210, 566, 174

It starts up slowly the first time it is run, but quickly on all subsequent runs, making it quite usable in general.  This example is simple, but there are no signs of errors due to the compilation performed by Nuitka.

#### Windows

On Windows, getting NumPy from the conda-forge channel is not needed (in fact, it does not seem to work), so it can be installed implicitly as a dependency for H5py.  To make a single executable, use Nuitka's `--onefile` argument instead of `--standalone`, and continue to use `--include-data-files`:

    $ conda create --name python-dist-demo-1 python=3.10
    $ conda activate python-dist-demo-1
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

    $ conda create --name python-dist-demo-1 python=3.10
    $ conda activate python-dist-demo-1
    $ conda install h5py libpython-static patchelf
    $ python -m pip install nuitka
    $ cd python-dist-demo/demo1
    $ python -m nuitka --onefile --include-data-files=../VERSION=VERSION demo1.py

Run this demo on Linux as follows:

    $ ./demo1.bin -i path/to/example.h5j
    Checking for '/tmp/VERSION'
    Checking for '/tmp/onefile_2083980_1686061142_611326/VERSION'
    Version 1.0.0
    Using input file: path/to/example.h5j
    H5J dimensions: 1210, 566, 174

On Windows and Linux, the `--onefile` option makes compilation take a long time.  On all platforms, the executables are rather large.

## Demo 2: Qt

The second demo uses a Python wrapping of the [Qt framework](https://www.qt.io/product/framework) for cross-platform user interface development.  The demo creates a simple application window.  When the user chooses an image file with the "File/Open" menu, the image is displayed in the window in binary black-and-white form based on a threshold value, which the user can control with a vertical slider on the left side of the window.  This demo tests not only basic user-interface elements (windows, menus, image displayers, sliders, etc.) but also more advanced features like threading: the thresholding of the image runs on a worker thread so the main user-interface thread stays fully responsive.

### PyInstaller

As with the first demo, the executables produced by PyInstaller start up too slowly to be useful.  Also, they are larger than those produced by Nuitka, by a factor of 1.8 on macOS, 1.9 on Windows, and 2.7 on Linux.

### Nuitka

As of midyear 2023, Qt 6 is the latest version, and there are two choices for Python wrappings: [PyQt6 and PySide6](https://www.pythonguis.com/faq/pyqt6-vs-pyside6).  Nuitka seems to work better with [PySide6](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html): on macOS, at least, a PyQt6 demo compiled with Nuitka crashes on startup.  Hence, the demo code here uses PySide6. Fortunately, there are [very few differences between the syntax of PySide6 and PyQt6](https://www.pythonguis.com/faq/pyqt6-vs-pyside6).

#### MacOS

As in the first demo, Nuitka has problems with "mkl" unless NumPy is installed from the conda-forge channel.  Note also that Nuitka needs a special argument (`--plugin-enable=pyside6`) to build with PySide6 correctly.

    $ conda create --name python-dist-demo-2 python=3.10
    $ conda activate python-dist-demo-2
    $ python -m pip install nuitka
    $ python -m pip install PySide6
    $ conda install -c conda-forge numpy
    $ python -m nuitka --standalone --macos-create-app-bundle --plugin-enable=pyside6 --macos-sign-notarization --macos-sign-identity=C83C...5335 demo2.py

Double-click on the application in the Finder to run it, or run it from a shell as:

    $ demo2.app/Contents/MacOS/demo2 

### Windows

Build on Windows with the new `--plugin-enable=pyside6` argument, but the default version of NumPy and the `--onefile` argument instead of `--standalone`.  Note also that the `--windows-disable-console` argument prevents an additional terminal shell from appearing when the executable is running.

    $ conda create --name python-dist-demo-2 python=3.10
    $ conda activate python-dist-demo-2
    $ python -m pip install nuitka
    $ python -m pip install PySide6
    $ conda install numpy
    $ python -m nuitka --onefile --plugin-enable=pyside6 --windows-disable-console demo2.py

Double-click on the application in the File Explorer to run it, or run it from a shell as:

    $ .\demo2.exe 

### Linux

A Linux build requires the new `--plugin-enable=pyside6` argument, plus the additional libpython-static and patchelf packages, as with the first demo.

    $ conda create --name python-dist-demo-2 python=3.10
    $ conda activate python-dist-demo-2
    $ python -m pip install nuitka
    $ python -m pip install PySide6
    $ conda install numpy libpython-static patchelf
    $ python -m nuitka --onefile --plugin-enable=pyside6 demo2.py

Run in a shell as:

    ./demo2.bin

On some Linux systems, like Ubuntu 20.04, importing PySide6 into Python might fail with an error like the following:

    qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.

The fix is to install an extra library:

    sudo apt install libxcb-cursor0

## Demo 3

_What to try next_?
* _PyTorch?_
* [_Blender as a Python module_](https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html)?