"""
Architecture.


### Desktop application

-----------------------------------------------------
 (Python)   VisPy 2 high-level API
-----------------------------------------------------
 (Python)   **VisPy 2 Datoviz renderer API**
-----------------------------------------------------
 (Cython)   Datoviz Python bindings
-----------------------------------------------------
 (C)        Datoviz core renderer
-----------------------------------------------------


### Remote application

Client:

-----------------------------------------------------
 (Python)   VisPy 2 high-level API
-----------------------------------------------------
 (Python)   VisPy 2 protocol generator (API -> YAML)
-----------------------------------------------------

Server:

-----------------------------------------------------
 (Python)   VisPy 2 protocol parser (YAML -> API)
-----------------------------------------------------
 (Python)   **VisPy 2 Datoviz renderer API**
-----------------------------------------------------
 (Cython)   Datoviz Python bindings
-----------------------------------------------------
 (C)        Datoviz core renderer
-----------------------------------------------------


"""

# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import logging
from pathlib import Path
from cv2 import CAP_OPENNI_VALID_DEPTH_MASK

import numpy as np

import datoviz as dvz


# -------------------------------------------------------------------------------------------------
# Logger
# -------------------------------------------------------------------------------------------------

logger = logging.getLogger('datoviz')


# -------------------------------------------------------------------------------------------------
# Mappings
# -------------------------------------------------------------------------------------------------

_VISUAL_TYPES = {
    'point': 1,  # DVZ_GRAPHICS_POINT
}

_DTYPES = {
    'vec3': np.dtype(('float32', 3)),
    'cvec4': np.dtype(('uint8', 4)),
}


# -------------------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------------------

VERTEX_DAT_ID = 100


# -------------------------------------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
# Array
# -------------------------------------------------------------------------------------------------

class Array:
    shape = None
    dtype = None
    dtype_orig = None
    _arr = None

    def __init__(self, shape, dtype=None):
        self.shape = shape
        self.dtype = _DTYPES[dtype] if dtype in _DTYPES else np.dtype(dtype)
        self.dtype_orig = dtype

        self._arr = np.zeros(shape, dtype=dtype)
        # if arr.ndim == 1:
        #     arr = arr[:, np.newaxis]

    def __setitem__(self, idx, val):
        self._arr[idx] = val


# -------------------------------------------------------------------------------------------------
# Visual
# -------------------------------------------------------------------------------------------------

class Visual:
    _id = None
    canvas = None  # canvas
    _rd = None
    _props = None
    _vtype = None

    def __init__(self, parent, vtype):
        self.canvas = parent  # canvas
        self._vtype = vtype
        self._rd = parent._rd  # renderer
        self._id = self._rd._id()
        self._props = {}
        assert self._id

        vtype_id = _VISUAL_TYPES.get(vtype)
        assert vtype_id

        self._rd._rst.create_graphics(
            self.canvas._id, vtype_id, id=self._id, flags=3)

        # Create the visual-specific vertex buffer
        if vtype == 'point':
            self._rd._rst.create_dat(
                2, 3*(4*4+4*1+1*4), id=VERTEX_DAT_ID, flags=0)
            self._rd._rst.set_vertex(self._id, VERTEX_DAT_ID)

    def __setitem__(self, prop, arr):
        assert isinstance(arr, Array)
        # TODO: if np.ndarray, automatically wrap it within an Array
        self._props[prop] = arr

    def _get_vertex(self):

        if self._vtype == 'point':
            # Return the vertex data from the props
            pos = self._props.get('pos', None)
            color = self._props.get('color', None)
            size = self._props.get('size', None)

            assert pos
            assert color
            assert size

            # pos_arr = self._arrays[pos.array_id][0]
            # color_arr = self._arrays[color.array_id][0]
            # size_arr = self._arrays[size.array_id][0]

            # TODO: take offset and shape into account

            # # Apply transforms to props.
            # pos_arr = self._apply_transforms(pos.transforms, pos_arr)
            # color_arr = self._apply_transforms(color.transforms, color_arr)
            # size_arr = self._apply_transforms(size.transforms, size_arr)

            # Create the vbo.
            n = pos.shape[0]
            vbo = np.empty(
                n, dtype=[('pos', 'float32', (3,)), ('color', 'uint8', (4,)), ('size', 'float32')])

            # Set the transform props to the vbo.
            vbo['pos'] = pos._arr
            vbo['color'] = color._arr
            vbo['size'].flat = size._arr

            return vbo


