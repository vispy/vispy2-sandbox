# -------------------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------------------

import io
import logging
from pathlib import Path
from pprint import pprint
import re
import yaml

import numpy as np
from matplotlib.colors import hsv_to_rgb

import datoviz as dvz


# -------------------------------------------------------------------------------------------------
# Logger
# -------------------------------------------------------------------------------------------------

logger = logging.getLogger('datoviz')


# -------------------------------------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------------------------------------

class Bunch(dict):
    def __init__(self, *args, **kwargs):
        self.__dict__ = self
        super().__init__(*args, **kwargs)


def bunchify(c):
    if isinstance(c, dict):
        c = Bunch(c)
    for k, v in c.items():
        if isinstance(v, dict):
            c[k] = bunchify(v)
    return c


def load_yaml(filename):
    with open(filename, "r") as stream:
        try:
            contents = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return contents


def parse_color(bgcolor):
    # TODO
    return (10, 10, 10)


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

ROOT_DIR = Path(__file__).parent / '../'
YAML_PATH = ROOT_DIR / 'research/example_transforms.yaml'
VERTEX_DAT_ID = 100


# -------------------------------------------------------------------------------------------------
# Router
# -------------------------------------------------------------------------------------------------

def to_uint8(arr):
    arr = np.clip(arr, 0, 1)
    return np.round(255 * arr).astype(np.uint8)

