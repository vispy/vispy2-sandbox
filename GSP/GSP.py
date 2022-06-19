# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import yaml
import base64
import itertools
import numpy as np
from datetime import datetime
from functools import wraps


def command(method=None, record=None, output=None):
    """Function decorator that create a command and optionally record it and write it
    to stdout. """

    def wrapper(func):

        @wraps(func)
        def inner(self, *args, **kwargs):
            keys = func.__code__.co_varnames[1:]
            values = args
            
            func(self, *args, **kwargs)

            # Create command
            parameters = {"id": self.id}
            for key, value in zip(keys,values):
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


class CID(yaml.YAMLObject):
    """ Command identifier """
    
    yaml_tag = "!CID"
    yaml_loader = yaml.SafeLoader
    counter = itertools.count()

    def __init__(self, id=None):
        if id is None:
            self.id = 1 + next(CID.counter)
        else:
            self.id = int(id)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __repr__(self):
        return "%d" % self.id

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.id}'.format(node))

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)

class OID(yaml.YAMLObject):
    """ Object identifier """
    
    yaml_tag = "!OID"
    yaml_loader = yaml.SafeLoader
    counter = itertools.count()

    def __init__(self, id=None):
        if id is None:
            self.id = 1 + next(OID.counter)
        else:
            self.id = int(id)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __repr__(self):
        return "%d" % self.id

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.id}'.format(node))

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)

    
class Object:

    record = True
    objects = {}

    def __init__(self):
        self.id = OID()
        if Object.record:
            Object.objects[self.id] = self

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        keys = list(vars(self).keys())
        keys.remove("id")
        for key in keys:
            if getattr(self, key) != getattr(other, key):
                return False
        return True

class Command:

    record = True
    output = True
    commands = []

    # Convenience method, not part of the protocol
    @classmethod
    def equal(cls, commands1, commands2):
        """ Test two sets of commands for equality"""
        
        l1 = list(commands1.values())
        l2 = list(commands2.values())
        try:
            for item in l1:
                l2.remove(item)
        except ValueError:
            return False
        return not l2
    
    @classmethod
    def write(cls, self, method, parameters):
        """ Dump the given method and paramters as a yaml block. """
        
        command_id = CID()
        timestamp = datetime.timestamp( datetime.now())

        # Replace objects by their id
        for key, value in parameters.items():
            if isinstance(value, Object):
                parameters[key] = value.id
        
        data = [ { "method" : method,
                   "id" : command_id,
                   "timestamp" : timestamp,
                   "parameters" : parameters } ]
        return yaml.dump(data, default_flow_style=None, sort_keys=False)

    @classmethod
    def process(cls, command, globals=None, locals=None):
        """ Process a yaml command and create or update the corresponding object. """
        
        data = yaml.safe_load(command)[0]
        try:
            classname, method = data["method"].split("/")
        except ValueError:
            classname, method = data["method"], None
        parameters = data["parameters"]
        object_id = parameters["id"]
        del parameters["id"]

        # Resolve objects references
        for key, value in parameters.items():
            if isinstance(value, OID):
                parameters[key] = Object.objects[value]

        if method is None:
            object = globals[classname](**parameters)
            object.id = object_id
            Object.objects[object_id] = object
        else:
            getattr(globals[classname], method)(Object.objects[object_id], **parameters)


def mode(mode="server", reset=True, record=None, output=None):
    "Set protocol in specified mode (server or client)."

    if reset:
        Object.objects = {}
    if mode == "client":
        Command.record = record if record is not None else True
        Command.output = output if output is not None else True
        Object.record = True
    else:
        Command.record = record if record is not None else False
        Command.output = output if output is not None else False
        Object.record = False

def objects():
    return Object.objects

def commands():
    return Command.commands

def process(command, globals=None, locals=None):
    Command.process(command, globals, locals)
