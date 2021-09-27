
import dataclasses

from src.utils import RGB, convert_hex_to_rgb

@dataclasses.dataclass
class Vertex():
    x: float
    y: float
    z: float = 1
    w: float = 1
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 255
    def __iter__(self):
        return self

def parse_xyrgb(line: "list[str]") -> Vertex:
    x = float(line[1])
    y = float(line[2])
    rgb = [int(line[3]), int(line[4]), int(line[5])]
    return Vertex(x, y, *rgb)

def parse_xyrgba(line: "list[str]") -> Vertex:
    x = float(line[1])
    y = float(line[2])
    rgba = [int(line[3]), int(line[4]), int(line[5]), int(line[6])]
    return Vertex(x, y, *rgba)

def parse_xyc(line: "list[str]") -> Vertex:
    x = float(line[1])
    y= float(line[2])
    hex = line[3]
    return vertex_from_xyc(x, y, hex)

def vertex_from_xyc(x: float, y: float, hex: str) -> Vertex:
    c: RGB = convert_hex_to_rgb(hex)
    return Vertex(x, y, c.r, c.g, c.b)
