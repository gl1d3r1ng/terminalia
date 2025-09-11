#!/bin/python
###
## Terminalia - tui game engine
## Made just 4 fun
## by gl1d3r1ng
###

import mathfuns
#import curser
import level
import blessed # install via pip or repos

### Lib vars
version = "v0.0.1.1"

gflags = {}
flags = {}

blueprints = {} ## for fast object making
container = {} ## vault with levels,...
currentlevel = None
actions = {"player": 0}

camera = {"x": 0, "y": 0}
xviewsize = 0
yviewsize = 0
log = []
term = blessed.Terminal()
light = {}

## cache
objects = {} # container["levels"][currentlevel]["objects"]
player_coords = {"x": 0, "y": 0}

### Funcs
## Initializing, loading, ...
def init(containerfile="container.jsonc", blueprintsfile="blueprints.jsonc"):
    global container, blueprints, gflags, objects, xviewsize, yviewsize
    blueprints = level.loadfile(blueprintsfile)
    container = level.loadfile(containerfile)
    gflags = container["gflags"]

    for lev in container["levels"]:
        objs = container["levels"][lev]["objects"]
        for object in objs:
            objs[object] = blueprints[objs[object]["bp"]] | objs[object] ## unite object with its blueprint
            objs[object].pop("bp")
            #print(objs[object])
    # del objs

    load_level(container["initialLevel"])
    objects = container["levels"][currentlevel]["objects"]
    update_player_coords()
    xviewsize = flags["viewsize"]["x"]
    yviewsize = flags["viewsize"]["y"]

def load_level(id: str):
    global currentlevel, container, flags
    if id in container["levels"]:
        currentlevel = id
        flags = container["levels"][currentlevel]["flags"]

def set_flag(flag: str, value: str, level = "<NONE>"):
    if level == "<NONE>":
        flags[flag] = value
    elif level in container["levels"]:
        container["levels"][level][flags] = value

def set_gflag(flag: str, value: str):
    gflags[flag] = value

## Cache
def update_player_coords() -> None:
    player_coords["x"] = objects["player"]["x"]
    player_coords["y"] = objects["player"]["y"]

## Scripting
def script_exec(cmd: list) -> None:
    cmdl = len(cmd)
    if cmdl != 0:
        index = 0
        while index != cmdl:
            com = cmd[index]
            match com[0]:
                case "set_flag":
                    set_flag(com[1], com[2], "<NONE>" if len(com) == 2 else com[3])
                case "exit":
                    break
            index += 1

## 
def check_zones() -> None:
    ...

def shift_object(id: str, x, y, ignor_coll = False):
    object = objects[id]
    for obj in objects:
        if obj != id:
            if object["x"] + x == objects[obj]["x"] and object["y"] + y == objects[obj]["y"]:
                if not(ignor_coll) and objects[obj]["coll"]:
                    break
    else:
        object["x"] += x
        object["y"] += y

## UI
def updatesc():
    ## create buffer
    global lightbuf
    objbuf = {}
    lightbuf = [{"shape": flags["darkness"]["shape"], "x": camera["x"], "y": camera["y"], "radius": flags["darkness"]["radius"], "tags": ["camera"]}]
    buf = "" #[""]*(yviewsize * 2 + 1)

    ## add objects to buffer
    for obj in objects:
        object = objects[obj]
        #print(objs[object])
        if mathfuns.in_square(object["x"], object["y"], camera["x"] - xviewsize,\
                             camera["y"] - yviewsize, xviewsize * 2, yviewsize * 2):
            objbuf[(object["x"], object["y"])] = {"id": obj}

    for y in range(camera["y"] + yviewsize, camera["y"] - yviewsize - 1, -1):
        for x in range(camera["x"] - xviewsize, camera["x"] + xviewsize + 1):
            if indarkness(x, y):
                icon = " "
            else:
                if (x, y) in objbuf:
                    icon = objects[objbuf[(x,y)]["id"]]["icon"]
                else:
                    # buf += "."
                    icon = "."
            buf += icon
        buf += "\n"

    print(term.home + term.clear + "".join(buf))

def indarkness(x, y):
    for source in lightbuf:
        match source["shape"]:
            case "circle":
                if mathfuns.in_circle(x, y, source["x"], source["y"], source["radius"]):
                    return 0

            case "square":
                if "camera" in source["tags"]:
                    xdist = flags["darkness"]["xdist"]
                    ydist = flags["darkness"]["ydist"]
                    if mathfuns.in_square(x, y, \
                            camera["x"] - xdist, camera["y"] - ydist, xdist * 2, ydist * 2):
                        return 0
                else:
                    if mathfuns.in_square(x, y, source["x"], source["y"], source["xlen"], source["ylen"]):
                        return 1
    return 1

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
        update_player_coords()
        actions["player"] = 100

    if flags["movecamera"]:
        camera["x"] = player_coords["x"]
        camera["y"] = player_coords["y"]
        

### Main code ###
init()
#print(container, currentlevel)
while 1:
    updatesc()
    if actions["player"] <= 0:
        useract()
    for action in actions:
        actions[action] -= 1
