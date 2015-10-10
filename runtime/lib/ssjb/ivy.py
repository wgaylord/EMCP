
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

import runtime.lib.ssjb as ssjb

# settings
PathIvy = os.path.join(os.path.dirname(__file__), "ivy-2.4.0.jar")
JarTypes = ["jar", "bundle"]


class Dep():

    def __init__(self, desc, transitive=True, localPath=None):
        parts = desc.split(":")
        self.groupId = parts[0]
        self.artifactId = parts[1]
        self.version = parts[2]
        self.transitive = transitive
        self.localPath = localPath

    def __str__(self):
        return "%s:%s:%s" % (self.groupId, self.artifactId, self.version)

    def getName(self):
        return "%s-%s" % (self.artifactId, self.version)


class TempDir(ssjb.file.TempDir):

    def __init__(self):
        ssjb.file.TempDir.__init__(self, "__ivy_tmp")


def makeLibsJar(pathOutJar, deps, extraRepos=None):

    # download the artifacts
    with TempDir() as dirTemp:
        args = _getIvyArgs(dirTemp, deps=deps, extraRepos=extraRepos)
        _callIvy(args)
        paths = _addLocalPaths(_getPaths(dirTemp, args), deps)

    # combine all the libs into one jar
    with TempDir() as dirTemp:
        for path in paths:
            ssjb.jar.unpackJar(dirTemp, path)
        # delete META-INF files that can conflict
        for glob in ["*.RSA", "*.DSA", "MANIFEST.MF"]:
            for path in ssjb.file.find(dirTemp, glob):
                ssjb.file.delete(os.path.join(dirTemp, path))
        ssjb.jar.makeJar(pathOutJar, dirTemp)

def makeJar(pathOut, dep, extraRepos=None):
    
    dirOut = os.path.dirname(pathOut)
    jarName = os.path.basename(pathOut)

    if dep.localPath is not None:
        # copy the local file
        ssjb.file.copy(dirOut, dep.localPath, renameTo=jarName)
    else:
        # download the artifact
        with TempDir() as dirTemp:
            args = _getIvyArgs(dirTemp, dep=dep, extraRepos=extraRepos, types=JarTypes)
            _callIvy(args)
            paths = _addLocalPaths(_getPaths(dirTemp, args), [dep])
            ssjb.file.copy(dirOut, paths[0], renameTo=jarName)

    # copy the jar
    print ("Wrote ", pathOut)

def getJarPaths(deps, extraRepos=None):
    paths = None
    with TempDir() as dirTemp:
        args = _getIvyArgs(dirTemp, deps=deps, extraRepos=extraRepos, types=JarTypes)
        paths = _addLocalPaths(_getPaths(dirTemp, args), deps)
    return paths

def _getIvyArgs(dirTemp, deps=None, dep=None, extraRepos=None, types=None):
    
    args = []

    # make ivy.xml if needed
    pathIvyXml = None
    if deps is not None:
        pathIvyXml = os.path.join(dirTemp, "ivy.xml")
        with open(pathIvyXml, "w") as file:
            file.write(_getIvyXml(deps))
        args += ["-ivy", pathIvyXml]
    
    # make ivysettings.xml if needed
    pathIvySettingsXml = None
    if extraRepos is not None:
        # make an ivy settings file
        pathIvySettingsXml = os.path.join(dirTemp, "ivysettings.xml")
        with open(pathIvySettingsXml, "w") as file:
            file.write(_getIvySettingsXml(extraRepos))
        args += ["-settings", pathIvySettingsXml]

    if dep is not None:
        if dep.localPath is not None:
            raise Exception("don't call _getIvyArgs with a single locally overridden dependency!")
        args += ["-dependency", dep.groupId, dep.artifactId, dep.version]

    if types is not None:
        args += ["-types"]
        if isinstance(types, list):
            args += types
        else:
            args.append(types)

    return args

def _getPaths(dirTemp, args):
    pathTemp = os.path.join(dirTemp, "classpath.txt")
    _callIvy(args + ["-cachepath", pathTemp])
    paths = None
    with open(pathTemp, "r") as file:
        paths = file.readline().strip().split(ssjb.ClasspathSeparator)
    return paths

