import runtime.downloader as downloader
import urllib2
import runtime.utils.whereis as whereis
import os
import json
import zipfile
import runtime.lib.ssjb.file
import runtime.lib.ssjb as ssjb
import runtime.utils.osutils as osutils
from os.path import expanduser

def downloadMCplusLibs(side,mcversion):
    print("Preparing to get Minecraft jar and its libs")
    version = urllib2.urlopen("http://s3.amazonaws.com/Minecraft.Download/versions/versions.json")
    versionJson = json.load(version)
    version.close()
    versions = []
    for x in versionJson["versions"]:
        versions.append(x["id"])
    if mcversion not in versions:
        print("[ERROR] The version you supplied in the config does not exist!: %s" % mcversion)
        exit(-1)
    if side == "Client" or side == "Both":
        sysAdd = ""
        if "Win" in osutils.getOS():
            sysAdd = "/AppData/Roaming"
        print("Searching for Client jar in %s" % expanduser("~")+sysAdd+"/.minecraft")
        jar = whereis.whereis(mcversion+".jar",expanduser("~")+sysAdd+"/.minecraft",["assets","saves"])
        if jar is not None:
            print("Jar located at %s." % jar[0])
            print("Client jar located copying to working dir.");
            ssjb.file.cp(jar[0]+"/"+mcversion+".jar",os.getcwd()+"/jars/versions/"+mcversion+"/"+mcversion+".jar")
        else:
            print("Client jar not loacted attemping to download.")
            try:
                downloader.DownloadZip(os.getcwd()+"/jars/versions/"+mcversion+"/"+mcversion+".jar","http://s3.amazonaws.com/Minecraft.Download/versions/" + mcversion+"/"+mcversion+".jar",mcversion + " Client Jar")
            except:
                print("Download failed. Please check your internet connection.")
                exit(-1)
        libjson = urllib2.urlopen("http://s3.amazonaws.com/Minecraft.Download/versions/<version>/<version>.json".replace("<version>",mcversion))
        libs = json.load(libjson)["libraries"]
        libjson.close()
        print("Searching for %s in %s" % ("libs",expanduser("~")+sysAdd+"/.minecraft/libraries"))
        for x in libs:
            libinfo = x["name"].split(":")
            if "natives" in x.keys():
                if "Win" in osutils.getOS():
                    downloadLib(libinfo[0],libinfo[1],libinfo[2],"-"+x["natives"]["windows"].replace("${arch}",osutils.getOS().split("-")[1]))
                if "Linux" in osutils.getOS():
                    downloadLib(libinfo[0],libinfo[1],libinfo[2],"-"+x["natives"]["linux"].replace("${arch}",osutils.getOS().split("-")[1]))
                if "Osx" in osutils.getOS():
                    downloadLib(libinfo[0],libinfo[1],libinfo[2],"-"+x["natives"]["osx"].replace("${arch}",osutils.getOS().split("-")[1]))
            else:
                downloadLib(libinfo[0],libinfo[1],libinfo[2])
    if side == "Server" or side == "Both":
        downloader.DownloadZip(os.getcwd()+"/jars/"+mcversion+"-server.jar",
                               " http://s3.amazonaws.com/Minecraft.Download/versions/"+mcversion+"/minecraft_server." +
                               mcversion+".jar",mcversion + " Server Jar")


def downloadLib(package,name,version,native=""):
    print("Attemping to get %s from your Minecraft installation."%name)
    sysAdd = ""
    if "Win" in osutils.getOS():
        sysAdd = "\\AppData\\Roaming"
    NatAdd = ""
    if downloader.isZip(os.getcwd()+"/jars/libraries/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name +"-"+version+NatAdd+".jar"):
        print("Skipped")
        pass
    if native is not "":
        NatAdd = native
    lib = whereis.whereis(name +"-"+version+NatAdd+".jar",expanduser("~")+sysAdd+"/.minecraft/libraries")
    if lib is not None:
        print("%s located at %s." % (name,lib[0]))
        ssjb.file.cp(lib[0]+"/"+name +"-"+version+NatAdd+".jar",os.getcwd()+"/jars/libraries/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name +"-"+version+NatAdd+".jar")
    else:
         downloader.DownloadZip(os.getcwd()+"/jars/libraries/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name +"-"+version+NatAdd+".jar","https://libraries.minecraft.net/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name+"-"+version+NatAdd+".jar",name)


def downloadFernflowerAndSpecialSoruce():
    downloader.DownloadZip(os.getcwd()+"/libs/fernflower.jar","https://hub.spigotmc.org/stash/projects/SPIGOT/repos/builddata/browse/bin/fernflower.jar?at=264466a4bebb5aa2b41b66c5009b098a8f2e90dc&raw","Fernflower Jar")
    downloader.DownloadZip(os.getcwd()+"/libs/specialSoruce.jar","https://hub.spigotmc.org/stash/projects/SPIGOT/repos/builddata/browse/bin/SpecialSource.jar?at=c48104cb841f7e7740aced01792b5aa79bed4278&raw","SpecialSoruce Jar")


def downloadMappings(maptype,mcversion,mapversion,side):
    """Downloads the mappings.   For MCP these mappings are hosted on my github. For Engima the mappings are from
    cuchaz's bitbucket.  The mapVersion is for MCP and Enigma  with enigma it is the commit to use and with MCP it
    is the MCPBot snapshot to use"""

    if(maptype == "Engima"):
        pass
    if(maptype == "MCP"):
        try:
            os.rmdir(os.getcwd()+"/mappings/")
        except:
            pass
        downloader.DownloadFile(os.getcwd()+"/mappings/joined.srg","https://raw.githubusercontent.com/chibill/Minecraft-Mappings/master/Mappings/mcp/"+mcversion+".srg","Mappings")

        if "mcp_stable" in mapversion:
            downloader.DownloadZip(os.getcwd()+"/tmp/mapversion.zip","http://export.mcpbot.bspk.rs/mcp_stable/"+mapversion[11:]+"/"+mapversion+".zip","Extra mapping data")
            test = zipfile.ZipFile(os.getcwd()+"/tmp/mapversion.zip")
            test.extractall(os.getcwd()+"/mappings/")
            test.close()
def deobf(mapType,mcVersion,mapVersion,side):
    """De-obfuscates the actual files"""


def decompile(mcVersion,side):
    """Decompiles the files"""


def editor(editor):
    """Generates the editor related files"""
