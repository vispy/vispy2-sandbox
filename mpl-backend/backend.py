# Reference implementation for the Vispy 2 rendering protocol
# Backend prototype
import re
import io
import yaml
import matplotlib
import numpy as np
matplotlib.use('agg')
import matplotlib.pyplot as plt

class Framebuffer:
    def __init__(self, width, height, ratio=1, dpi=100):
        self.width = width
        self.height = height
        self.ratio = ratio
        self.dpi = dpi
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

    def point(self, viewport, x, y, color):
        dpi = viewport.framebuffer.figure.dpi
        size = (72/dpi)**2
        viewport.axes.scatter([x],
                              [y],
                              s=size,
                              color=color,
                              antialiased=True)

    def segment(self, viewport, x0, y0, x1, y1, color):
        dpi = viewport.framebuffer.figure.dpi
        viewport.axes.plot([x0, x1],
                           [y0, y1],
                           color = color,
                           linewidth = 72/dpi,
                           # antialiased = False,
                           snap=True)


# -----------------------------------------------------------------------------
def parse(filename):

    # Read yaml file
    with open(filename, "r") as stream:
        try:
            stack = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Execute commands
    actors = {}
    for item in stack:
        for key, value in item.items():
            actor_id = value["id"]
            params = re.sub(r"('#[0-9]+')", r"actors[\1]",
                            str(value["parameters"]))

            # Create command
            if key == "create":
                atype = value["type"]
                command = "%s(**%s)" % (atype, params)
                actors[actor_id] = eval(command)

            # Execute command
            elif key == "execute":
                action = value["action"]
                command = "actors['%s'].%s(**%s)" % (actor_id, action, params)
                eval(command)

            # Execute command
            elif key == "request":
                action = value["action"]
                command = "actors['%s'].%s(**%s)" % (actor_id, action, params)
                yield eval(command)

        
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    # filename = "single-viewport.yaml"
    # filename = "two-viewports.yaml"
    filename = "four-viewports.yaml"
    
    for output in parse(filename): pass

    matplotlib.use('MacOSX')
    height,width,depth = output.shape
    dpi = 100
    fig = plt.figure(figsize = (width/dpi, height/dpi), dpi=dpi)
    ax = fig.add_axes([0,0,1,1])
    ax.imshow(output)
    ax.set_axis_off()
    plt.show()
