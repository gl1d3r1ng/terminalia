#!/bin/python
###
## Terminalia - tui game engine
## Made just 4 fun; Expect a lot of crutches
## by gl1d3r1ng
###

import re
import mathfuns
#import curser
import level
import blessed # install via pip or repos

### Lib vars
version = "v0.0.1.22"

##
mode = ""

## debug
c = 0

## flags
gflags = {}
flags = {}

## vaults
blueprints = {} ## for fast object making
container = {} ## vault with levels,...
currentlevel = None
actions = {"player": 0}
scripts = {}
items = {}
objects = {}
achievments = {} ## To be added...

## grafic
fps = 60
camera = {"x": 0, "y": 0}
xviewsize = 0
yviewsize = 0
log = []
log_limit = 100
term = blessed.Terminal()
lights = {}
color_switchers = {}

## cache
player_coords = {"x": 0, "y": 0}
player = ...
protobuf = {}

pads = {\
        "map": {"brcolor": None, "disable": False, "border": False, "xorg": "0", "yorg": "0", "worg": "20", "horg": "20", "xpadding": 0, "ypadding": 0, "xcut": False, "scroll": 0, "text": ""}, \
        "log": {"brcolor": None, "disable": False, "border": True, "xorg": "0", "yorg": "term.height // 2", "worg": "term.width", "horg": "term.height // 2", "xpadding": 0, "ypadding": 0, "xcut": False, "scroll": 0, "text": ""}, \
        "items": {"brcolor": None, "disable": True, "border": True, "xorg": "term.width // 4", "yorg": "term.height // 4", "worg": "term.width // 2", "horg": "term.height // 2", "xpadding": 1, "ypadding": 1, "xcut": True, "scroll": 0, "text": ""}, \
        "msg": {"brcolor": None, "disable": True, "border": True, "xorg": "term.width // 6", "yorg": "term.height // 3", "worg": "term.width // 2", "horg": "term.height // 2", "xpadding": 2, "ypadding": 2, "xcut": True, "scroll": 0, "text": ""}, \
        "flags": {"brcolor": "purple", "disable": True, "border": True, "xorg": "term.width // 2", "yorg": "2", "worg": "term.width // 2", "horg": "term.height // 2", "xpadding": 1, "ypadding": 1, "xcut": False, "scroll": 0, "text": ""} }


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
    load_level(gflags["currentlevel"])

def load_level(id: str):
    global currentlevel, container, flags, objects, scripts, xviewsize, yviewsize, player
    if level_exist(id):
        currentlevel = id
        flags = container["levels"][currentlevel]["flags"]
        objects = container["levels"][currentlevel]["objects"]
        scripts = container["levels"][currentlevel]["scripts"]
        update_player_coords()
        xviewsize = flags["viewsize"]["x"]
        yviewsize = flags["viewsize"]["y"]
        player = objects["player"]
    
def level_exist(id: str) -> bool:
    if id in container["levels"]:
        return True
    return False

def flag_exist(flag: str, level = None) -> bool:
    if flag in flags:
        return True
    return False

def set_flag(flag: str, value: str, level = None):
    if level == None:
        flags[flag] = value
    elif level_exist(level):
        container["levels"][level][flags] = value

def read_flag(flag, level: str | None = None):
    if level == None:
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
        for param, value in params.items():
            objects[param] = value

def rem_object(id: str) -> None:
    if id in objects:
        del objects[id]

def mod_object(id: str, params: dict = {}) -> None:
    if id in objects:
        object = objects[id]
        for param, value in params.items():
            object[param] = value

def object_prop(id: str, prop: str):
    if object_exist(id):
        if prop in objects[id]:
            return objects[id][prop]

def object_exist(id: str) -> bool:
    if id in objects:
        return True
    return False

## Items
def add_item(id: str, bp: str, owner: str | None, x: int | None = None, y: int | None = None):
    ...

def rem_item(id: str) -> None:
    if id in items:
        del items[id]

def use_item(id: str) -> None:
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

