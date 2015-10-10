
import os
import shutil
import fnmatch


class TempDir():
    
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        delete(self.path)
        mkdir(self.path)
        return self.path

    def __exit__(self, type, value, traceback):
        delete(self.path)

    def __str__(self):
        return self.path


def mkdir(path):
    if os.path.exists(path) and os.path.isdir(path):
        # nothing to do
        pass
    else:
        os.makedirs(path)

def find(dirSrc, pattern=None):
    out = []
    for root, dirs, files in os.walk(dirSrc):
        for file in files:
            path = os.path.join(root, file)[len(dirSrc) + 1:]
            if pattern is None or fnmatch.fnmatch(path, pattern):
                out.append(path)
    return out

def cp(pathSrc, pathDest):
    (dirParent, filename) = os.path.split(pathDest)

    try:
        os.makedirs(dirParent)
    except:
        pass
    shutil.copy2(pathSrc, pathDest)

def copy(dirDest, pathSrc, renameTo=None):
    (dirParent, filename) = os.path.split(pathSrc)
    if renameTo is None:
        renameTo = filename
    pathDest = os.path.join(dirDest, renameTo)
    cp(pathSrc, pathDest)

def copyTree(dirDest, dirSrc, paths):
    for path in paths:
        pathSrc = os.path.join(dirSrc, path)
        pathDest = os.path.join(dirDest, path)
        dirParent = os.path.dirname(pathDest)
        if not os.path.isdir(dirParent):
            os.makedirs(dirParent)
        shutil.copy2(pathSrc, pathDest)

def delete(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
    except:
        # don't care if it failed
        pass

