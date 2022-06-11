# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import yaml
import base64
import itertools
from datetime import datetime

def command(method=None, record=None, output=None, check=None, encode=[]):
    """
    Function decorator that records a new command and optionally checks for
    argument types, reccord the command and write it to stdout.
    """

    def wrapper(func):
        def inner(self, *args, **kwargs):
            keys = func.__code__.co_varnames[1:]
            values = args

            # Check parameter types
            if check or Command.check:
                for key, value in zip(keys, values):
                    if key in self.types.keys() and not isinstance(value, self.types[key]):
                        raise TypeError("Wrong type for parameter %s : %s" % (key, type(value)))
                for key, value in kwargs.items():
                    if key in self.types.keys() and not isinstance(value, self.types[key]):
                        raise TypeError("Wrong type for parameter %s : %s" % (key, type(value)))
            func(self, *args, **kwargs)

            # Create command
            parameters = {"id": self.id}
            for key, value in zip(keys,values):
                if key in encode:
                    parameters[key] = Command.encode(value)
                else:
                    parameters[key] = value
            classname = self.__class__.__name__
            methodname = func.__code__.co_name if method is None else method
            name = "%s/%s" % (classname, methodname) if methodname else classname
            command = Command.write(self, name, parameters)
            if record or Command.record:
                Command.commands.append(command)
            if output or Command.output:
                print(command)
        return inner
    return wrapper

class Object:

    id_counter = itertools.count()
    record = True
    objects = {}

    def __init__(self):
        self.id = 1 + next(Object.id_counter)
        if Object.record:
            Object.objects[self.id] = self

    def __eq__(self, other):
        for key in vars(self).keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True

class Command:

    check = True
    record = True
    output = True
    id_counter = itertools.count()
    commands = []

    @classmethod
    def encode(cls, data):
        return str(base64.b64encode(str(data).encode("utf-8")))
        

    
    @classmethod
    def write(cls, self, method, parameters):
        command_id = 1 + next(Command.id_counter)
        timestamp = datetime.timestamp( datetime.now())
        data = [ { "method" : method,
                   "id" : command_id,
                   "timestamp" : timestamp,
                   "parameters" : parameters } ]
        return yaml.dump(data, sort_keys=False)

    @classmethod
    def process(cls, command, globals=None, locals=None):
        data = yaml.safe_load(command)[0]
        try:
            classname, method = data["method"].split("/")
        except ValueError:
            classname, method = data["method"], None
        parameters = data["parameters"]
        
        if method is None:
            object_id = parameters["id"]
            del parameters["id"]
            object = globals[classname](**parameters)
            object.id = object_id
            Object.objects[object_id] = object
        else:
            object_id = parameters["id"]
            del parameters["id"]
            getattr(globals[classname], method)(Object.objects[object_id], **parameters)


def mode(mode="server", reset=True, record=None, output=None, check=None):
    "Set protocol in specified mode (server or client)."

    if reset:
        Object.objects = {}

    if mode == "client":
        command.check = check if check is not None else True
        Command.record = record if record is not None else True
        Command.output = output if output is not None else True
        Object.record = True
    else:
        command.check = check if check is not None else False
        Command.record = record if record is not None else False
        Command.output = output if output is not None else False
        Object.record = False

def objects():
    return Object.objects

def commands():
    return Command.commands

def process(command, globals=None, locals=None):
    Command.process(command, globals, locals)
