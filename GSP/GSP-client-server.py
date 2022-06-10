# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference client implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import yaml
import itertools
from datetime import datetime

# -----------------------------------------------------------------------------
def command(method=None, record=None, output=None, check=None):
    """Function decorator that records a new command and optionally checks for
       argument types and write command to stdout."""
    
    def wrapper(func):
        def inner(self, *args, **kwargs):
            keys = func.__code__.co_varnames[1:]
            values = args
            if check or Command.check:
                for key, value in zip(keys, values):
                    if not isinstance(value, self.types[key]):
                        raise TypeError("Wrong type for parameter %s : %s" % (key, type(value)))
                for key, value in kwargs.items():
                    if not isinstance(value, self.types[key]):
                        raise TypeError("Wrong type for parameter %s : %s" % (key, type(value)))

            func(self, *args, **kwargs)

            methodname = func.__code__.co_name if method is None else method
            classname = self.__class__.__name__
            name = "%s/%s" % (classname, methodname) if methodname else classname
            command = Command.write(self, name, *keys)
            if record or Command.record:
                Command.commands.append(command)
            if output or Command.output:
                print(command)
        return inner
    return wrapper



# -----------------------------------------------------------------------------
class Object:

    id_counter = itertools.count()
    record = True
    objects = {}

    def __init__(self):
        self.id = 1 + next(Object.id_counter)
        if Object.record:
            Object.objects[self.id] = self

class Command:

    check = True
    record = True
    output = True
    id_counter = itertools.count()
    commands = []

    @classmethod
    def write(cls, self, method, *args):
        command_id = 1 + next(Command.id_counter)
        timestamp = datetime.timestamp( datetime.now())
        data = [ { "method" : method,
                   "id" : command_id,
                   "timestamp" : timestamp,
                   "parameters" : {key: getattr(self,key)
                                   for key in ["id"] + list(args)}} ]
        return yaml.dump(data, sort_keys=False)

    @classmethod
    def read(cls, command):
        data = yaml.safe_load(command)[0]
        try:
            classname, method = data["method"].split("/")
        except ValueError:
            classname, method = data["method"], None
        parameters = data["parameters"]
        
        if method is None:
            object_id = parameters["id"]
            del parameters["id"]
            object = globals()[classname](**parameters)
            object.id = object_id
            Object.objects[object_id] = object
        else:
            object_id = parameters["id"]
            del parameters["id"]
            getattr(globals()[classname], method)(Object.objects[object_id], **parameters)

        
# -----------------------------------------------------------------------------
class Canvas(Object):

    # Authorized types for class attributes
    types = { "id" : (int,),
              "width": (float, int),
              "height": (float, int),
              "dpi": (float, int),
              "dpr": (float, int) }

    @command("")
    def __init__(self, width, height, dpi, dpr):
        Object.__init__(self)
        self.width = width
        self.height = height
        self.dpi = dpi
        self.dpr = dpr

    @command("set_size")
    def set_size(self, width, height):
        self.width = width
        self.height = height

    @command("set_dpi")
    def set_dpi(self, dpi):
        self.dpi = dpi

    @command("set_dpr")
    def set_dpr(self, dpr):
        self.dpr = dpr

    def __repr__(self):
        return f"Canvas [id={self.id}]: {self.width},{self.height},{self.dpi},{self.dpr}"
    
# -----------------------------------------------------------------------------
class Viewport(Object):

    # Authorized types for class attributes
    types = { "id" : (int,),
              "canvas" : (int,),
              "x": (float, int),
              "y": (float, int),
              "width": (float, int),
              "height": (float, int) }

    @command("")
    def __init__(self, canvas, x, y, width, height):
        Object.__init__(self)
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @command("set_position")
    def set_position(self, x, y):
        self.x = x
        self.y = y

    @command("set_size")
    def set_size(self, width, height):
        self.width = width
        self.height = height
        
    def __repr__(self):
        return f"Viewport [id={self.id}]: {self.x},{self.y},{self.width},{self.height}"
        

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # Create & write commands
    # -----------------------
    Command.check = True
    Command.record = True
    Command.output = True
    Object.record = True
    
    canvas = Canvas(512,512, 100, 1)
    canvas.set_size(500, height=500)
    viewport = Viewport(canvas.id, 0, 0, 512, 512)
    viewport.set_position(0, 0)

    print("Client objects")
    for object in Object.objects.values():
        print("-", object)
    
    # Read & execute commands
    # -----------------------
    Object.objects = {}
    Command.check = False
    Command.record = False
    Command.output = False
    Object.record = False
    
    for command in Command.commands:
        Command.read(command)
    print()
    print("Server objects")
    for object in Object.objects.values():
        print("-", object)

