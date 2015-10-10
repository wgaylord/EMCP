import os
import sys
import urllib
import zipfile
import os.path


def report(count, blockSize, totalSize):
     percent = int(count*blockSize*100/totalSize)
     sys.stdout.write("\r%d%%" % percent + ' complete')
     sys.stdout.flush()


def isZip(input):
     try:
       test = zipfile.ZipFile(input)
       test.close()
       return True
     except:
         return False


def DownloadZip(SaveLoc,DownloadURL,Item):
    print("Preparing to download - "+ Item)
    (dirParent, filename) = os.path.split(SaveLoc)
    try:
       os.makedirs(dirParent)
    except:
       pass
    if(not isZip(SaveLoc)):
        print("File does not exist or is corrupt.")
        if(os.path.exists(SaveLoc)):
            os.remove(SaveLoc)
        sys.stdout.write('\rFetching ' + Item  + '...\n')
        urllib.urlretrieve(DownloadURL,SaveLoc , reporthook=report)
        sys.stdout.flush()
    else:
        print("Fetching "+Item+" - SKIPPED")
    print("\n")

def DownloadFile(SaveLoc,DownloadURL,Item):
    print("Preparing to download - "+ Item)
    (dirParent, filename) = os.path.split(SaveLoc)
    try:
       os.makedirs(dirParent)
    except:
       pass
    if(os.path.exists(SaveLoc)):
        os.remove(SaveLoc)
    sys.stdout.write('\rFetching ' + Item  + '...\n')
    urllib.urlretrieve(DownloadURL,SaveLoc , reporthook=report)
    sys.stdout.flush()
    print("\n")