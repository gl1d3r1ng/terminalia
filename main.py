#!/bin/python
###
## Terminalia - tui game engine
## Made just 4 fun
## by gl1d3r1ng
###

import re
import mathfuns
#import curser
import level
import blessed # install via pip or repos

### Lib vars
version = "v0.0.1.22"

## flags
gflags = {}
flags = {}

##
blueprints = {} ## for fast object making
container = {} ## vault with levels,...
currentlevel = None
actions = {"player": 0}
scripts = {}
items = {}
objects = {}

## grafic
fps = 60
camera = {"x": 0, "y": 0}
xviewsize = 0
yviewsize = 0
log = []
log_view_limit = 10
term = blessed.Terminal()
lights = {}
color_switchers = {}

## cache
player_coords = {"x": 0, "y": 0}

### Funcs
## Initializing, loading, ...
def init(containerfile="container.jsonc", blueprintsfile="blueprints.jsonc"):
    global container, blueprints, gflags, object_bps, items_bps
    blueprints = level.loadfile(blueprintsfile)
    object_bps = blueprints["objects"]
    items_bps = blueprints["items"]
    container = level.loadfile(containerfile)
    gflags = container["gflags"]

    for lev in container["levels"]:
        objs = container["levels"][lev]["objects"]
        for object in objs:
            objs[object] = object_bps[objs[object]["bp"]] | objs[object] ## unite object with its blueprint
            objs[object].pop("bp")

    for lev in container["levels"]:
        itms = container["levels"][lev]["items"]
        for item in itms:
            itms[item] = items_bps[itms[item]["bp"]] | itms[item] ## unite item with its blueprint
            itms[item].pop("bp")
            #print(objs[item])
    load_level(container["initialLevel"])

def load_level(id: str):
    global currentlevel, container, flags, objects, scripts, xviewsize, yviewsize
    if id in container["levels"]:
        currentlevel = id
        flags = container["levels"][currentlevel]["flags"]
        objects = container["levels"][currentlevel]["objects"]
        scripts = container["levels"][currentlevel]["scripts"]
        update_player_coords()
        xviewsize = flags["viewsize"]["x"]
        yviewsize = flags["viewsize"]["y"]
        

def set_flag(flag: str, value: str, level = "<NONE>"):
    if level == "<NONE>":
        flags[flag] = value
    elif level in container["levels"]:
        container["levels"][level][flags] = value

def read_flag(flag, level = "<NONE>"):
    if level == "<NONE>":
        return flags[flag]
    elif level in container["levels"]:
        return container["levels"][level]["flags"][flag]

def set_gflag(flag: str, value: str):
    gflags[flag] = value

def read_gflag(flag: str):
    return gflags[flag]

## Objects
def add_object(id: str, bp, x: int = 0, y: int = 0, params: dict = {}) -> None:
    if id not in objects:
        objects[id] = {}
        if bp != None:
            objects[id] = objects[id] | blueprints[bp]
        objects["x"] = x
        objects["y"] = y
        for k, v in params.items():
            objects[k] = v

def rem_object(id: str) -> None:
    if id in objects:
        del objects[id]

def mod_object():
    ...

def object_prop(id: str, prop: str):
    if object_exist(id):
        if prop in objects[id]:
            return objects[id][prop]

def object_exist(id: str) -> bool:
    if id in objects:
        return True
    return False

## Items
def add_item():
    ...

def rem_item():
    ...

def use_item():
    ...

## Cache
def update_player_coords() -> None:
    player_coords["x"] = objects["player"]["x"]
    player_coords["y"] = objects["player"]["y"]

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
def sprint(text, end:str  = ""):
    print(text, end=end)

buf = {}
def updatemap():
    ...

def updatesc():
    ## create buffer
    global lightbuf
    objbuf = {}
    lightbuf = [{"shape": flags["darkness"]["shape"], "x": camera["x"], "y": camera["y"], "radius": flags["darkness"]["radius"], "tags": ["camera"]}]
    buf = ""

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
                    icon = color_compile(objects[objbuf[(x,y)]["id"]]["icon"])
                else:
                    icon = "." ## emptyness
            buf += icon
        buf += "\n"

    sprint(term.home + term.clear + "".join(buf) + "\n")

    ## Logs
    loglen = len(log)
    sprint(term.move_xy(0, term.height - (loglen if loglen <= log_view_limit else log_view_limit) - 1))
    for msg in log[(loglen - log_view_limit) if loglen > log_view_limit else  None:]:
        sprint(msg+ "\n")

    # print(term.move_xy(xviewsize * 2 + 3, 0), flags)

    # time.sleep(1/fps)

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

def color_compile(msg: str, normal_end = True) -> str:
    ## Changes [color] to ansi color; changes \[ to [, \] to ]
    matches = re.findall(r"(?<!\\)\[.*?]", msg)
    for Match in matches:
        if Match == "[0]":
            replacing = term.normal
        else:
            replacing = f"{getattr(term, Match[1:-1])}"
        msg = msg.replace(Match, replacing)
    msg = msg.replace(r"\[", "[").replace(r"\]", "]")
    if normal_end:
        msg += term.normal
    return msg

def log_update(msg: str) -> None:
    log.append(msg)

def kbread():
    shift = [0,0]
    with term.cbreak(), term.hidden_cursor():
        inp = term.inkey(timeout=1/fps)
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
        case "m": log_update(color_compile("M was [red]pressed[0]!"))
        case "s": script_exec("script0")
        case "q": exit()
        case _: ...

    if actions["player"] <= 0:
        if shift != [0, 0]:
            shift_object("player", shift[0], shift[1])
            update_player_coords()
            actions["player"] = 1

    if flags["movecamera"]:
        camera["x"] = player_coords["x"]
        camera["y"] = player_coords["y"]
        
def debug_file_update(msg):
    with open("debug.log", "a") as dfile:
        dfile.write("".join(msg) + "\n")

## scripts
sglobals = {"__builtins__":{
    "print": print,
    "log_update": log_update,
    "add_object": add_object,
    "object_exist": object_exist,
    "object_prop": object_prop,
    "rem_object": rem_object
}}

def script_exec(id:str, code: str = "") -> None:
    if id != None:
        code = scripts[id]["code"]
    exec(code, sglobals)

def script_autorun():
    ...
### Main code ###
init()
with term.fullscreen():
    while 1:
        updatesc()
        kbread()
        if actions["player"] > 0:
            for action in actions:
                actions[action] -= 1
