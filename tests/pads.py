import blessed
import re

term = blessed.Terminal()
fps = 60

msg = "I\'m just a text for [green]terminalia[normal] pads demo\n\\[nothing] special\n[red]my author is a crutchmaker[normal]\n[yellow]h/l[normal] to resize my [purple]width[normal]\n[yellow]j/k[normal] to resize my [purple]height[normal]\n[yellow]H/J/K/L[normal] to shift [blue]me[normal]\n[yellow]i[normal] to toogle xcut [blue]mode[normal]"
pads = {"maintext": {"brcolor": None, "disable": False, "border": True, "xorg": "2", "yorg": "4", "worg": "30", "horg": "10", "padding": 0, "xcut": True, "scroll": 1, "buf": msg},\
        "coords": {"brcolor": "purple", "disable": False, "border": True, "xorg": "term.width // 2", "yorg": "term.height // 2", "worg": "10", "horg": "6", "padding": 0, "xcut": False, "scroll": 0, "buf": ""},\
        "term": {"brcolor": "yellow", "disable": False, "border": True, "xorg": "term.width // 2", "yorg": "term.height // 2 - 8", "worg": "10", "horg": "4", "padding": 0, "xcut": False, "scroll": 0, "buf": ""}\
        }

def sprint(text, end=""):
    print(text, end=end)

def render() -> None:
    global pads
    add2protobuf  = lambda x, y, char: protobuf.update({(pad['x'] + x, pad['y'] + y): char})

    pads["coords"]["buf"] = f"[purple]Textarea[normal]\n[blue]x[normal]: {pads['maintext']['x']}\n[blue]y[normal]: {pads['maintext']['y']}\n[blue]w[normal]: {pads['maintext']['width']}\n[blue]h[normal]: {pads['maintext']['height']}"
    pads["term"]["buf"] = f"[black_on_yellow]Terminal[normal]\n[green]w[normal]: {term.width}\n[green]h[normal]: {term.height}"
    buf = ""
    protobuf = {}

    for _, pad in pads.items():
        brcolor = ""; rescolor = ""
        if pad["brcolor"] != None:
            brcolor = getattr(term, pad["brcolor"])
            rescolor = term.normal

        if pad["border"]:
            add2protobuf(-1 - pad["padding"], -1 - pad["padding"], brcolor + "┏")
            add2protobuf(pad["width"] + pad["padding"], -1 - pad["padding"], "┓" + rescolor)
            add2protobuf(-1 - pad["padding"], pad["height"] + pad["padding"], brcolor + "┗")
            add2protobuf(pad["width"] + pad["padding"], pad["height"] + pad["padding"], "┛" + rescolor)
            for x in range(0 - pad["padding"], pad["width"] + pad["padding"]):
                add2protobuf(x, -1 - pad["padding"], "━")
            for y in range(0 - pad["padding"], pad["height"] + pad["padding"]):
                add2protobuf(-1 - pad["padding"], y, brcolor + "┃" + rescolor)
                add2protobuf(pad["width"] + pad["padding"], y, brcolor + "┃" + rescolor)
            for x in range(0 - pad["padding"], pad["width"] + pad["padding"]):
                add2protobuf(x, pad["height"] + pad["padding"], "━")

        colors = {}
        text = pad["buf"]
        #print(text)
        pattern = r'((?<!\\)\[.*?])|((?<=\x1B).+?m)'
        text = text.replace("\\[", "\0")
        matches = [[match.group(), match.start()] for match in re.finditer(pattern, text)]

        pos_shift = 0

        for i in range(len(matches)):
            matches[i][1] -= pos_shift
            pos_shift += len(matches[i][0])

        for match in matches:
            if match[0][-1] == "]":
                colors[match[1]] = getattr(term, match[0][1:-1])
            else:
                colors[match[1]] = "\x1b" + match[0]
            text = text.replace(match[0], "", 1)
        text = text.replace("\0", "[")
        # print(colors, text)

        #a = "\n" if not pad["xcut"] else ""
        strings = [string + "\n" for string in text.split("\n")]
        
        if pad["xcut"]:
            y = 0
            pos = 0
            color = ""
            for string in strings:
                #print(string)
                x = 0
                for sym in string:
                    if pos in colors:
                        color = colors[pos]
                    tmp = False

                    if sym == "\n":
                        sym = term.normal + " "
                    elif x + 1 == pad["width"]:
                        sym = term.reverse + ">" + term.normal
                        tmp = True
                    else:
                        sym = color + sym
                    
                    add2protobuf(x, y, sym)
                    x += 1
                    pos += 1

                    if color == term.normal:
                        color = ""

                    if tmp:
                        #pos += len(string) -x# -1
                        for i in range(len(string) - x):
                            pos += 1
                            if pos in colors:
                                color = colors[pos]
                        break

                while x < pad["width"]:
                    #for i in range(0, pad["width"] - x):
                    add2protobuf(x, y, " ")
                    x += 1
                y += 1
                if y == pad["height"]:
                    break
            while y < pad["height"]:
                for x in range(0, pad["width"]):
                    add2protobuf(x, y, " ")
                y += 1
 
        else:
            chunks = []

            for string in strings:
                for i in range(0, len(string), pad["width"]):
                    chunks.append(string[i:i+pad["width"]])

            y = 0
            pos = 0
            color = ""
            for chunk in chunks:
                x = 0
                for sym in chunk:
                    if pos in colors:
                        color = colors[pos]

                    if sym == "\n":
                        if x != 0:
                            sym = term.normal + " "
                    else:
                        if len(chunk) == x + 1 or x + 1 + pad["x"] == term.width:
                            sym += term.normal
                        sym = color + sym

                    if x == 0 and sym == "\n":
                        y -= 1
                        x = pad["width"]
                    else:
                        add2protobuf(x, y, sym)
                        x += 1
                    pos += 1
                    
                    if color == term.normal:
                        color = ""

                if x != pad["width"]:
                    for i in range(0, pad["width"] - x):
                        add2protobuf(x, y, " ")
                        x += 1
                y += 1
                if y == pad["height"]:
                    break
            while y < pad["height"]:
                for x in range(0, pad["width"]):
                    add2protobuf(x, y, " ")
                y += 1

    for y in range(term.height):
        for x in range(term.width):
            if (x, y) in protobuf:
                buf += protobuf[(x, y)]
            else:
                buf += " "
        if y != term.height:
            buf += "\n"
    #print(protobuf); exit()
    sprint(term.clear + term.home)
    sprint(buf)

