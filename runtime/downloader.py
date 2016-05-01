import os
import sys
import urllib
import zipfile
import os.path
from runtime.lib.tqdm import tqdm

def my_hook(t):
  """
  Wraps tqdm instance. Don't forget to close() or __exit__()
  the tqdm instance once you're done with it (easiest using `with` syntax).

  Example
  -------

  >>> with tqdm(...) as t:
  ...     reporthook = my_hook(t)
  ...     urllib.urlretrieve(..., reporthook=reporthook)

  """
  last_b = [0]

  def inner(b=1, bsize=1, tsize=None):
    """
    b  : int, optional
        Number of blocks just transferred [default: 1].
    bsize  : int, optional
        Size of each block (in tqdm units) [default: 1].
    tsize  : int, optional
        Total size (in tqdm units). If [default: None] remains unchanged.
    """
    if tsize is not None:
        t.total = tsize
    t.update((b - last_b[0]) * bsize)
    last_b[0] = b
  return inner

def isZip(input):
    try:
        test = zipfile.ZipFile(input)
        test.close()
        return True
    except:
        return False


def DownloadZip(SaveLoc,DownloadURL,Item,Canskip=True):
   # print("Preparing to download - "+ Item)
    (dirParent, filename) = os.path.split(SaveLoc)
    try:
       os.makedirs(dirParent)
    except:
       pass
    skip = isZip(SaveLoc)
    if not Canskip:
        skip = False
    if not skip:
        if os.path.exists(SaveLoc):
            os.remove(SaveLoc)
        
        with tqdm(unit='B', unit_scale=True, leave=True, miniters=1,
          desc=Item) as t:
            urllib.urlretrieve(DownloadURL,SaveLoc , reporthook=my_hook(t))
      #  sys.stdout.flush()
    else:
        print("Fetching "+Item+" - SKIPPED")
    print("\n")

def DownloadFile(SaveLoc,DownloadURL,Item):
    (dirParent, filename) = os.path.split(SaveLoc)
    try:
       os.makedirs(dirParent)
    except:
       pass
    if(os.path.exists(SaveLoc)):
        os.remove(SaveLoc)
    with tqdm(unit='B', unit_scale=True, leave=True, miniters=1,
          desc=Item) as t:
        urllib.urlretrieve(DownloadURL,SaveLoc , reporthook=my_hook(t))
    print("\n")