def render_pad(padname: str) -> None:
    global protobuf, add2protobuf, pads
    pad = pads[padname]
    if not pad["disable"]:
        add2protobuf = lambda x, y, char, precolor, postcolor: protobuf.update({(pad['x'] + x, pad['y'] + y): {"char": char, "precolor": precolor, "postcolor": postcolor}})
        text = pad["text"]
        xcut = pad["xcut"]

        pattern = r'\\\[.*?]'
        matches = set(re.findall(pattern, text))
        for mat in matches:
            text = text.replace(mat, getattr(term, mat[1:-1]))
        #text = text.replace("\\[", "[")
        # print(text); exit()

        brcolor = ""; rescolor = ""
        if pad["brcolor"] != None:
            brcolor = getattr(term, pad["brcolor"])
            rescolor = term.normal

        if pad["border"]:
            add2protobuf(0, 0, "┏", brcolor, "")
            add2protobuf(pad["width"] - 1, 0, "┓", "", rescolor)
            add2protobuf(0, pad["height"] - 1, "┗", brcolor, "")
            add2protobuf(pad["width"] - 1, pad["height"] - 1, "┛", "" , rescolor)
            for x in range(1, pad["width"] - 1):
                add2protobuf(x, 0, "━", "", "")
            for y in range(1, pad["height"] - 1):
                add2protobuf(0, y, "┃", brcolor, rescolor)
                add2protobuf(pad["width"] - 1, y, "┃", term.normal + brcolor, rescolor)
            for x in range(1, pad["width"] - 1):
                add2protobuf(x, pad["height"] - 1, "━", "", "")

        for y in range(pad["border"], pad["height"] - pad["border"]):
            for x in range(pad["border"], pad["width"] - pad["border"]):
                add2protobuf(x, y, " ", "", "")

        y = int(pad["border"])
        precolor = ""
        postcolor = ""
        harverst = ""
        reset_x = pad["border"] + pad["xpadding"] # bool + int = int
        max_x = pad["width"] - 2 * pad["border"] - pad["xpadding"] * 2 + 1
        max_y = pad["height"] - 1 * pad["border"] - pad["ypadding"] * 1
        x = reset_x
        page = 0

        y = pad["border"] + pad["ypadding"]
        for sym in text:
            #sym = text[index]
            if harverst != "":
                harverst += sym
                if sym == "m":
                    precolor += harverst
                    harverst = ""
            else:
                if sym == "\n":
                    if page >= pad["scroll"]:
                        y += 1
                    else:
                        page += 1

                    if y >= max_y:
                        break

                    x = reset_x

                elif ord(sym) == 27:
                    harverst += sym

                else:
                    if x >= max_x:
                        if xcut:
                            if x == max_x:
                                if page >= pad["scroll"]:
                                    add2protobuf(x - 1, y, ">", term.reverse, term.normal)
                                x += 1
                        else:
                            if page >= pad["scroll"]:
                               y += 1
                            else:
                                page += 1
                            if y >= max_y:
                                break
                            x = reset_x
                            if page >= pad["scroll"]:
                                add2protobuf(x, y, sym, precolor, postcolor)
                            if precolor != "":
                                precolor = ""
                            x += 1
                    else:
                        if page >= pad["scroll"]:
                            add2protobuf(x, y, sym, precolor, postcolor)
                        if precolor == term.normal:
                            precolor = ""
                        x += 1

 
def update_sizes(init=False, all=False, padname=""):
    if all:
        for pad in pads:
            update_pads_sizes(pad, init)
    else:
        update_pads_sizes(padname, init)

def update_pads_sizes(padname: str, init):
    pad = pads[padname]
    if init:
        pad["x"] = eval(pad["xorg"])
        pad["xs"] = 0
        pad["y"] = eval(pad["yorg"])
        pad["ys"] = 0
        pad["width"] = eval(pad["worg"])
        pad["ws"] = 0
        pad["height"] = eval(pad["horg"])
        pad["hs"] = 0
    else:
        pad["x"] = eval(pad["xorg"] + "+" + str(pad["xs"]))
        pad["y"] = eval(pad["yorg"] + "+" + str(pad["ys"]))
        pad["width"] = eval(pad["worg"] + "+" + str(pad["ws"]))
        pad["height"] = eval(pad["horg"] + "+" + str(pad["hs"]))


