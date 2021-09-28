import copy

import numpy as np
from PIL import Image

import src.lines as lines
import src.utils as utils
import src.vertex as vertex


def transform_vertex(point: vertex.Vertex, draw_data: utils.DrawData) -> vertex.Vertex:
    """Ideas for this were taken from http://www.songho.ca/opengl/gl_transform.html

    Args:
        image (Image): The image we will add the pixel to
        point (vertex.Vertex): The point to be added
        draw_data (utils.DrawData): Data needed to draw the image
    """
    copy_point = copy.deepcopy(point)
    # Apply the model view transformations
    eye_coordinates: np.ndarray = np.matmul(draw_data.model_view, copy_point.position_data())
    # Apply the projection matrix
    clip_coordinates = np.matmul(draw_data.projection, eye_coordinates)
    # divide each x, y, and z by w
    copy_point.x = clip_coordinates[0] / clip_coordinates[3]
    copy_point.y = clip_coordinates[1] / clip_coordinates[3]
    copy_point.z = clip_coordinates[2] / clip_coordinates[3]
    copy_point.w = clip_coordinates[3]
    # apply a viewport transformation
    copy_point.x = (copy_point.x + 1) * draw_data.width/2
    copy_point.y = (copy_point.y + 1) * draw_data.height/2
    print(copy_point)
    return copy_point

def draw_3d_triangle(image: Image, draw_data: utils.DrawData, i1: vertex.Vertex, i2: vertex.Vertex, i3: vertex.Vertex):
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
        if not 0 <= pixel.x < draw_data.width:
            continue
        # check y
        if not 0 <= pixel.y < draw_data.height:
            continue
        # check z bounds
        if not draw_data.near <= pixel.z <= draw_data.far:
            continue
        # check depth buffer
        if draw_data.depth_buffer[(pixel.y, pixel.x)] < pixel.z:
            continue
        # Set the pixel and depth buffer values
        draw_data.depth_buffer[(pixel.y, pixel.x)] = pixel.z
        color: utils.RGB = draw_data.color.as_rgb(rounded=True)

        image.im.putpixel((pixel.x, pixel.y), (color.r, color.g, color.b, color.a))