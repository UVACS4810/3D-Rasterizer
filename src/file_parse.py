
import copy
import math

import numpy as np
from PIL import Image

import src.three_d as three_d
import src.utils as utils
import src.vertex as vertex


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

def get_vertex_by_index(verts, index: str) -> vertex.Vertex:
    if (index.strip("-")).isnumeric():
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
    ### DRAW DATA UPDATES ###
    if keyword == "xyz":
        new_vertex: vertex.Vertex = vertex.Vertex(
            x=float(line[1]),
            y=float(line[2]),
            z=float(line[3]),
            r=draw_data.color.r,
            g=draw_data.color.g,
            b=draw_data.color.b,
            a=draw_data.color.a,
        )
        draw_data.vertex_list.append(new_vertex)

    elif keyword == "color":
        r = float(line[1])
        g = float(line[2])
        b = float(line[3])
        draw_data.color = utils.RGBFloat(r, g, b)
    
    elif keyword == "loadmv":
        # Take the 1x16 list and turn it into a 4x4 ndarray
        draw_data.model_view = np.asarray(line[1:], float).reshape(4,4)

    elif keyword == "loadp":
        # Take the 1x16 list and turn it into a 4x4 ndarray
        draw_data.projection = np.asarray(line[1:], float).reshape(4,4)
    
    ### DRAWING TRIANGLES ###
    elif keyword == "trif":
        i1, i2, i3 = line[1:4]
        p1 = get_vertex_by_index(draw_data.vertex_list, i1)
        p2 = get_vertex_by_index(draw_data.vertex_list, i2)
        p3 = get_vertex_by_index(draw_data.vertex_list, i3)
        three_d.draw_3d_triangle(image, draw_data, p1, p2, p3)
    
    elif keyword == "trig":
        i1, i2, i3 = line[1:4]
        p1 = get_vertex_by_index(draw_data.vertex_list, i1)
        p2 = get_vertex_by_index(draw_data.vertex_list, i2)
        p3 = get_vertex_by_index(draw_data.vertex_list, i3)
        three_d.draw_3d_triangle(image, draw_data, p1, p2, p3, gouraud=True)
    
    ### MATRIX MANIPULATION ###
    elif keyword == "translate":
        assert len(line) == 4
        dx: float = float(line[1])
        dy: float = float(line[2])
        dz: float = float(line[3])
        translate_matrix = np.identity(4)
        translate_matrix[0,3] = dx
        translate_matrix[1,3] = dy
        translate_matrix[2,3] = dz
        draw_data.model_view = np.matmul(draw_data.model_view, translate_matrix)

    elif keyword == "rotatex":
        assert len(line) == 2
        theta = math.radians(float(line[1]))

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        rotation_matrix = np.identity(4)
        rotation_matrix[1,1] = cos_theta
        rotation_matrix[2,2] = cos_theta
        rotation_matrix[2,1] = sin_theta
        rotation_matrix[1,2] = -sin_theta
        draw_data.model_view = np.matmul(draw_data.model_view, rotation_matrix)
    
    elif keyword == "rotatey":
        assert len(line) == 2
        theta = math.radians(float(line[1]))

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        rotation_matrix = np.identity(4)
        rotation_matrix[0,0] = cos_theta
        rotation_matrix[2,2] = cos_theta
        rotation_matrix[0,2] = sin_theta
        rotation_matrix[2,0] = -sin_theta
        draw_data.model_view = np.matmul(draw_data.model_view, rotation_matrix)
    
    elif keyword == "rotatez":
        assert len(line) == 2
        theta = math.radians(float(line[1]))

        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        rotation_matrix = np.identity(4)
        rotation_matrix[0,0] = cos_theta
        rotation_matrix[1,1] = cos_theta
        rotation_matrix[1,0] = sin_theta
        rotation_matrix[0,1] = -sin_theta
        draw_data.model_view = np.matmul(draw_data.model_view, rotation_matrix)
    
    elif keyword == "scale":
        assert len(line) == 4
        sx = float(line[1])
        sy = float(line[2])
        sz = float(line[3])

        scale_matrix = np.identity(4)
        scale_matrix[0,0] = sx
        scale_matrix[1,1] = sy
        scale_matrix[2,2] = sz
        draw_data.model_view = np.matmul(draw_data.model_view, scale_matrix)
    
    elif keyword == "multmv":
        # Take the 1x16 list and turn it into a 4x4 ndarray
        assert len(line) == 17
        draw_data.model_view = np.matmul(draw_data.model_view, np.asarray(line[1:], float).reshape(4,4))

    # elif keyword == "rotate":
    #     # Info about the rotation matrix taken from 
    #     # http://www.songho.ca/opengl/gl_matrix.html and 
    #     # https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glRotate.xml
    #     assert len(line) == 5
    #     # radians we will rotate counter-clockwise
    #     theta = math.radians(float(line[1]))
    #     # x, y, and z components of our rotation vector
    #     x = float(line[2])
    #     y = float(line[3])
    #     z = float(line[4])
    #     ## The first step is to normalize the vector
    #     length = math.sqrt(x^2 + y^2 + z^2)
    #     x = x/length
    #     y = y/length
    #     z = z/length
    #     # Now that we have a normalized vector, we will compute the sin and cos of our angle
    #     c = math.cos(theta)
    #     s = math.sin(theta)