def update_map() -> str:
    ## create buffer
    global lightbuf
    object_item_buf = {}
    visible_objects_items = []
    lightbuf = [{"shape": flags["darkness"]["shape"], "x": camera["x"], "y": camera["y"], "radius": flags["darkness"]["radius"], "tags": ["camera"]}]
    buf = ""

    ## add objects to buffer
    for obj in objects:
        object = objects[obj]
        #print(objs[object])
        if mathfuns.in_square(object["x"], object["y"], camera["x"] - xviewsize,\
                             camera["y"] - yviewsize, xviewsize * 2, yviewsize * 2):
            object_item_buf[(object["x"], object["y"])] = {"id": obj, "color": "", "type": ""}

    for item_name in items:
        item = items[item_name]
        #print(objs[object])
        if item["owner"] == None:
            if mathfuns.in_square(item["x"], item["y"], camera["x"] - xviewsize,\
                             camera["y"] - yviewsize, xviewsize * 2, yviewsize * 2):
                object_item_buf[(item["x"], item["y"])] = {"id": item_name, "color": "", "type": item}

    for y in range(camera["y"] + yviewsize, camera["y"] - yviewsize - 1, -1):
        for x in range(camera["x"] - xviewsize, camera["x"] + xviewsize + 1):
            if indarkness(x, y):
                icon = " "
            else:
                if (x, y) in object_item_buf:
                    icon = color_compile(objects[object_item_buf[(x,y)]["id"]]["icon"])
                else:
                    icon = "." ## emptyness
            buf += icon
        buf += "\n"

    return "".join(buf)
    #sprint(term.home + term.clear + "".join(buf) + "\n")

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

def update_log_pad():
    loglen = len(log)
    text = ""
    if loglen <= log_limit:
        for msg in log:
            text += msg + "\n"
    else:
        for msg in log[loglen - log_limit::]:
            text += msg + "\n"

    return text

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
    if len(log) < log_limit:
        log.pop(0)
    pads["log"]["text"] = update_log_pad()

def debug_file_update(msg):
    with open("debug.log", "a") as dfile:
        dfile.write("".join(msg) + "\n")

## scripts
Caller = ""
exec_globals = {"__builtins__":{
    "sprint": sprint,
    "c": c,
    "set_flag": set_flag,
    "read_flag": read_flag,
    "set_gflag": set_gflag,
    "log_update": log_update,
    "add_object": add_object,
    "object_exist": object_exist,
    "object_prop": object_prop,
    "rem_object": rem_object,
    "caller": Caller
}}

def script_exec(id:str, caller: str = "", code: str = "") -> None:
    global Caller
    if caller != "":
        if caller in objects:
            Caller = objects[caller]
        elif caller in items:
            Caller = items[caller]
        else:
            log_update(f"ERR:: {caller} not found")

    if id != None:
        code = scripts[id]["code"]
    exec(code, exec_globals)
    Caller = ""

def script_autorun():
    ...

def actions_update():
    for action in actions:
        actions[action] -= 1

def update() -> None:
    global protobuf,pads

    pads["map"]["text"] = update_map()
    if not pads["flags"]["disable"]:
        pads["flags"]["text"] = str(flags)

    buf = ""

    for pad in pads:
        render_pad(pad)

    # print(protobuf); exit()
    for y in range(term.height):
        for x in range(term.width):
            if (x, y) in protobuf:
                item = protobuf[(x, y)]
                buf += item["precolor"] + item["char"] + item["postcolor"]
            else:
                buf += " "
        if y != term.height:
            buf += "\n"
    protobuf = {}

    sprint(term.clear + term.home)
    sprint(buf)

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
        case "f": pads["flags"]["disable"] = pads["flags"]["disable"] * -1 + 1
        case _: ...

    if actions["player"] <= 0:
        if shift != [0, 0]:
            shift_object("player", shift[0], shift[1])
            update_player_coords()
            actions["player"] = 1

    if flags["movecamera"]:
        camera["x"] = player_coords["x"]
        camera["y"] = player_coords["y"]
        

### Main code ###
init()
update_sizes(True, True)
with term.fullscreen():
    while 1:
        update()
        kbread()
        if actions["player"] > 0:
            actions_update()
