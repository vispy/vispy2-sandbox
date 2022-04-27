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


# -------------------------------------------------------------------------------------------------
# Visual
# -------------------------------------------------------------------------------------------------

class Visual:
    _id = None
    canvas = None  # canvas
    rd = None

    def __init__(self, parent, vtype):
        self.canvas = parent  # canvas
        self.rd = parent.rd  # renderer
        self._id = self.rd._id()
        assert self._id

        vtype_id = _VISUAL_TYPES.get(vtype)
        assert vtype_id

        self.rd._rst.create_graphics(
            self.canvas._id, vtype_id, id=self._id, flags=3)

        # Create the visual-specific vertex buffer
        if vtype == 'point':
            self.rd._rst.create_dat(
                2, 3*(4*4+4*1+1*4), id=VERTEX_DAT_ID, flags=0)
            self.rd._rst.set_vertex(self._id, VERTEX_DAT_ID)


# -------------------------------------------------------------------------------------------------
# Canvas
# -------------------------------------------------------------------------------------------------

class Canvas:
    _id = None
    rd = None

    def __init__(self, parent, width, height):
        self.rd = parent  # renderer
        self._id = self.rd._id()
        assert self._id

        flags = 0
        self.rd._rst.create_canvas(width, height, id=self._id, flags=flags)

    def visual(self, vtype):
        return Visual(self, vtype)


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
    N = 100
    pos = r.array((N, 3), dtype=np.float32)
    color = r.array((N, 4), dtype=np.uint8)

    # # upload the data to the array
    # pos[:] = np.random.rand(N, 3)
    # color[:] = np.random.randint(size=(N, 4), low=128, high=255)

    # # assign the props to the array
    # v['pos'] = pos
    # v['color'] = color

    # # panzoom transform
    # tr = PanZoom()

    # # draw a list of visuals in a given viewport
    # v.draw([v], transforms=[tr])  # by default, use the full viewport

    # start the Datoviz event loop, which will process all pending requests
    r.run()


if __name__ == '__main__':
    main()
