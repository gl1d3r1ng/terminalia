import blessed
import math

term = blessed.Terminal()

fps = 60
updates = 0
c = 0.09

switchers = {"color0": {"speed": 10}}

colors0 = [term.normal, term.on_mediumpurple4, \
           term.on_mediumpurple3, term.on_mediumpurple2, term.on_mediumpurple1]

for switcher in switchers:
    swch = switchers[switcher]
    swch["len"] = len(colors0) - 1

def get_state(switcher_name: str) -> int:
    swch = switchers[switcher_name]
    ln = swch["len"]
    speed = swch["speed"]
    return round(ln / 2 * (math.sin(0.1 * c * speed * updates) + 1))

while 1:
    updates = 0
    while updates < 10 ** 10:
        print(f"{term.home}{term.clear}\n{term.red}FPS{term.normal}: {fps}\n{term.yellow}Updates{term.normal}: {updates}\n{term.green}speed{term.normal}: {switchers['color0']['speed']}")
        swch = switchers["color0"]
        state = get_state("color0")
        print(f"{colors0[state]}I\'m violet text!{term.normal}")
        
        with term.cbreak():
            lastkey = term.inkey(timeout=1/fps)
            match lastkey:
                case "h":
                    swch["speed"] -= 1 if swch["speed"] > 0 else 0
                case "l":
                    swch["speed"] += 1
                case "k":
                    fps += 1
                case "j":
                    if fps - 1 > 0: fps -= 1
                case "q":
                    exit()

        updates += 1
