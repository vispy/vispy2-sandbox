# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked
from canvas import Canvas

class Viewport(Object):

    @typechecked
    @command("")
    def __init__(self, canvas : Canvas,
                       x :      Union[int,float],
                       y :      Union[int,float],
                       width :  Union[int,float],
                       height : Union[int,float]):
        Object.__init__(self)
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @typechecked
    @command("set_position")
    def set_position(self, x : Union[int,float],
                           y : Union[int,float]):
        self.x = x
        self.y = y

    @typechecked
    @command("set_size")
    def set_size(self, width :  Union[int,float],
                       height : Union[int,float]):
        self.width = width
        self.height = height
        
    def __repr__(self):
        return f"Viewport [id={self.id}]: {self.x},{self.y},{self.width},{self.height}"
