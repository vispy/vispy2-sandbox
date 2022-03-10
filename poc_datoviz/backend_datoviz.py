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
YAML_PATH = ROOT_DIR / 'research/example_scatter.yaml'


# -------------------------------------------------------------------------------------------------
# Commands
# -------------------------------------------------------------------------------------------------

class Command:
    def __init__(self, name, object_type, object_id, **kwargs):
        self.name = name
        self.object_type = object_type
        self.object_id = object_id
        self.parameters = kwargs

    def __str__(self):
        """ Debug representation """
        return f"{self.name.upper()} [{self.object_type} {self.object_id}]"

    def yaml(self):
        """YAML representation."""
        s = ""
        s += f"- {self.name}:\n"
        s += f"    object_type: \"{self.object_type}\"\n"
        s += f"    object_id: \"{self.object_id}\"\n"
        s += f"    parameters: "
        if len(self.parameters):
            s += "\n"
            for key, value in self.parameters.items():
                s += f"      {key}: {value}\n"
        else:
            s += "{}\n"
        s += "\n"
        return s


# -------------------------------------------------------------------------------------------------
# Router
# -------------------------------------------------------------------------------------------------

class Renderer:
    _ids = None
    _arrays = {}
    _props = {}

    def __init__(self):
        self._ids = {}
        self._rnd = dvz.Renderer()
        self._rst = dvz.Requester()

        self._router = {
            ('create', 'canvas'): self.create_canvas,
            ('create', 'visual'): self.create_visual,
            ('create', 'array'): self.create_array,
            ('update', 'array'): self.update_array,
            ('update', 'prop'): self.update_prop,
            ('update', 'visual'): self.update_visual,
            ('begin_draw', 'canvas'): self.begin_draw_canvas,
            ('draw', 'canvas'): self.draw_canvas,
            ('end_draw', 'canvas'): self.end_draw_canvas,
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
        visual_id = self._id(cmd.id)
        canvas_id = self._id(cmd.parameters.canvas_id)
        visual_type = _VISUAL_TYPES.get(cmd.parameters.type)
        assert visual_type

        self._rst.create_graphics(
            canvas_id, visual_type, id=visual_id, flags=3)

        # HACK
        self._rst.create_dat(2, 3*(4*4+4*1+1*4), id=100, flags=0)
        self._rst.set_vertex(visual_id, 100)

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
        data = cmd.parameters.data
        arr[:] = data

    def update_prop(self, cmd):
        # Set up a link between a prop and an array.
        visual_id = cmd.id
        prop = cmd.parameters.prop
        array_id = cmd.parameters.array_id
        offset = cmd.parameters.offset
        shape = cmd.parameters.shape
        self._props[visual_id, prop] = (array_id, offset, shape)

    def update_visual(self, cmd):
        # Update the visual's data from the props.

        # HACK: construct the full vertex buffer array with the props
        dtypes = [(name, dtype)
                  for (name, (_, dtype)) in self._arrays.items()]
        n = max(arr.shape[0] for arr, _ in self._arrays.values())
        out = np.empty(n, dtype=dtypes)
        for (name, (arr, _)) in self._arrays.items():
            out[name] = arr.squeeze()

        # HACK: upload.
        self._rst.upload_dat(100, 0, out)

    def begin_draw_canvas(self, cmd):
        canvas_id = self._id(cmd.id)

        # Begin the draw instructions.
        self._rst.record_begin(canvas_id),

    def draw_canvas(self, cmd):
        # Add a draw instruction.
        canvas_id = self._id(cmd.id)

        # Viewport.
        self._rst.record_viewport(canvas_id, *cmd.parameters.viewport)

        # Draw the visuals.
        for vid in cmd.parameters.visuals:
            # HACK TODO: first_vertex and vertex_count
            self._rst.record_draw(canvas_id, self._id(vid), 0, 3)

    def end_draw_canvas(self, cmd):
        canvas_id = self._id(cmd.id)

        # End the draw instructions.
        self._rst.record_end(canvas_id),

    def run_commands(self, cmds):
        do_render = None
        with self._rst.requests():
            for cmd in cmds:
                b = bunchify(cmd)
                name = list(b.keys())[0]
                if name == 'render':
                    do_render = b[name].id
                    continue
                tp = b[name].type
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
    with open('out.png', 'wb') as f:
        f.write(buf)
