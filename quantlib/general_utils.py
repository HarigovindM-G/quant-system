# This is a utility file that allows us to perform simple tasks such as I/O, disk writing etc.
# We use a pickle object. This is like preserving a Python object on your disk.

import pickle


def save_file(path, obj):
    try:
        with open(path, "wb") as fp:
            pickle.dump(obj, fp)
    except Exception as err:
        print("pickle error:", str(err))


def load_file(path):
    try:
        with open(path, "rb") as fp:
            file = pickle.load(fp)
        return file
    except Exception as err:
        print("load error:", str(err))
        return None
