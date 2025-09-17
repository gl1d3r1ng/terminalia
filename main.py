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
version = "v0.0.1.2"

gflags = {}
flags = {}

blueprints = {} ## for fast object making
container = {} ## vault with levels,...
currentlevel = None
actions = {"player": 0}
checkers = {}
scripts = {}

fps = 60
camera = {"x": 0, "y": 0}
xviewsize = 0
yviewsize = 0
log = []
log_view_limit = 10
term = blessed.Terminal()
light = {}
color_switchers = {}

## cache
objects = {} # container["levels"][currentlevel]["objects"]
player_coords = {"x": 0, "y": 0}

### Funcs
## Initializing, loading, ...
def init(containerfile="container.jsonc", blueprintsfile="blueprints.jsonc"):
    global container, blueprints, gflags
    blueprints = level.loadfile(blueprintsfile)
    container = level.loadfile(containerfile)
    gflags = container["gflags"]

    for lev in container["levels"]:
        objs = container["levels"][lev]["objects"]
        for object in objs:
            objs[object] = blueprints[objs[object]["bp"]] | objs[object] ## unite object with its blueprint
            objs[object].pop("bp")
            #print(objs[object])

        checkers = container["levels"][lev]["checkers"]
        for checker in checkers:
            if not "on" in checkers[checker]:
                checkers[checker]["on"] = True
    # del objs
    load_level(container["initialLevel"])

def load_level(id: str):
    global currentlevel, container, flags, objects, checkers, scripts, xviewsize, yviewsize
    if id in container["levels"]:
        currentlevel = id
        flags = container["levels"][currentlevel]["flags"]
        objects = container["levels"][currentlevel]["objects"]
        checkers = container["levels"][currentlevel]["checkers"]
        scripts = container["levels"][currentlevel]["scripts"]
        update_player_coords()
        xviewsize = flags["viewsize"]["x"]
        yviewsize = flags["viewsize"]["y"]
        

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
def script_exec(cmd: list, id = None) -> None:
    if id != None:
        cmd = scripts[id]

    commands = ["set_gflag", "log_update"]
    cmdl = len(cmd)
    vars = {}
    points = {} ## TBC...
    if cmdl != 0:
        index = 0
        for com in cmd:
            if len(com[0]) > 1 and com[0][0] == ":":
            #print(com)
                ...
        while index < cmdl:
            com = cmd[index]
            if com[0] in commands:
                globals()[com[0]](*com[1:])
            else:
                match com[0]:
                    case "var":
                        vars[com[1]] = com[2]
                    case "goto":
                        index = com[1] - 1
                    case "if":
                        ...
                    case "ifgo":
                        ...
                    case "set_flag":
                        set_flag(com[1], com[2], "<NONE>" if len(com) == 2 else com[3])
                    case "pass":
                        pass
                    case "exit":
                        break
            index += 1

## Checkes
def add_checker():
    ...

def switch_checker(checker: str):
    if checker in checkers:
        Checker = checkers[checker]
        match Checker["on"]:
            case True: Checker["on"] = False
            case False: Checker["on"] = True

def check_checkers() -> None:
    for checker in checkers:
        if checkers[checker]["on"]:
            #debug_file_update(checker)
            Checker = checkers[checker]
            ready_conds = 0
            for condition in Checker["conditions"]:
                match condition[0]:
                    case "flag":
                        if condition[1] in flags:
                            if flags[condition[1]] == condition[2]:
                                ready_conds += 1
                    case "in_square":
                        ...
                        
            if ready_conds == len(Checker["conditions"]):
                script_exec([], Checker["script"])
                if Checker["disable"]:
                    switch_checker(checker)
                #log_update("Exected "+checker)

## Objects
def add_object():
    ...

def rem_object():
    ...

def mod_object():
    ...

## Items
def add_item():
    ...

def rem_item():
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
                    icon = color_compile(objects[objbuf[(x,y)]["id"]]["icon"])
                else:
                    icon = "." ## emptyness
            buf += icon
        buf += "\n"

    print(term.home + term.clear + "".join(buf))

    ## Logs
    loglen = len(log)
    print(term.move_xy(0, term.height - (loglen if loglen <= log_view_limit else log_view_limit) - 2))
    for msg in log[(loglen - log_view_limit) if loglen > log_view_limit else  None:]:
        print(msg)

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
        case "s": set_flag("flag0", "yess")
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

### Main code ###
init()
#print(container, currentlevel)
with term.fullscreen():
    while 1:
        updatesc()
        kbread()
        check_checkers()
        if actions["player"] > 0:
            for action in actions:
                actions[action] -= 1
