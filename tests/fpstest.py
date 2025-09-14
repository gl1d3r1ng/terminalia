import blessed
import time

term = blessed.Terminal()

fps = 60
updates = 0

# switchers = {"color0": [0, 1, 0, 1"frame"]}
switchers = {"color0": {"frame": 0, "shift": 1, "updates": 0, "frameupdate": 15},\
            "bouncer0": {"frame": 0, "maxframe": 9, "shift": 1, "updates": 0, "frameupdate": 15}}

colors0 = [term.normal, term.on_mediumpurple4, \
           term.on_mediumpurple3, term.on_mediumpurple2, term.on_mediumpurple1]

lastkey = ""

bouncer0 = switchers["bouncer0"]
color0 = switchers["color0"]
while 1:
    shift = 0

    print(term.home + term.clear + f"FPS: {fps}\nUpdates: {updates}")

    print(color0["frameupdate"])
    print(f"\n{colors0[color0["frame"]]}Violet text{term.normal} <- {term.green}blinking text{term.normal}")

    print(f"[{' ' * bouncer0['frame']}{term.yellow}*\
{term.normal}{' ' * (bouncer0['maxframe'] - 1 - bouncer0['frame'])}] <- {term.green}bouncer{term.normal}")

    print(f"\n\n{term.green}h{term.normal},{term.green}l{term.normal} - change color updating speed\
        \n{term.green}j{term.normal},{term.green}k{term.normal} - change fps\
        \n{term.green}q{term.normal} - exit")
    
    ## change color
    if color0["updates"] >= color0["frameupdate"]:
        color0["updates"] //= color0["frameupdate"]
        if color0["frame"] + color0["shift"] in [len(color0), -1]:
            color0["shift"] *= -1
        color0["frame"] += color0["shift"]
    
    color0["updates"] += 1

    ## move bouncer
    if bouncer0["updates"] >= bouncer0["frameupdate"]:
        bouncer0["updates"] //= bouncer0["frameupdate"]
        if bouncer0["frame"] + bouncer0["shift"] in [bouncer0["maxframe"], -1]:
            bouncer0["shift"] *= -1
        bouncer0["frame"] += bouncer0["shift"]

    bouncer0["updates"] += 1

    ## bouncer0 (ping-pong)

    
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
            case "q":
                exit()
    
    if color0["frameupdate"] + shift > 0:
        color0["frameupdate"] += shift

    updates += 1
    #time.sleep(1/fps)
