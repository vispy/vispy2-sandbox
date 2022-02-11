import asyncio

import wgpu
import wgpu.backends.rs
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
import numpy as np

import json
import yaml
import toml


# todo: props like color


class CommandParser:
    def __init__(self):

        self._canvases = {}
        self._idmap = {}
        self._command_count = 0

    def request_draw():
        for canvas in self._canvases.values():
            canvas.request_draw()

    def push(self, command):
        """Push a command."""
        if not isinstance(command, dict):
            raise TypeError("Command should be a dict.")

        self._command_count += 1

        # Parse the command
        action = command["action"]
        id = command["id"]
        command_id = command.get("cmd_id", self._command_count + 1)

        # New objects need new id's
        if action.startswith("create"):
            if id in self._idmap:
                raise ValueError(f"Given id for {action} already in use.")

        if action == "create_canvas":
            size = command["width"], command["height"]
            canvas = WgpuCanvas(size=size)
            canvas.scene = gfx.Scene()
            self._idmap[id] = canvas
            self._canvases[id] = canvas
            loop = asyncio.get_event_loop()  # get_running_loop()
            loop.call_later(0.01, show, canvas, canvas.scene)

        elif action == "create_node":
            node = gfx.Group()
            self._idmap[id] = node
            parent = self._lookup(
                command, "parent", (wgpu.gui.WgpuCanvasBase, gfx.WorldObject)
            )
            if isinstance(parent, wgpu.gui.WgpuCanvasBase):
                parent.scene.add(node)
            else:
                parent.add(node)

        elif action == "create_buffer":
            array = arrray_from_size_and_format(command["size"], command["format"])
            self._idmap[id] = gfx.Buffer(array)

        elif action == "upload_buffer":
            buffer = self._lookup(command, "id", gfx.Buffer)
            new_array = np.asanyarray(command["data"])
            i1 = command["offset"]
            i2 = i1 + len(new_array)
            buffer.data[i1:i2] = new_array
            buffer.update_range(i1, i2 - i1)

        elif action == "create_visual":
            type = command["type"]
            node = self._lookup(command, "node", gfx.WorldObject)
            if type == "points":
                positions = self._lookup(command, "positions", gfx.Buffer)
                ob = gfx.Points(
                    gfx.Geometry(positions=positions),
                    gfx.PointsMaterial(size=10, color="green"),
                )
            elif type == "line":
                positions = self._lookup(command, "positions", gfx.Buffer)
                ob = gfx.Line(
                    gfx.Geometry(positions=positions),
                    gfx.LineMaterial(thickness=10, color="green"),
                )
            else:
                raise ValueError(f"Unknown visual type '{type}'.")
            self._idmap[id] = ob
            node.add(ob)

        else:
            raise ValueError(f"Unknown action {action}")

    def _lookup(self, command, key, cls):
        try:
            id = command[key]
        except KeyError:
            msg = f"Command with action '{command['action']}' is missing key '{key}'"
            raise ValueError(msg) from None
        try:
            ob = self._idmap[id]
        except KeyError:
            msg = f"Command with action '{command['action']}' has '{key}' that is not a known id."
            raise ValueError(msg) from None
        if cls and not isinstance(ob, cls):
            obtype = ob.__class__.__name__
            if isinstance(cls, tuple):
                reftype = " or ".join(x.__name__ for x in cls)
            else:
                reftype = cls.__name
            msg = f"Command with action '{command['action']}' has '{key}' that is a {obtype}, not a {reftype}."
            raise ValueError(msg)
        return ob


## Utils


def show(canvas, scene, up=None):

    bb = scene.get_world_bounding_box()  # 2x3
    size = bb[1] - bb[0]
    center = bb[0] + 0.5 * size

    camera = gfx.OrthographicCamera(2, 2)  # size[0], size[1])
    camera.position.from_array(center)
    # camera = gfx.PerspectiveCamera(70, 16 / 9)
    # look_at = camera.show_object(scene)
    canvas.camera = camera

    renderer = gfx.renderers.WgpuRenderer(canvas)

    # controls = gfx.OrbitControls(camera.position.clone(), look_at, up=up)
    # controls = gfx.PanZoomControls(camera.position.clone())
    # controls.add_default_event_handlers(canvas, camera)

    def animate():
        # controls.update_camera(camera)
        renderer.render(scene, camera)

    canvas.request_draw(animate)


def arrray_from_size_and_format(size, format):
    channels, _, dtype = format.partition("x")
    channels = int(channels or 1)
    return np.zeros((size, channels), dtype)


## Init

cp = CommandParser()

INPUT = "viz.yaml"

with open(INPUT, "rt") as f:
    commands = yaml.load(f, yaml.FullLoader)


async def init():
    for command in commands:
        cp.push(command)


loop = asyncio.get_event_loop()
loop.create_task(init())
run()


with open("viz.json", "wt") as f:
    f.write(json.dumps(commands, indent=4))
with open("viz.toml", "wt") as f:
    f.write(toml.dumps({"command": commands}))

if False:
    ## Interactively change the data

    command = {
        "action": "upload_buffer",
        "id": 3,
        "offset": 1,
        "data": [[0.5, 0.5, 0]],
    }
    cp.push(command)
    cp.request_draw()
