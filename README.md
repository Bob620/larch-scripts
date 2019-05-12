## Install/Run
Since XRayLarch has a lot of problems, we need to install the module manually. However, it fails to install a bunch of
the requirements (at least on Win10, I need to do more testing). Because of this the process is way more intensive than
it should be.

This is implemented in python 3.6/3.7

First off:
```commandline
pip install xraylarch
```

Which will fail to correctly install requirements, thus we need to install them manually.

```commandline
pip install matplotlib scipy numpy sqlalchemy h5py requests pyshortcuts lmfit sklearn
```

This codebase uses matplotlib (specifically pyplots) to handle graphing and scipy for 1 smoothing algorithm.

## Code Stuff
This code is a mess and should only be used to test things at this point, I give no suggestion it will work.