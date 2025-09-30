import blessed
import re

term = blessed.Terminal()
fps = 60

text = "I\'m just a text for [green]terminalia[normal] pads demo\n\\[nothing] special\n[red]my author is a crutchmaker[normal]\n[yellow]h/l[normal] to resize my [purple]width[normal]\n[yellow]j/k[normal] to resize my [purple]height[normal]\n[yellow]H/J/K/L[normal] to shift [blue]me[normal]\n[yellow]i[normal] to toogle xcut [blue]mode[normal]"
pads = {"maintext": {"brcolor": None, "disable": False, "border": True, "xorg": "2", "yorg": "4", "worg": "30", "horg": "10", "padding": 0, "xcut": False, "scroll": 1, "text": text},\
        "coords": {"brcolor": "purple", "disable": False, "border": True, "xorg": "term.width // 2", "yorg": "term.height // 2", "worg": "10", "horg": "6", "padding": 0, "xcut": False, "scroll": 0, "text": ""},\
        "term": {"brcolor": "yellow", "disable": False, "border": True, "xorg": "term.width // 2", "yorg": "term.height // 2 - 8", "worg": "10", "horg": "4", "padding": 0, "xcut": False, "scroll": 0, "text": ""}\
        }
protobuf = {}

def sprint(text):
    print(text, end="")

def render_pad(padname: str) -> None:
    global protobuf, add2protobuf, pads
    pad = pads[padname]
    if not pad["disable"]:
        add2protobuf = lambda x, y, char, precolor, postcolor: protobuf.update({(pad['x'] + x, pad['y'] + y): {"char": char, "precolor": precolor, "postcolor": postcolor}})
        text = pad["text"]
        xcut = pad["xcut"]

        pattern = r'(?<!\\)\[.*?]'
        matches = set(re.findall(pattern, text))
        for mat in matches:
            text = text.replace(mat, getattr(term, mat[1:-1]))
        text = text.replace("\\[", "[")
        # print(text.encode("utf-8")); exit()
        # print(text); exit()
        #matches = [[match.group(), match.start()] for match in re.finditer(pattern, text)]


        brcolor = ""; rescolor = ""
        if pad["brcolor"] != None:
            brcolor = getattr(term, pad["brcolor"])
            rescolor = term.normal

        if pad["border"]:
            add2protobuf(-1 - pad["padding"], -1 - pad["padding"], "┏", brcolor, "")
            add2protobuf(pad["width"] + pad["padding"], -1 - pad["padding"], "┓", "", rescolor)
            add2protobuf(-1 - pad["padding"], pad["height"] + pad["padding"], "┗", brcolor, "")
            add2protobuf(pad["width"] + pad["padding"], pad["height"] + pad["padding"], "┛", "" , rescolor)
            for x in range(0 - pad["padding"], pad["width"] + pad["padding"]):
                add2protobuf(x, -1 - pad["padding"], "━", "", "")
            for y in range(0 - pad["padding"], pad["height"] + pad["padding"]):
                add2protobuf(-1 - pad["padding"], y, "┃", brcolor, rescolor)
                add2protobuf(pad["width"] + pad["padding"], y, "┃", term.normal + brcolor, rescolor)
            for x in range(0 - pad["padding"], pad["width"] + pad["padding"]):
                add2protobuf(x, pad["height"] + pad["padding"], "━", "", "")

        y = 0
        x = 0
        precolor = ""
        postcolor = ""
        harverst = ""
        for sym in text:
            #sym = text[index]
            if harverst != "":
                harverst += sym
                if sym == "m":
                    precolor += harverst
                    harverst = ""
            else:
                if sym == "\n":
                    postcolor = term.normal
                    while x < pad["width"]:
                        add2protobuf(x, y, " ", "", postcolor)
                        x += 1
                        postcolor = ""
                    postcolor = ""
                    y += 1
                    if y == pad["height"]:
                        break
                    x = 0
                elif ord(sym) == 27:
                    harverst += sym
                else:
                    if x >= pad["width"]:
                        if xcut:
                            if x == pad["width"]:
                                add2protobuf(x - 1, y, ">", term.reverse, term.normal)
                                x += 1
                        else:
                            y += 1
                            if y == pad["height"]:
                                break
                            x = 0
                            add2protobuf(x, y, sym, precolor, postcolor)
                            if precolor != "":
                                precolor = ""
                            x += 1
                    else:
                        add2protobuf(x, y, sym, precolor, postcolor)
                        if precolor == term.normal:
                            precolor = ""
                        x += 1
        while y < pad["height"]:
            postcolor = term.normal
            while x < pad["width"]:
                add2protobuf(x, y, " ", "", postcolor)
                x += 1
                postcolor = ""
            x = 0
            y += 1

        # print(protobuf); exit()


def update() -> None:
    global protobuf,pads

    pads["coords"]["text"] = f"[purple]Textarea[normal]\n[blue]x[normal]: {pads['maintext']['x']}\n[blue]y[normal]: {pads['maintext']['y']}\n[blue]w[normal]: {pads['maintext']['width']}\n[blue]h[normal]: {pads['maintext']['height']}"
    pads["term"]["text"] = f"[black_on_yellow]Terminal[normal]\n[green]w[normal]: {term.width}\n[green]h[normal]: {term.height}"

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

update_sizes(True, True)
update()
while 1:
    with term.cbreak(), term.hidden_cursor():
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

        if inp or pheight != term.height or pwidth != term.width:
            update_sizes(all=True)
            update()
