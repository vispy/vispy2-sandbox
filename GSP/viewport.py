# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from GSP import Object, command
    
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
