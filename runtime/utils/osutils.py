import platform
import runtime.lib.ssjb as ssjb

def getOS():
    out = ""
    if "Windows" in platform.platform():
        out = "Win-"
    if "Linux" in platform.platform():
        out = "Linux-"
    if "Osx" in platform.platform():
        out = "Osx-"
    return out + str(ssjb.getJvmBitness())