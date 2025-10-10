import blessed
import re

term = blessed.Terminal()
fps = 60

text = "I\'m just a text for \\[green]terminalia\\[normal] pads demo\n[nothing] special\n\\[red]my author is a crutchmaker\\[normal]\n\\[yellow]h/l\\[normal] to resize my \\[purple]width\\[normal]\n\\[yellow]j/k\\[normal] to resize my \\[purple]height\\[normal]\n\\[yellow]H/J/K/L\\[normal] to shift \\[blue]me\\[normal]\n\\[yellow]i\\[normal] to toogle xcut \\[blue]mode\\[normal]"
pads = {"maintext":\
        {"brcolor": None, "disable": False, "border": True, "xorg": "2", "yorg": "4", "worg": "40", "horg": "15", "xpadding": 1, "ypadding": 2, "xcut": False, "scroll": 1, "text": text},\
        "coords": {"brcolor": "purple", "disable": False, "border": True, "xorg": "term.width // 2", "yorg": "term.height // 2", "worg": "15", "horg": "12", "xpadding": 0, "ypadding": 0, "xcut": False, "scroll": 0, "text": ""},\
        "term": {"brcolor": "yellow", "disable": False, "border": True, "xorg": "term.width // 2", "yorg": "term.height // 2 - 8", "worg": "12", "horg": "6", "xpadding": 0, "ypadding": 0, "xcut": False, "scroll": 0, "text": ""}\
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

        #pattern = r'(?<!\\)\\[.*?]'
        pattern = r"\\\[.+?]"
        matches = set(re.findall(pattern, text))
        for mat in matches:
            text = text.replace(mat, getattr(term, mat[2:-1]))
        #text = text.replace("\\[", "[")
        # print(text.encode("utf-8")); exit()
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

def update() -> None:
    global protobuf,pads

    pads["coords"]["text"] = f"\\[purple]Textarea\\[normal]\n\\[blue]x\\[normal]: {pads['maintext']['x']}\n\\[blue]y\\[normal]: {pads['maintext']['y']}\n\\[blue]w\\[normal]: {pads['maintext']['width']}\n\\[blue]h\\[normal]: {pads['maintext']['height']}\n\\[blue]xpadding\\[normal]: {pads['maintext']['xpadding']}\n\\[blue]ypadding\\[normal]: {pads['maintext']['ypadding']}\n\\[blue]scroll\\[normal]: {pads['maintext']['scroll']}\n\\[blue]xcut\\[normal]: {pads['maintext']['xcut']}"
    pads["term"]["text"] = f"\\[black_on_yellow]Terminal\\[normal]\n\\[green]w\\[normal]: {term.width}\n\\[green]h\\[normal]: {term.height}"

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
                case "i": maintext["xcut"] = (maintext["xcut"] -1) * -1 
                case "b": maintext["border"] = (maintext["border"] - 1) * -1
                case "n": maintext["scroll"] += 1
                case "N": maintext["scroll"] -= 1 if maintext["scroll"] > 0 else 0
                case "l": maintext["ws"] += 1
                case "h": maintext["ws"] -= 1 if maintext["width"] - 1 > 0 else 0
                case "k": maintext["hs"] += 1
                case "j": maintext["hs"] -= 1 if maintext["height"] - 1 > 0 else 0
                case "L": maintext["xs"] += 1
                case "H": maintext["xs"] -= 1 #if maintext["x"] - 1 > 0 else 0
                case "K": maintext["ys"] += 1
                case "J": maintext["ys"] -= 1 #if maintext["y"] - 1 > 0 else 0
                case "o": maintext["xpadding"] += 1
                case "O": maintext["xpadding"] -= 1 if maintext["xpadding"] > 0 else 0
                case "p": maintext["ypadding"] += 1
                case "P": maintext["ypadding"] -= 1 if maintext["ypadding"] > 0 else 0
                case "q": exit()

        if inp or pheight != term.height or pwidth != term.width:
            update_sizes(all=True)
            update()