# -------------------------------------------------------------------------------------------------
# Canvas
# -------------------------------------------------------------------------------------------------

class Canvas:
    _id = None
    _rd = None

    def __init__(self, parent, width, height):
        self._rd = parent  # renderer
        self._id = self._rd._id()
        assert self._id

        flags = 0
        self._rd._rst.create_canvas(width, height, id=self._id, flags=flags)

    def visual(self, vtype):
        return Visual(self, vtype)

    def draw(self, visuals, transforms=None, viewport=None):
        if not visuals:
            return

        if not viewport or viewport == 'full':
            viewport = (0, 0, 0, 0)

        rst = self._rd._rst
        cid = self._id

        # Begin.
        rst.record_begin(cid)

        # Viewport.
        rst.record_viewport(cid, *viewport)

        # Draw the visuals.
        for visual in visuals:

            # Compute the VBO from the props, arrays, transforms, and upload it
            vbo = visual._get_vertex()
            rst.upload_dat(VERTEX_DAT_ID, 0, vbo)

            # Record the draw command.
            rst.record_draw(cid, visual._id, 0, vbo.size)

        # End
        rst.record_end(cid)


# -------------------------------------------------------------------------------------------------
# Renderer
# -------------------------------------------------------------------------------------------------

class Renderer:
    def __init__(self):
        self._rnd = dvz.Renderer(offscreen=False)
        self._rst = dvz.Requester()
        self._runner = dvz.Runner(self._rnd)
        # self._ids = {}
        self._next_id = 1
        self._rst.begin()

    def _id(self):
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def canvas(self, width, height):
        return Canvas(self, width, height)

    def array(self, shape, dtype=None):
        return Array(shape, dtype=dtype)

    def flush(self):
        self._rst.end()
        self._rst.submit(self._rnd)

        self._rst.begin()

    def run(self):
        self._rst.end()
        self._rst.submit(self._rnd)

        self._runner.run()


class PanZoom:
    pass


# -------------------------------------------------------------------------------------------------
# Entry-point
# -------------------------------------------------------------------------------------------------

def main():

    # instantiate a Datoviz renderer
    r = Renderer()

    # enqueue a canvas creation request, and return a handle
    c = r.canvas(800, 600)
    # r.flush()

    # create a visual
    v = c.visual('point')

    # create a pos N*3 array
    N = 1000
    pos = r.array((N, 3), dtype=np.float32)
    color = r.array((N, 4), dtype=np.uint8)
    size = r.array((N, 1), dtype=np.float32)

    # upload the data to the array
    pos[:] = np.random.normal(size=(N, 3), loc=0, scale=.25)
    color[:] = np.random.randint(size=(N, 4), low=128, high=255)
    size[:] = 10

    # assign the props to the array
    v['pos'] = pos
    v['color'] = color
    v['size'] = size

    # if number of items = number of groups, update the groups
    # if number of items = number of points, update the points
    # if number of items = 1, update everything (uniform)

    # v.assign(pos=pos, transforms=[...])

    # panzoom transform
    tr = PanZoom()

    # draw a list of visuals in a given viewport
    # by default, use the full viewport

    # TODO: add Viewport object instead
    # TODO: add collection to the protocol?
    # TODO: beter separation between client and server in datoviz, better API
    c.draw([v], transforms=[tr], viewport='full')

    # start the Datoviz event loop, which will process all pending requests
    r.run()


if __name__ == '__main__':
    main()
