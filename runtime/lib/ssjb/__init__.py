
# stupidly simple jar builder
# Jeff Martin
# copyright 2015
# license: GPL v3

import sys
import os
import subprocess


# setup tasks
tasks = {}

def registerTask(name, func):
    tasks[name] = func

def run():

    # get the task name
    taskName = "main"
    if len(sys.argv) > 1:
        taskName = sys.argv[1]
    
    # find that task
    try:
        task = tasks[taskName]
    except:
        print ("Couldn't find task: %s" % taskName)
        return

    # run it!
    print ("Running task: %s" % taskName)
    task()


# set up the default main task
def mainTask():
    print ("The main task doesn't do anything by default")

# set up the default tasks task
def tasksTask():
    print ("Listing all registered tasks.")
    print ("Name :  Description")
    for x in tasks.keys():
        if tasks[x].__doc__ is not None:
            print (x + " : " + tasks[x].__doc__)
        else:
            print (x + " : No description provided")
    print ("Finished reporting available tasks")


#register default main task
registerTask("main", mainTask)

#register default tasks task
registerTask("tasks", tasksTask)

# global vars
JvmBitness = None
ClasspathSeparator = ";" if sys.platform == "win32" else ":"

# library of useful functions

def call(args):
    result = subprocess.call(args)
    if result != 0:
        raise Exception("call command failed with code %d" % result)

def callJava(classpath, className, javaArgs):
    if isinstance(classpath, list):
        classpath = ClasspathSeparator.join(classpath)
    call(["java", "-cp", classpath, className] + javaArgs)

def callJavaJar(jar, javaArgs):
    call(["java", "-jar", jar] + javaArgs)

def getJvmBitness():
    global JvmBitness
    if JvmBitness is None:
        with open(os.devnull, "w") as devnull:
            result = subprocess.call(["java", "-version", "-d64"], stdout=devnull, stderr=devnull)
            JvmBitness = 64 if result == 0 else 32
    return JvmBitness

