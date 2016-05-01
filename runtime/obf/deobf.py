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
import shutil
import runtime.utils.cleanup_src as cs

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
            except Exception as e:
                print e
                print("Download failed. Please check your internet connection.")
                exit(-1)
        libjson = urllib2.urlopen("http://s3.amazonaws.com/Minecraft.Download/versions/<version>/<version>.json".replace("<version>",mcversion))
        libs = json.load(libjson)["libraries"]
        libjson.close()
        print("Searching for libraries in your .minecraft. Will download if they ar enot present")
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
        print("Downloading Server jar")
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
        #print("Skipped")
        pass
    if native is not "":
        NatAdd = native
    lib = whereis.whereis(name +"-"+version+NatAdd+".jar",expanduser("~")+sysAdd+"/.minecraft/libraries")
    if lib is not None:
        #print("%s located at %s." % (name,lib[0]))
        ssjb.file.cp(lib[0]+"/"+name +"-"+version+NatAdd+".jar",os.getcwd()+"/jars/libraries/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name +"-"+version+NatAdd+".jar")
    else:
         downloader.DownloadZip(os.getcwd()+"/jars/libraries/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name +"-"+version+NatAdd+".jar","https://libraries.minecraft.net/"+package.replace(".","/")+"/"+name+"/"+version+"/"+name+"-"+version+NatAdd+".jar",name)


def downloadDecompAndDeobf(Config):
    print("Downloading Decompiler")
    downloader.DownloadZip(os.getcwd()+"/libs/decomp.jar",Config["DecompilerUrl"],"Decompiler Jar")
    print("Downloading De-obfuscator")
    downloader.DownloadZip(os.getcwd()+"/libs/deobf.jar",Config["DeobfuscatorUrl"],"Deobfuscator Jar")


def downloadMappings(mcversion,mapversion,side):
    """Downloads the mappings.   For Engima the mappings are from cuchaz's bitbucket.
    mapversion is the commit of the mappings you want."""
    map = urllib2.urlopen("https://minecraft16.ml/enigma.json")
    versions = json.load(map)
    map.close()
    if side == "Client" or side == "Server":
        downloadurl = versions[mcversion][side].replace("mapversion",mapversion)
        downloader.DownloadFile(os.getcwd()+"/mappings/enigma-"+side.lower()+".mappings",downloadurl,"Enigma Mappings")
    else:
        downloadurl = versions[mcversion]["Client"].replace("mapversion",mapversion)
        downloader.DownloadFile(os.getcwd()+"/mappings/enigma-client.mappings",downloadurl,"Enigma Mappings")
        downloadurl2 = versions[mcversion]["Server"].replace("mapversion",mapversion)
        downloader.DownloadFile(os.getcwd()+"/mappings/enigma-server.mappings",downloadurl2,"Enigma Mappings")


def deobf(mcVersion,side,Config):
    """De-obfuscates the actual files"""
    if side == "Client":
        os.system(Config["DeobfuscatorCommand"].replace("<path-to-deobfuscator>",os.getcwd()+"/libs/deobf.jar").replace("<in-jar>",os.getcwd()+"/jars/versions/"+mcVersion+"/"+mcVersion+".jar").replace("<out-jar>",os.getcwd()+"/tmp/client-deobf.jar").replace("<map>",os.getcwd()+"/mappings/enigma-client.mappings"))
    if side == "Server":
        os.system(Config["DeobfuscatorCommand"].replace("<path-to-deobfuscator>",os.getcwd()+"/libs/deobf.jar").replace("<in-jar>",os.getcwd()+"/jars/"+mcversion+"-server.jar").replace("<out-jar>",os.getcwd()+"/tmp/server-deobf.jar").replace("<map>",os.getcwd()+"/mappings/enigma-server.mappings"))
    if side == "Both":
        os.system(Config["DeobfuscatorCommand"].replace("<path-to-deobfuscator>",os.getcwd()+"/libs/deobf.jar").replace("<in-jar>",os.getcwd()+"/jars/versions/"+mcVersion+"/"+mcVersion+".jar").replace("<out-jar>",os.getcwd()+"/tmp/client-deobf.jar").replace("<map>",os.getcwd()+"/mappings/enigma-client.mappings"))
        os.system(Config["DeobfuscatorCommand"].replace("<path-to-deobfuscator>",os.getcwd()+"/libs/deobf.jar").replace("<in-jar>",os.getcwd()+"/jars/"+mcversion+"-server.jar").replace("<out-jar>",os.getcwd()+"/tmp/server-deobf.jar").replace("<map>",os.getcwd()+"/mappings/enigma-server.mappings"))


def decompile(side,Config):
    """Decompiles the files"""
    try:
        shutil.rmtree(os.getcwd()+"/src")
    except:
        pass
    try:
        os.makedirs(os.getcwd()+"/tmp/decomp")
    except:
        pass
    if side == "Client" or side == "Both":
        print("Decompiling Client")
        os.system(Config["DecompilerCommand"].replace("<path-to-decompiler>",os.getcwd()+"/libs/decomp.jar").replace("<jar-in>",os.getcwd()+"/tmp/client-deobf.jar").replace("<jar-out>",os.getcwd()+"/tmp/decomp"))
        print("Extracting Client src")
        test = zipfile.ZipFile(os.getcwd()+"/tmp/decomp/client-deobf.jar")
        test.extractall(os.getcwd()+"/src/minecraft/")
        test.close()
    if side == "Server" or side == "Both":
        print("Decompiling Server")
        os.system(Config["DecompilerCommand"].replace("<path-to-decompiler>",os.getcwd()+"/libs/decomp.jar").replace("<jar-in>",os.getcwd()+"/tmp/server-deobf.jar").replace("<jar-out>",os.getcwd()+"/tmp/decomp"))
        print("Extracting Server src")
        test = zipfile.ZipFile(os.getcwd()+"/tmp/decomp/server-deobf.jar")
        test.extractall(os.getcwd()+"/src/minecraft-server/")
        test.close()
def cleanup_src():
    print("Cleaning up the src a bit")
    cs.strip_comments(os.getcwd()+"/src/")

def editor(editor):
    """Generates the editor related files"""
    print("Generating editor related files")
