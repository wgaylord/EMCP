import runtime.lib.ssjb as ssjb
import runtime.obf.deobf as deobf
import json
import os

#Used for testing new mappings and also making new ones.
SkipMappingDownload = True

#Will skip patching of the files if I ever have to do patching
SkipPatching = False

Config = {}

HEADER = """
 .----------------.  .----------------.  .----------------.  .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. |
| |  _________   | || | ____    ____ | || |     ______   | || |   ______     | |
| | |_   ___  |  | || ||_   \  /   _|| || |   .' ___  |  | || |  |_   __ \   | |
| |   | |_  \_|  | || |  |   \/   |  | || |  / .'   \_|  | || |    | |__) |  | |
| |   |  _|  _   | || |  | |\  /| |  | || |  | |         | || |    |  ___/   | |
| |  _| |___/ |  | || | _| |_\/_| |_ | || |  \ `.___.'\  | || |   _| |_      | |
| | |_________|  | || ||_____||_____|| || |   `._____.'  | || |  |_____|     | |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'

Created by Chibill as replacement for MCP
EMCP stands for Enigma Minecraft Coder Pack.
Designed for use with Enigma's mappings
"""


def read_config(rel_path="config.conf"):
    with open(os.path.join(os.getcwd(), rel_path)) as in_file:
        return json.load(in_file)


def deobfuscate():
    """Deobfuscates Minecraft using the setting supplied in the setting file. Then decompiles it"""

    print("""Config is targeting version {MC Verson} with a side of: {Side}
Using Enigma Mappings with there version being: {Mapping Version}
The editor files will be built for: {Editor}""".format(**Config))
    mcVersion = Config["MC Verson"]
    side = Config["Side"]
    deobf.downloadMCplusLibs(side, mcVersion)
    deobf.downloadDecompAndDeobf(Config)
    deobf.downloadMappings(mcVersion, Config["Mapping Version"], side)
    deobf.deobf(mcVersion, side, Config)
    deobf.decompile(side, Config)
    deobf.cleanup_src()
    # deobf.editor(Config["Editor"])


if __name__ == "__main__":
    print(HEADER)
    print("Reading Config")
    Config = read_config()
    ssjb.registerTask("deobf",deobfuscate)
    ssjb.run()
