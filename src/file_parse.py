
from PIL import Image

import src.vertex as vertex
import src.lines as lines
from src.utils import RGB, add_pixel_colors, convert_hex_to_rgb, line_to_list, ImageInfo


def get_image_info(line: str) -> ImageInfo:
    """parses the first line of the file to get the metadata

    Args:
        line (str): the first line of a file

    Returns:
        ImageInfo: the input file metadata
    """
    line_as_list = line_to_list(line)
    # Set the Image info
    image_info = ImageInfo(
        width=int(line_as_list[1]),
        height=int(line_as_list[2]),
        filename=line_as_list[3],
    )
    # Set the values for the case in which we are making multiple png files
    if line_as_list[0] == "pngs":
        image_info.number_of_images = int(line_as_list[-1])

    return image_info

def add_pixel(vert: vertex.Vertex, image: Image, color: RGB = None) -> None:
    # check to see if a color has been specified. If now, make color equal to the color of the vert
    if not color:
        color = RGB(
            r=vert.r,
            g=vert.g,
            b=vert.b,
            a=vert.a,
        )
    # Get the current value of the pixel in the immage
    original_color = RGB(*image.getpixel((vert.x, vert.y)))
    # if the alpha of the currently placed pixel is 0, we can just use our new color.
    # if the alpha of the currently placed pixel is not 0, we have to use the over operator
    # to determine the new color and alpha.
    if original_color.a != 0:
        color: RGB = add_pixel_colors(color, original_color)
    image.im.putpixel((vert.x, vert.y), (color.r, color.g, color.b, color.a))

def get_vertex_by_index(verts, index) -> vertex.Vertex:
    # if its a negative index just use that idex
    if index < 0:
        return verts[index]
    return verts[index - 1]

def parse_line(line: "list[str]", image: Image, vertex_list: "list[vertex.Vertex]") -> None:
    """
    parse keywords
    1) png width height filename: 
    2) xyz x y z:
    3) trif i1 i2 i3
    4) color r g b:
    5) loadmv a11 a12 ... a44
    6) loadp a11 a12 ... a44
    """
    keyword: str = line[0]
    if keyword == "xyrgb":
        # make the vertex
        new_vertex = vertex.parse_xyrgb(line)
        vertex_list.append(new_vertex)
    
    if keyword == "xyrgba":
        new_vertex = vertex.parse_xyrgba(line)
        vertex_list.append(new_vertex)


    if keyword == "xyc":
        # make the vertex
        new_vertex = vertex.parse_xyc(line)
        vertex_list.append(new_vertex)
    
    if keyword == "lineg":
        # linearly interpolate colors
        p1_index = int(line[1])
        p2_index = int(line[2])
        p1 = get_vertex_by_index(vertex_list, p1_index)
        p2 = get_vertex_by_index(vertex_list, p2_index)
        verts: list[vertex.Vertex] = lines.dda_on_vertex(p1, p2)
        for vert in verts:
            add_pixel(vert, image)
    
    if keyword in ["linec", "lineca"]:
        p1_index = int(line[1])
        p2_index = int(line[2])
        p1 = get_vertex_by_index(vertex_list, p1_index)
        p2 = get_vertex_by_index(vertex_list, p2_index)
        hexcolorcode = line[3]
        c: RGB = convert_hex_to_rgb(hexcolorcode)
        verts: list[vertex.Vertex] = lines.dda_on_vertex(p1, p2)
        for vert in verts:
            add_pixel(vert, image, c)


    if keyword == "trig":
        i1_index = int(line[1])
        i2_index = int(line[2])
        i3_index = int(line[3])
        i1 = get_vertex_by_index(vertex_list, i1_index)
        i2 = get_vertex_by_index(vertex_list, i2_index)
        i3 = get_vertex_by_index(vertex_list, i3_index)
        verts: list[vertex.Vertex] = lines.triangle_fill(i1, i2, i3)
        for vert in verts:
            add_pixel(vert, image)

    if keyword in ["tric", "trica"]:
        i1_index = int(line[1])
        i2_index = int(line[2])
        i3_index = int(line[3])
        i1 = get_vertex_by_index(vertex_list, i1_index)
        i2 = get_vertex_by_index(vertex_list, i2_index)
        i3 = get_vertex_by_index(vertex_list, i3_index)
        hexcolorcode = line[4]
        c: RGB = convert_hex_to_rgb(hexcolorcode)
        verts = lines.triangle_fill(i1, i2, i3)
        for vert in verts:
            add_pixel(vert, image, c)
    
    if keyword == "circle":
        i1_index = i1_index = int(line[1])
        i1 = get_vertex_by_index(vertex_list, i1_index)
        vertex_color = RGB(i1.r, i1.g, i1.b, i1.a)
        radius = int(line[2])
        verts = draw_circle(round(i1.x), round(i1.y), radius, vertex_color)
        for vert in verts:
            add_pixel(vert, image, vertex_color)

    if keyword == "cubicc":
        i1 = get_vertex_by_index(vertex_list, int(line[1]))
        i2 = get_vertex_by_index(vertex_list, int(line[2]))
        i3 = get_vertex_by_index(vertex_list, int(line[3]))
        i4 = get_vertex_by_index(vertex_list, int(line[4]))
        hexcolorcode: str = line[5]
        c: RGB = convert_hex_to_rgb(hexcolorcode)
        verts = draw_bezier_curve([i1,i2,i3,i4])
        for vert in verts:
            add_pixel(vert, image, c)
    
    if keyword == "beznc":
        # n is the number of control points for the curve
        n = int(line[1])
        control_points = []
        for i in range(n):
            control_points.append(
                get_vertex_by_index(vertex_list, int(line[2 + i]))
            )
        hexcolorcode: str = line[-1]
        c: RGB = convert_hex_to_rgb(hexcolorcode)
        verts = draw_bezier_curve(control_points)
        for vert in verts:
            add_pixel(vert, image, c)
    
    if keyword == "cubicg":
        i1 = get_vertex_by_index(vertex_list, int(line[1]))
        i2 = get_vertex_by_index(vertex_list, int(line[2]))
        i3 = get_vertex_by_index(vertex_list, int(line[3]))
        i4 = get_vertex_by_index(vertex_list, int(line[4]))
        verts = draw_bezier_curve([i1,i2,i3,i4])
        for vert in verts:
            add_pixel(vert, image)