class Renderer:
    _ids = None
    _visuals = {}
    _arrays = {}
    _props = {}
    _transforms = {}

    def __init__(self):
        self._ids = {}
        self._rnd = dvz.Renderer()
        self._rst = dvz.Requester()

        self._router = {
            ('create', 'canvas'): self.create_canvas,
            ('create', 'visual'): self.create_visual,
            ('create', 'array'): self.create_array,
            ('update', 'array'): self.update_array,
            ('create', 'transform'): self.create_transform,
            ('update', 'prop'): self.update_prop,
            ('draw', 'canvas'): self.draw_canvas,
        }

    def _id(self, s):
        if s not in self._ids:
            self._ids[s] = len(self._ids) + 1
        assert s in self._ids
        return self._ids[s]

    def create_canvas(self, cmd):
        w = cmd.parameters.width
        h = cmd.parameters.height
        id = self._id(cmd.id)
        background = parse_color(cmd.parameters.bgcolor)
        flags = 0
        self._rst.create_board(w, h, id=id, background=background, flags=flags)

    def create_visual(self, cmd):
        p = cmd.parameters
        self._visuals[cmd.id] = p

        visual_id = self._id(cmd.id)
        canvas_id = self._id(p.canvas_id)
        visual_type = _VISUAL_TYPES.get(p.type)
        assert visual_type

        self._rst.create_graphics(
            canvas_id, visual_type, id=visual_id, flags=3)

        # Create the visual-specific vertex buffer
        if p.type == 'point':
            self._rst.create_dat(2, 3*(4*4+4*1+1*4), id=VERTEX_DAT_ID, flags=0)
            self._rst.set_vertex(visual_id, VERTEX_DAT_ID)

    # Arrays

    def create_array(self, cmd):
        array_id = cmd.id
        ndim = cmd.parameters.ndim
        shape = cmd.parameters.shape
        dtype = cmd.parameters.dtype
        dtype = _DTYPES[dtype] if dtype in _DTYPES else np.dtype(dtype)
        arr = np.zeros(shape, dtype=dtype)
        if arr.ndim == 1:
            arr = arr[:, np.newaxis]
        self._arrays[array_id] = (arr, dtype)

    def update_array(self, cmd):
        # Update data in an array.
        array_id = cmd.id
        arr, _ = self._arrays[array_id]
        p = cmd.parameters

        if p.type == 'direct':
            data = np.asarray(p.data)
        elif p.type == 'custom_linspace':
            data = np.linspace(p.range[0], p.range[1], p.count)
        elif p.type == 'line':
            data = np.c_[np.linspace(p.x[0], p.x[1], p.count), np.full(
                p.count, p.y), np.full(p.count, p.z)]
        else:
            raise ValueError(f"unknown data request type '{p.type}'")

        # Reshape the array if needed.
        if data.shape[0] > arr.shape[0]:
            arr = np.resize(arr, (data.shape[0],) + arr.shape[1:])
            self._arrays[array_id] = (arr, arr.dtype)

        if data.ndim == 1:
            data = data[:, np.newaxis]
        arr[:] = data

    # Transforms

    def create_transform(self, cmd):
        p = cmd.parameters
        self._transforms[cmd.id] = p

    # Props

    def update_prop(self, cmd):
        # Set up a link between a prop and an array.
        visual_id = cmd.id
        p = cmd.parameters
        prop = p.prop
        self._props[visual_id, prop] = p

    def _apply_transform(self, tr, arr):
        if tr.type == 'custom_sine':
            arr[:, 1] = tr.amplitude * np.sin(2*np.pi*tr.frequency*(arr[:, 0]-tr.phase))
            return arr
        elif tr.type == 'colormap':
            arr_n = (arr - arr.min()) / (arr.max() - arr.min())
            n = len(arr_n)
            rgb = hsv_to_rgb(np.c_[arr_n, np.ones(n), np.ones(n)])
            return np.c_[to_uint8(rgb), np.full(n, 255)]
        else:
            return ValueError(f"unknown transform '{tr.type}'")

    def _apply_transforms(self, trids, arr):
        for trid in trids:
            tr = self._transforms[trid]
            arr = self._apply_transform(tr, arr)
        return arr

    def _get_vertex(self, visual_id):
        if self._visuals[visual_id].type == 'point':
            # Return the vertex data from the props
            pos = self._props[visual_id, 'pos']
            color = self._props[visual_id, 'color']
            size = self._props[visual_id, 'size']

            pos_arr = self._arrays[pos.array_id][0]
            color_arr = self._arrays[color.array_id][0]
            size_arr = self._arrays[size.array_id][0]

            # TODO: take offset and shape into account

            # Apply transforms to props.
            pos_arr = self._apply_transforms(pos.transforms, pos_arr)
            color_arr = self._apply_transforms(color.transforms, color_arr)
            size_arr = self._apply_transforms(size.transforms, size_arr)

            # Create the vbo.
            n = pos_arr.shape[0]
            vbo = np.empty(
                n, dtype=[('pos', 'float32', (3,)), ('color', 'uint8', (4,)), ('size', 'float32')])

            # Set the transform props to the vbo.
            vbo['pos'] = pos_arr
            vbo['color'] = color_arr
            vbo['size'] = size_arr

            return vbo

    # Drawing

    def draw_canvas(self, cmd):
        # Add a draw instruction.
        canvas_id = self._id(cmd.id)

        # Begin.
        self._rst.record_begin(canvas_id)

        # Viewport.
        self._rst.record_viewport(canvas_id, *cmd.parameters.viewport)

        # Draw the visuals.
        for vid in cmd.parameters.visuals:

            # Compute the VBO from the props, arrays, transforms, and upload it
            vbo = self._get_vertex(vid)
            self._rst.upload_dat(VERTEX_DAT_ID, 0, vbo)

            # Record the draw command.
            self._rst.record_draw(canvas_id, self._id(vid), 0, vbo.size)

        # End
        self._rst.record_end(canvas_id)

    # Rendering

    def run_commands(self, cmds):
        do_render = None
        with self._rst.requests():
            for cmd in cmds:
                b = bunchify(cmd)
                name = list(b.keys())[0]
                if name == 'render':
                    do_render = b[name].id
                    continue
                tp = b[name].object
                fn = self._router.get((name, tp), None)
                if not fn:
                    logger.error(f"Unknown command {(name, tp)}")
                    continue
                assert fn
                out = fn(b[name])

        self._rst.submit(self._rnd)

        if do_render is not None:
            return self.get_image(do_render)

    def get_image(self, id):
        board_id = self._id(id)
        # Trigger a redraw.
        with self._rst.requests():
            self._rst.update_board(board_id)
        self._rst.submit(self._rnd)

        # Get the image.
        img = self._rnd.get_png(board_id)

        # Return as PNG
        output = io.BytesIO(img)
        return output


if __name__ == '__main__':
    cmds = load_yaml(YAML_PATH)

    r = Renderer()
    img = r.run_commands(cmds)
    buf = img.getvalue()
    with open('out2.png', 'wb') as f:
        f.write(buf)
