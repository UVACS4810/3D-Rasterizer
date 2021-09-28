
from PIL import Image
import numpy as np
import copy

import src.vertex as vertex
import src.lines as lines
import src.utils as utils

def get_image_info(line: str) -> utils.ImageInfo:
    """parses the first line of the file to get the metadata

    Args:
        line (str): the first line of a file

    Returns:
        ImageInfo: the input file metadata
    """
    line_as_list = utils.line_to_list(line)
    # Set the Image info
    image_info = utils.ImageInfo(
        width=int(line_as_list[1]),
        height=int(line_as_list[2]),
        filename=line_as_list[3],
    )
    # Set the values for the case in which we are making multiple png files
    if line_as_list[0] == "pngs":
        image_info.number_of_images = int(line_as_list[-1])

    return image_info

def convert_to_screen_coordinates(point: vertex.Vertex, draw_data: utils.DrawData) -> None:
    new_x = (draw_data.width/2 * point.x) + (point.x + draw_data.width/2)
    new_y = (draw_data.height/2 * point.y) + (point.y + draw_data.height/2)
    point.x = new_x
    point.y = new_y

def transform_vertex(point: vertex.Vertex, draw_data: utils.DrawData) -> vertex.Vertex:
    """Ideas for this were taken from http://www.songho.ca/opengl/gl_transform.html

    Args:
        image (Image): The image we will add the pixel to
        point (vertex.Vertex): The point to be added
        draw_data (utils.DrawData): Data needed to draw the image
    """
    copy_point = copy.deepcopy(point)
    # Apply the model view transformations
    print("before mv = " + str(copy_point.position_data()))
    eye_coordinates: np.ndarray = np.matmul(copy_point.position_data(), draw_data.model_view)
    print("after mv = " + str(eye_coordinates))
    # Apply the projection matrix
    clip_coordinates = np.matmul(eye_coordinates, draw_data.projection)
    # divide each x, y, and z by w
    copy_point.x = clip_coordinates[0] / clip_coordinates[3]
    copy_point.y = clip_coordinates[1] / clip_coordinates[3]
    copy_point.z = clip_coordinates[2] / clip_coordinates[3]
    copy_point.w = clip_coordinates[3]
    # apply a viewport transformation
    copy_point.x = (copy_point.x + 1) * draw_data.width/2
    copy_point.y = (copy_point.y + 1) * draw_data.height/2
    return copy_point

def draw_triangle(image: Image, draw_data: utils.DrawData, i1: vertex.Vertex, i2: vertex.Vertex, i3: vertex.Vertex):
    # First, transform the vertexes provided
    p1 = transform_vertex(i1, draw_data)
    p2 = transform_vertex(i2, draw_data)
    p3 = transform_vertex(i3, draw_data)
    # Rasterize the triangle into fragments, interpolating a z value 
    # (and other values as extras require) for each pixel. 
    pixels: list[vertex.Vertex] = lines.triangle_fill(p1, p2, p3)
    # Only continue with those pixels that are on the screen and 
    # have z between 0 and 1. 
    for pixel in pixels:
        # check x
        if pixel.x not in range(draw_data.width):
            continue
        # check y
        if pixel.y not in range(0, draw_data.height):
            continue
        # check z bounds
        if not draw_data.near <= pixel.z <= draw_data.far:
            continue
        # check depth buffer
        if draw_data.depth_buffer[(pixel.y, pixel.x)]:
            if draw_data.depth_buffer[(pixel.y, pixel.x)] < pixel.z:
                continue
        # Set the pixel and depth buffer values
        draw_data.depth_buffer[(pixel.y, pixel.x)] = pixel.z
        color: utils.RGB = draw_data.color.as_rgb()
        image.im.putpixel((pixel.x, pixel.y), (color.r, color.g, color.b, color.a))

def get_vertex_by_index(verts, index: str) -> vertex.Vertex:
    if index.isnumeric():
        index = int(index)
    else:
        raise Exception("The index of a vertex must be a number", index)
    # if its a negative index just use that idex
    if index < 0:
        return verts[index]
    return verts[index - 1]

def parse_line(line: "list[str]", image: Image, draw_data: utils.DrawData) -> None:
    """
    parse keywords:
    \b xyz x y z:
    \b trif i1 i2 i3
    \b color r g b:
    \b loadmv a11 a12 ... a44
    \b loadp a11 a12 ... a44
    """
    keyword: str = line[0]

    if keyword == "xyz":
        new_vertex: vertex.Vertex = vertex.Vertex(
            x=float(line[1]),
            y=float(line[2]),
            z=float(line[3])
        )
        draw_data.vertex_list.append(new_vertex)

    if keyword == "trif":
        i1, i2, i3 = line[1:4]
        p1 = get_vertex_by_index(draw_data.vertex_list, i1)
        p2 = get_vertex_by_index(draw_data.vertex_list, i2)
        p3 = get_vertex_by_index(draw_data.vertex_list, i3)
        draw_triangle(image, draw_data, p1, p2, p3)
    
    if keyword == "color":
        r = float(line[1])
        g = float(line[2])
        b = float(line[3])
        draw_data.color = utils.RGBFloat(r, g, b)
    
    if keyword == "loadmv":
        draw_data.model_view = np.asarray(line[1:], float).reshape(4,4)
        print(draw_data.model_view)
