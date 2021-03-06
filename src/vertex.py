
import dataclasses

import numpy as np

import src.utils as utils

@dataclasses.dataclass
class Pixel():
    x: int
    y: int
    r: int
    g: int
    b: int
    a: int = 255

@dataclasses.dataclass
class Vertex():
    x: float
    y: float
    z: float = 1
    w: float = 1
    r: float = 0
    g: float = 0
    b: float = 0
    a: float = 255

    def __iter__(self):
        return self
    def as_ndarray(self) -> np.ndarray:
        return np.array(utils.object_to_list(self))
    def as_pixel(self) -> Pixel:
        return Pixel(
            x=round(self.x),
            y=round(self.y),
            r=round(255 * self.r),
            g=round(255 * self.g),
            b=round(255 * self.b),
            a=round(255 * self.a),
        )
    def position_data(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z, self.w])

def ndarray_to_vertex(q: np.ndarray, is_rounded: bool = True) -> Vertex:
    if is_rounded:
        return Vertex(
                *(np.round(q.tolist()).astype(int))
            )
    return Vertex(
        *(q.tolist())
    )

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
