# Reference implementation for the Vispy 2 rendering protocol
# Backend prototype
import re
import io
import yaml
import matplotlib
import numpy as np
matplotlib.use('agg')
import matplotlib.pyplot as plt
from command import Command


class Framebuffer:
    def __init__(self, width, height, ratio=1, dpi=100):
        self.width = width
        self.height = height
        self.ratio = ratio
        self.dpi = dpi
        plt.autoscale(False)
        self.figure = plt.figure(frameon=False,
                                 dpi=self.dpi)
        self.figure.set_size_inches(self.ratio * self.width / self.dpi,
                                    self.ratio * self.height /self.dpi)
        
    def render(self, format):
        self.figure.canvas.draw()
        with io.BytesIO() as output:
            self.figure.savefig(output, format='raw')
            output.seek(0)
            data = np.frombuffer(output.getvalue(), dtype=np.uint8)
        return data.reshape(self.ratio * self.height,
                            self.ratio * self.width,
                            -1)


class Viewport:
    def __init__(self, framebuffer, extent, depth):
        self.framebuffer = framebuffer
        self.extent = extent
        self.depth = depth
        x, y, width, height = self.extent
        self.axes = framebuffer.figure.add_axes([x / framebuffer.width,
                                                 y / framebuffer.height,
                                                 width / framebuffer.width,   
                                                 height / framebuffer.height])
        self.axes.set_xlim(0, width)
        self.axes.set_ylim(0, height)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.axes.zorder = depth 
        for position in ["top", "bottom", "left", "right"]:
            self.axes.spines[position].set_visible(False)
            
    
class Renderer:
    def __init__(self):
        pass
        
    def clear(self, viewport, color):
        viewport.axes.set_facecolor(color)

    # def point(self, viewport, x, y, color):
    #     dpi = viewport.framebuffer.figure.dpi
    #     size = (72/dpi)**2
    #     viewport.axes.scatter([x],
    #                           [y],
    #                           s=size,
    #                           color=color,
    #                           antialiased=True,
    #                           snap=True)

    def render_path(self, viewport, vertices, color):
        dpi = viewport.framebuffer.figure.dpi
        vertices = np.array(vertices)
        viewport.axes.plot(vertices[:,0], vertices[:,1], color=color)


def parse(filename):
    # Read yaml file
    with open(filename, "r") as stream:
        try:
            commands = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Execute commands
    objects = {}
    for command in commands:
        (name, content), *rest = command.items()
        command = Command(name,
                          content["object"],
                          content["method"],
                          **content["parameters"])
        result = eval(command.call("objects"))
        if name == Command.CREATE:
            objects[content["object"]] = result
        if name == Command.REQUEST:
            yield result
