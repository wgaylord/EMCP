
import os
import zipfile
import tempfile

import runtime.lib.ssjb


def buildManifest(title, version, author, mainClass=None):
    manifest = {
        "Title": title,
        "Version": version,
        "Created-by": author
    }
    if mainClass is not None:
        manifest["Main-Class"] = mainClass
    return manifest

def makeJar(pathOut, dirIn, dirRoot=None, manifest=None):

    # build the base args
    if dirRoot is None:
        dirRoot = dirIn
        dirIn = "."
    invokeArgs = ["jar"]
    filesArgs = ["-C", dirRoot, dirIn]

    if manifest is not None:
        # make a temp file for the manifest
        tempFile, tempFilename = tempfile.mkstemp(text=True)
        try:
            # write the manifest
            for (key, value) in manifest.iteritems():
                os.write(tempFile, "%s: %s\n" % (key, value))
            os.close(tempFile)

            # build the jar with a manifest
            ssjb.call(invokeArgs + ["cmf", tempFilename, pathOut] + filesArgs)

        finally:
            os.remove(tempFilename)
    else:
        # just build the jar without a manifest
        ssjb.call(invokeArgs + ["cf", pathOut] + filesArgs)

    print ("Wrote jar: %s" % pathOut)

def unpackJar(dirOut, pathJar, allow=None):
    with zipfile.ZipFile(pathJar) as zf:
        for info in zf.infolist():
            if allow is None or allow(info):
                zf.extract(info, dirOut)
    print ("Unpacked jar: %s" % pathJar)

def unpackJars(dirOut, dirJars, recursive=False):
    for name in os.listdir(dirJars):
        path = os.path.join(dirJars, name)
        if os.path.isfile(path):
            if name[-4:] == ".jar":
                unpackJar(dirOut, path)
        elif os.path.isdir(path) and recursive:
            unpackJars(dirOut, path, recursive)

