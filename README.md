Second homework assignment for CS 4810

Markdown taken from class website

All code is my own.

What should be coded
==============

The entire flow looks like this (required parts are in bold):

1.  **When a color**, normal, or texture coordinate is specified, **remember it as the current value of that type**.
2.  **When a point is specified, store it in a list as with HW1. We’ll index that list in the say way we did for that HW.**
    1.  for the required part, just **store the (x, y, z, w)**
    2.  some elective parts will also require storing the current normal, color, and/or texture coordinate with the point
3.  When a drawing command is specified,
    1.  It it involves creating several triangles, do that and send the triangles through the next steps
    2.  **Apply Model/View transformations (rotations, scaling, translations, matrices, etc), if any, to each vertex.**
    3.  Clip planes happen here.
    4.  **Apply the current projection matrix, if any, to each vertex.**
    5.  Frustum clipping happens here in OpenGl, but we won’t add it.
    6.  **Divide each x, y, and z by w.**
    7.  **Apply a viewport transformation so that (-1, -1) is placed in the top left corner and (1, 1) in the bottom right corner of the image.**
    8.  **Rasterize the triangle into fragments, interpolating a z value** (and other values as extras require) **for each pixel. Only continue with those pixels that are on the screen (i.e., 0 ≤ x < w and 0 ≤ y < h) and have z between 0 and 1.**
    9.  **Check each pixel’s z against a depth buffer. Keep only those less than the buffer’s current value.**
    10.  Texture and lighting happens here to find colors for each fragment. It can also happen before the depth buffer check if you prefer.
    11.  **Set the pixel and depth buffer values**

Reading Input
-----------------
### Input Keywords
* **png *width height filename***
* **xyz** $ x \space y \space z$
* **trif** $ i_1 \space i_2 \space i_3$
* **color** $r \space g \space b$ : The inputs will be in range $0-1$.
* **loadmv** $a_{1,1} \space a_{1,2}\space a_{1,3}\space a_{1,4}\space a_{2,1}\space a_{2,2} \dots a_{4,4}$
* **loadp** $a_{1,1} \space a_{1,2}\space a_{1,3}\space a_{1,4}\space a_{2,1}\space a_{2,2} \dots a_{4,4}$

## Running the code

To run the program, use the command
```shell
$ make run file=inputfilename.txt
```