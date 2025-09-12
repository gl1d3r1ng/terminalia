import blessed
import time

term = blessed.Terminal()

fps = 60
updates = 0

# switchers = {"colors0": [0, 1, 0, 1"frame"]}
switchers = {"colors0": {"frame": 0, "shift": 1, "updates": 0, "frameupdate": 15},\
            "bouncer0": {"frame": 0, "shift": 1, "updates": 0, "frameupdate": 15}}

colors0 = [term.normal, term.on_mediumpurple4, \
           term.on_mediumpurple3, term.on_mediumpurple2, term.on_mediumpurple1]

lastkey = ""

while 1:
    shift = 0
    print(term.home + term.clear + f"FPS: {fps}\nUpdates: {updates}")

    print(switchers["colors0"]["frameupdate"])
    print(f"\n{colors0[switchers['colors0']["frame"]]}Violet text{term.normal}")
    print(f"\n\n{term.green}h{term.normal},{term.green}l{term.normal} - change color updating speed\
        \n{term.green}j{term.normal},{term.green}k{term.normal} - change fps")
    
    ## change color
    if switchers["colors0"]["updates"] >= switchers["colors0"]["frameupdate"]:
        switchers["colors0"]["updates"] //= switchers["colors0"]["frameupdate"]
        if switchers["colors0"]["frame"] + switchers["colors0"]["shift"] in [len(colors0), -1]:
            switchers["colors0"]["shift"] *= -1
        switchers["colors0"]["frame"] += switchers["colors0"]["shift"]
    
    switchers["colors0"]["updates"] += 1
    
    with term.cbreak():
        lastkey = term.inkey(timeout=1/fps)
        match lastkey:
            case "h":
                shift = -1
            case "l":
                shift = 1
            case "k":
                fps += 1
            case "j":
                if fps - 1 > 0: fps -= 1
            # case _:
            #     shift = 0
    
    if switchers["colors0"]["frameupdate"] + shift > 0:
        switchers["colors0"]["frameupdate"] += shift

    updates += 1
    #time.sleep(1/fps)
