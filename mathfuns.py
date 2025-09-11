import math

## vector type
class vec2:
    x = 0
    y = 0

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, vec) -> "vec2":
        return vec2(self.x + vec.x, self.y + vec.y)

    def __str__(self) -> str:
        return f"{self.x};{self.y}"

## calculate distanse between pofloats
def dist(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) ## Pythagorean theorem

## is pofloat in circle?
def in_circle(xpofloat: float, ypofloat: float, xcenter: float, ycenter: float, radius: float) -> bool:
    if dist(xpofloat, ypofloat, xcenter, ycenter) <= radius:
        return True
    return False

## is pofloat in square?
def in_square(xpofloat: float, ypofloat: float, xbegin: float, ybegin: float, xlen: float, ylen: float) -> bool:
    if xbegin <= xpofloat and xbegin + xlen >= xpofloat:
        if ybegin <= ypofloat and ybegin + ylen >= ypofloat:
            return True
    return False

## is pofloat on line?
def on_line(xpofloat: float, ypofloat: float, xline1: float, yline1: float, xline2: float, yline2: float) -> bool:
    k = (yline2 - yline1) / (xline2 - xline1)
    if xpofloat * k - ypofloat == 0:
        return True
    return False

def in_triangle() -> bool:
    ... # to be continiud
