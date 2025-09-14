import blessed

term = blessed.Terminal()

def paint(msg: list) -> str:
    buf = ""
    for item in msg:
        if item == "\0":
            buf += term.normal
        elif item[0] == "\0":
            buf += getattr(term, item[1:])
        else:
            buf += item
    return buf

msgs = [["\0tomato", "red", "\0", " text"],
        ["I am a purple ", "\0on_mediumpurple4", "T", "\0on_mediumpurple3", "E", "\0on_mediumpurple2", "X",\
         "\0on_mediumpurple1", "T", "\0"]]

for msg in msgs:
    print(paint(msg))
