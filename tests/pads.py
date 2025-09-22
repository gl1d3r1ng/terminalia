import blessed

term = blessed.Terminal()
fps = 60

msg = "I\'m just a text for [green]terminalia[normal] pads demo\n\\[nothing] special\nmy author is a crutchmaker\nh/l to resize my width\nj/k to resize my height\nH/J/K/L to shift me"
pads = {0: {"name": "text area", "border": True, "x": 2, "y": 4, "width": 30, "height": 10, "padding": 0, "buf": msg},\
        1: {"name": "coords", "border": True, "x": term.width - 16, "y": term.height // 2, "width": 10, "height": 6, "padding": 0, "buf": ""}}

def sprint(text, end=""):
    print(text, end=end)

def render_print():
    add2protobuf  = lambda x, y, char: protobuf.update({(pad['x'] + x, pad['y'] + y): char})

    sprint(term.clear + term.home)
    
    pads[1]["buf"] = f"Textarea\nx: {pads[0]['x']}\ny: {pads[0]['y']}\nw: {pads[0]['width']}\nh: {pads[0]['height']}"
    buf = ""
    protobuf = {}

    for _, pad in pads.items():
        colors = {}
        pos = 0
        harvest = ""
        text = ""
        escape_seq = False
        for sym in pad["buf"]:
            if ((sym == "[" and not escape_seq) or harvest != "") and sym != "]":
                harvest += sym
            elif sym == "]" and harvest != "":
                colors[pos] = getattr(term, harvest[1:])
                harvest = ""
            else:
                if sym == "\\":
                    if not escape_seq:
                        escape_seq = True
                        sym = ""
                if sym != "" and escape_seq:
                    escape_seq = False
                text += sym
                pos += 1

        # print(colors, text); exit()
        strings = text.split("\n")
        chunks = []

        for string in strings:
            for i in range(0, len(string), pad["width"]):
                chunks.append(string[i:i+pad["width"]])

        if pad["border"]:
            add2protobuf(-1 - pad["padding"], -1 - pad["padding"], "┏")
            add2protobuf(pad["width"] + pad["padding"], -1 - pad["padding"], "┓")
            add2protobuf(-1 - pad["padding"], pad["height"] + pad["padding"], "┗")
            add2protobuf(pad["width"] + pad["padding"], pad["height"] + pad["padding"], "┛")
            for x in range(0 - pad["padding"], pad["width"] + pad["padding"]):
                add2protobuf(x, -1 - pad["padding"], "━")
            for y in range(0 - pad["padding"], pad["height"] + pad["padding"]):
                add2protobuf(-1 - pad["padding"], y, "┃")
                add2protobuf(pad["width"] + pad["padding"], y, "┃")
            for x in range(0 - pad["padding"], pad["width"] + pad["padding"]):
                add2protobuf(x, pad["height"] + pad["padding"], "━")

        y = 0
        pos = 0
        color = ""
        for chunk in chunks:
            x = 0
            for sym in chunk:
                if pos in colors:
                    color = colors[pos]
                    sym = color + sym
                elif x == 0:
                    sym = color + sym

                if len(chunk) == x + 1:
                    sym += term.normal

                add2protobuf(x, y, sym)
                
                if color == term.normal:
                    color = ""
                x += 1; pos += 1

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
    sprint(buf)

render_print()

while 1:
    with term.cbreak():
        inp = term.inkey(timeout=1/fps)
        if inp:
            match inp:
                case "l": pads[0]["width"] += 1
                case "h": pads[0]["width"] -= 1 if pads[0]["width"] - 1 > 0 else 0
                case "k": pads[0]["height"] += 1
                case "j": pads[0]["height"] -= 1 if pads[0]["height"] - 1 > 0 else 0
                case "L": pads[0]["x"] += 1
                case "H": pads[0]["x"] -= 1 if pads[0]["x"] - 1 > 0 else 0
                case "K": pads[0]["y"] += 1
                case "J": pads[0]["y"] -= 1 if pads[0]["y"] - 1 > 0 else 0
                case "q": exit(0)
            render_print()
        else:
            ...