def _addLocalPaths(paths, deps):
    for dep in deps:
        if dep.localPath is not None:
            paths.insert(0, dep.localPath)
    return paths

def _prettyPrintXml(elem):
    return xml.dom.minidom.parseString(ET.tostring(elem)).toprettyxml()

def _getIvyXml(deps):
    rootElem = ET.Element("ivy-module")
    rootElem.set("version", "2.0")
    infoElem = ET.SubElement(rootElem, "info")
    infoElem.set("organisation", "no one cares")
    infoElem.set("module", "no one cares")
    infoElem.set("status", "no one cares")
    depsElem = ET.SubElement(rootElem, "dependencies")
    for dep in deps:
        if dep.localPath is None:
            depElem = ET.SubElement(depsElem, "dependency")
            depElem.set("org", dep.groupId)
            depElem.set("name", dep.artifactId)
            depElem.set("rev", dep.version)
            depElem.set("transitive", "true" if dep.transitive else "false")
    return _prettyPrintXml(rootElem)

def _getIvySettingsXml(extraRepos):

    rootElem = ET.Element("ivysettings")
    settingsElem = ET.SubElement(rootElem, "settings")
    settingsElem.set("defaultResolver", "chain")
    resolversElem = ET.SubElement(rootElem, "resolvers")
    chainElem = ET.SubElement(resolversElem, "chain")
    chainElem.set("name", "chain")

    # add the maven central repo by default
    centralElem = ET.SubElement(chainElem, "ibiblio")
    centralElem.set("name", "maven-central")
    centralElem.set("m2compatible", "true")

    # add the extra repos
    for repo in extraRepos:
        repoElem = ET.SubElement(chainElem, "ibiblio")
        repoElem.set("name", repo)
        repoElem.set("root", repo)
        repoElem.set("m2compatible", "true")
    
    return _prettyPrintXml(rootElem)

def _callIvy(args, debug=False):
    baseArgs = [
        "java", "-jar", PathIvy,
        "-m2compatible"
    ]
    if not debug:
        baseArgs += ["-warn"]
    ssjb.call(baseArgs + args)

def deployJarToLocalMavenRepo(pathLocalRepo, pathJar, artifact, deps=None):
    with TempDir() as dirTemp:
        
        # write the pom file
        pathPom = os.path.join(dirTemp, "artifact.pom")
        with open(pathPom, "w") as file:
            file.write(_getPomXml(artifact, deps))

        ssjb.call(["mvn", "install:install-file",
            "-DlocalRepositoryPath=%s" % pathLocalRepo,
            "-Dfile=%s" % pathJar,
            "-DpomFile=%s" % pathPom
        ])
    print ("Deployed Maven artifact %s to %s" % (artifact, pathLocalRepo))

def _getPomXml(artifact, deps=None):

    def setProp(elem, name, val):
        propElem = ET.SubElement(elem, name)
        propElem.text = val

    def addDep(elem, dep):
        depElem = ET.SubElement(elem, "dependency")
        setProp(depElem, "groupId", dep.groupId)
        setProp(depElem, "artifactId", dep.artifactId)
        setProp(depElem, "version", dep.version)
    
    rootElem = ET.Element("project")
    setProp(rootElem, "groupId", artifact.groupId)
    setProp(rootElem, "artifactId", artifact.artifactId)
    setProp(rootElem, "version", artifact.version)
    setProp(rootElem, "packaging", "jar")
    if deps is not None:
        depsElem = ET.SubElement(rootElem, "dependencies")
        for dep in deps:
            addDep(depsElem, dep)

    return _prettyPrintXml(rootElem)

def evictDep(dep, extraRepos=None):
    for pathJar in getJarPaths([dep], extraRepos):
        dirArtifact = os.path.dirname(os.path.dirname(pathJar))
        if os.path.basename(dirArtifact) == dep.artifactId:
            ssjb.file.delete(dirArtifact)
            print ("Deleted %s" % dirArtifact)

