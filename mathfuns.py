import math

## vector type
class vec2:
    x = 0
    y = 0

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, vec) -> "vec2":
        return vec2(self.x + vec.x, self.y + vec.y)

    def __str__(self) -> str:
        return f"{self.x};{self.y}"

## calculate distanse between points
def dist(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) ## Pythagorean theorem

## is point in circle?
def inCircle(xpoint: int, ypoint: int, xcenter: int, ycenter: int, radius: int) -> bool:
    if dist(xpoint, ypoint, xcenter, ycenter) <= radius:
        return True
    return False

## is point in square?
def inSquare(xpoint: int, ypoint: int, xbegin: int, ybegin: int, xlen: int, ylen: int) -> bool:
    if xbegin <= xpoint and xbegin + xlen >= xpoint:
        if ybegin <= ypoint and ybegin + ylen >= ypoint:
            return True
    return False
