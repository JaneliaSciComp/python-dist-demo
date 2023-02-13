# Normal usage:
# $ conda create --name python-dist-demo
# $ conda activate python-dist-demo
# $ conda install h5py
# $ python demo1 -i path/to/example.h5j

# When bundling with PyInstaller or Nuitka on macOS, though, that approach can fail with
# errors referring to "MKL" (as of early spring, 2023).  A work-around is to install the
# packages differently:
# $ conda create --name python-dist-demo python=3.10
# $ conda activate python-dist-demo
# $ conda install -c conda-forge numpy
# $ conda install h5py
# $ python -m nuitka --standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION demo1.py

import argparse
import h5py
import os
import sys

def report_version():
    ver_paths = []
    cwd = os.path.dirname(os.path.realpath(__file__))
    pcwd = os.path.dirname(cwd)

    # For running the script directly with Python.
    ver_path = os.path.join(pcwd, "VERSION")
    ver_paths.append(ver_path)

    # Necessary for use with Nuitka, when it creates an app bundle on macOS or
    # a single exe on Windows.
    # MacOS: `--standalone --macos-create-app-bundle --include-data-files=../VERSION=VERSION`
    # Windows: `--onefile --include-data-files=../VERSION=VERSION`
    ver_path = os.path.join(cwd, "VERSION")
    ver_paths.append(ver_path)

    for ver_path in ver_paths:
        print("Checking for '{}'".format(ver_path))
        if os.path.exists(ver_path):
            try:
                with open(ver_path) as ver_file:
                    ver = ver_file.read().strip()
                    print("Version {}".format(ver))
                    break
            except:
                pass

def get_vol_int_attr(attrs, name):
    val = 0
    if name in attrs:
        val = attrs[name]
        if not isinstance(val, int):
            val = val[0]
    return val

def get_vol_bbox(path):
    dx = dy = dz = 0
    with h5py.File(path, "r") as f:
        attrs = f["Channels"].attrs
        dx = get_vol_int_attr(attrs, "width")
        dy = get_vol_int_attr(attrs, "height")
        dz = get_vol_int_attr(attrs, "frames")
    return (dx, dy, dz)  

def report_h5j_metadata(input):
    bbox = get_vol_bbox(input)
    print("H5J dimensions: {}, {}, {}".format(bbox[0], bbox[1], bbox[2]))

if __name__ == "__main__":
    report_version()
    
    parser = argparse.ArgumentParser()
    parser.set_defaults(input="")
    parser.add_argument("--input", "-i", dest="input", help="path to input H5J file")
    args = parser.parse_args()

    if not args.input:
        print("Please specify an input H5J files with the .h5j extension")
        sys.exit()

    if os.path.splitext(args.input)[1] != ".h5j":
        print("Input file '{}' does not have the '.h5j' extension.".format(args.input))
        sys.exit()

    print("Using input file: {}".format(args.input))
    report_h5j_metadata(args.input)
