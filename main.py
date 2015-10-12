import runtime.lib.ssjb as ssjb
import runtime.obf.deobf as deobf
import json
import os

Config = {}

HEADER = """
  _____ __  __  _____ _____
 / ____|  \/  |/ ____|  __ \.
| |    | \  / | |    | |__) |
| |    | |\/| | |    |  ___/
| |____| |  | | |____| |
 \_____|_|  |_|\_____|_|

Created by Chibill as custom coded version of MCP.
CMCP stands for Chibill's MCP or Custom MCP.
Desinged for use with Enigma's mappings
"""


def readconfig():
    global Config
    config = open(os.getcwd()+"/config.conf")
    Config = json.load(config)
    config.close()

def deobfuscate():
    """Deobfuscates Minecraft using the setting supplied in the setting file. Then decompiles it"""

    mcVersion = Config["MC Verson"]
    side = Config["Side"]
    editor = Config["Editor"]
    mapVersion = Config["Mapping Version"]
    print("""Config is targeting version %s with a side of: %s
Using Enigma Mappings with there version being: %s
The editor files will be built for: %s""" % (mcVersion, side, mapVersion, editor))
    deobf.downloadMCplusLibs(side,mcVersion)
    deobf.downloadDecompAndDeobf(Config)
    deobf.downloadMappings(mcVersion,mapVersion,side)
    deobf.deobf(mcVersion,side,Config)
    deobf.decompile(side,Config)
    #deobf.editor(editor)


if __name__ == "__main__":
    print(HEADER)
    print("Reading Config")
    readconfig()
    ssjb.registerTask("deobf",deobfuscate)
    ssjb.run()