def update_sizes(init=False, all=False):
    if all:
        for pad in pads:
            Pad = pads[pad]
            if init:
                Pad["x"] = eval(Pad["xorg"])
                Pad["xs"] = 0
                Pad["y"] = eval(Pad["yorg"])
                Pad["ys"] = 0
                Pad["width"] = eval(Pad["worg"])
                Pad["ws"] = 0
                Pad["height"] = eval(Pad["horg"])
                Pad["hs"] = 0
            else:
                Pad["x"] = eval(Pad["xorg"] + "+" + str(Pad["xs"]))
                Pad["y"] = eval(Pad["yorg"] + "+" + str(Pad["ys"]))
                Pad["width"] = eval(Pad["worg"] + "+" + str(Pad["ws"]))
                Pad["height"] = eval(Pad["horg"] + "+" + str(Pad["hs"]))


## Maincode
update_sizes(all=True, init=True)
render()
while 1:
    with term.cbreak():
        maintext = pads["maintext"]
        pwidth = term.width
        pheight = term.height

        inp = term.inkey(timeout=1/fps)
        if inp:
            match inp:
                case "i": maintext["xcut"] = True if not maintext["xcut"] else False
                case "l": maintext["ws"] += 1
                case "h": maintext["ws"] -= 1 if maintext["width"] - 1 > 0 else 0
                case "k": maintext["hs"] += 1
                case "j": maintext["hs"] -= 1 if maintext["height"] - 1 > 0 else 0
                case "L": maintext["xs"] += 1
                case "H": maintext["xs"] -= 1 #if maintext["x"] - 1 > 0 else 0
                case "K": maintext["ys"] += 1
                case "J": maintext["ys"] -= 1 #if maintext["y"] - 1 > 0 else 0
                case "q": exit()
        if pheight != term.height or pwidth != term.width or inp:
            update_sizes(all=True)
            render()

