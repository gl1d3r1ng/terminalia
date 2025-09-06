import json

def loadfile(name: str):
    return json.loads(open(name, "r").read())


