#!/bin/python
###
## Terminalia - tui game engine
## Made just 4 fun
## by gl1d3r1ng
###

import mathfuns
#import curser
import script
import level
import blessed # install via pip or repos

### Lib vars
version = "v0.0.0"

flags = {}

blueprints = {} ## for fast object making
container = {} ## vault with levels,...
currentlevel = None
actions = {"player": 0}

camera = [0,0]
xviewsize = 6
yviewsize = 4
log = []
term = blessed.Terminal()


### Funcs
## Initializing, loading, ...
def init(containerfile="container.jsonc", blueprintsfile="blueprints.jsonc"):
    global container
    global blueprints
    global flags
    blueprints = level.loadfile(blueprintsfile)
    container = level.loadfile(containerfile)
    flags = container["flags"]

    for lev in container["levels"]:
        objs = container["levels"][lev]["objects"]
        for object in objs:
            objs[object] = objs[object] | blueprints[objs[object]["bp"]] ## unite object with its blueprint
            objs[object].pop("bp")
            #print(objs[object])
        del objs

    loadlevel(container["initialLevel"])

def loadlevel(id: str):
    global currentlevel
    global container
    if id in container["levels"]:
        currentlevel = id

## Scripting
def sexec(cmd: list) -> None:
    cmdl = len(cmd)
    if cmdl != 0:
        index = 0
        while index != cmdl :
            com = cmd[index]
            match com[0]:
                case "set_flag":
                    flags[com[1]] = com[2]
                case "exit":
                    break
            index += 1

## 
def check_zones() -> None:
    ...

def shift_object(id: str, x, y, ignor_coll = False):
    objs = container["levels"][currentlevel]["objects"]
    object = objs[id]
    for obj in objs:
        if obj != id:
            if object["x"] + x == objs[obj]["x"] and object["y"] + y == objs[obj]["y"]:
                if not(ignor_coll) and objs[obj]["coll"]:
                    break
    else:
        object["x"] += x
        object["y"] += y

## UI
def updatesc():
    #buf = [["."] * (viewsize * 2 + 1)] * (viewsize * 2 + 1)
    ## create buffer
    buf = [["."]*(xviewsize * 2 + 1) for _ in range(yviewsize * 2 + 1)]
    objs = container["levels"][currentlevel]["objects"] # make this as cache

    ## add objects to buffer
    for obj in objs:
        object = objs[obj]
        #print(objs[object])
        if mathfuns.inSquare(object["x"], object["y"], camera[0] - xviewsize,\
                             camera[1] - yviewsize, xviewsize * 2, yviewsize * 2):
            buf[-object["y"] + yviewsize - camera[1]][object["x"] + xviewsize - camera[0]] = object["icon"]

    ## darkness
    if flags["darkness"] >= 0:
        ...

    ## print byffer
    buf1 = ""
    for y in buf:
        for x in y:
            buf1 += "".join(x)
        buf1 += "\n"
    print(term.home + term.clear + buf1)
    #print(container["levels"][currentlevel]["objects"]["player"]["x"], \
    #      container["levels"][currentlevel]["objects"]["player"]["y"])

def useract():
    shift = [0,0]
    with term.cbreak(), term.hidden_cursor():
        inp = term.inkey()
        if inp.is_sequence: 
            inp = repr(inp)

    #print(inp)
    match inp:
        case "h": shift = [-1, 0]
        case "j": shift = [0, -1]
        case "k": shift = [0, 1]
        case "l": shift = [1, 0]
        case "b": shift = [-1, -1]
        case "n": shift = [1, -1]
        case "y": shift = [-1, 1]
        case "u": shift = [1, 1]
        case "q": exit()
        case _: ...

    if shift != [0, 0]:
        shift_object("player", shift[0], shift[1])
        actions["player"] = 100

    if flags["movecamera"]:
    #camera[]
        ...

### Main code ###
init()
#print(container, currentlevel)
while 1:
    updatesc()
    if actions["player"] <= 0:
        useract()
    for action in actions:
        actions[action] -= 1
