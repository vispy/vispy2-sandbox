# Reference implementation for the Vispy 2 rendering protocol
# Frontend prototype
from matplotlib.figure import Figure
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.backend_bases import FigureManagerBase
from matplotlib.backend_bases import RendererBase
from command import Command

class RendererTemplate(RendererBase):
    def __init__(self, dpi):
        super().__init__()
        self.dpi = dpi
    def draw_path(self, gc, path, transform, rgbFace=None):
        self.figure.commands.append(
            Command(Command.EXECUTE, "#3", "render_path",
                    viewport = '"#2"',
                    vertices = transform.transform_path(path).vertices.tolist(),
                    color=list(rgbFace or gc.get_rgb())))
        
    def draw_markers(self, gc, marker_path, marker_trans, path, trans,
                     rgbFace=None):
        pass
    def draw_path_collection(self, gc, master_transform, paths,
                              all_transforms, offsets, offsetTrans,
                              facecolors, edgecolors, linewidths, linestyles,
                              antialiaseds):
        pass
    def draw_quad_mesh(self, gc, master_transform, meshWidth, meshHeight,
                        coordinates, offsets, offsetTrans, facecolors,
                        antialiased, edgecolors):
        pass
    def draw_image(self, gc, x, y, im):
        pass
    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
        pass
    def flipy(self):
        return True
    def get_canvas_width_height(self):
        return 100, 100
    def get_text_width_height_descent(self, s, prop, ismath):
        return 1, 1, 1
    def points_to_pixels(self, points):
        return points/72.0 * self.dpi

class FigureCanvasTemplate(FigureCanvasBase):
    def draw(self):
        renderer = RendererTemplate(self.figure.dpi)
        renderer.figure = self.figure
        self.figure.commands.append(
            Command(Command.CREATE, "#3", "Renderer"))
        self.figure.draw(renderer)
        
    def print_yaml(self, filename, **kwargs):
        self.draw()
        self.figure.commands.append(
            Command(Command.REQUEST, "#1", "render", format = '"raw"'))
        
        with open(filename, "w") as file: 
            for command in self.figure.commands:
                file.write(command.yaml())

class FigureManagerTemplate(FigureManagerBase):
    pass
def new_figure_manager(num, *args, FigureClass=Figure, **kwargs):
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)
def new_figure_manager_given_figure(num, figure):
    dpi = figure.dpi
    width, height = figure.get_size_inches()
    figure.commands = [
        Command(Command.CREATE, "#1", "Framebuffer",
                width=int(width*dpi),
                height=int(height*dpi),
                ratio=1,
                dpi=figure.dpi),
        Command(Command.CREATE, "#2", "Viewport",
                framebuffer = '"#1"',
                extent = [0, 0, int(width*dpi), int(height*dpi)],
                depth = 0)]
    canvas = FigureCanvasTemplate(figure)
    manager = FigureManagerTemplate(canvas, num)
    return manager

