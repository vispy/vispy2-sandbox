# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked

class Canvas(Object):

    @typechecked
    @command("")
    def __init__(self, width :     int, 
                       height :    int,
                       dpi :       Union[int,float],
                       dpr :       Union[int,float],
                       offscreen : bool):
        Object.__init__(self)
        self.width = width
        self.height = height
        self.dpi = dpi
        self.dpr = dpr
        self.offscreen = offscreen

    @typechecked        
    @command("set_size")
    def set_size(self, width :  int, 
                       height : int):
        self.width = width
        self.height = height

    @typechecked        
    @command("set_dpi")
    def set_dpi(self, dpi : Union[int,float]) :
        self.dpi = dpi

    @typechecked
    @command("set_dpr")
    def set_dpr(self, dpr : Union[int,float]) :
        self.dpr = dpr

    def __repr__(self):
        return f"Canvas [id={self.id}]: {self.width},{self.height},{self.dpi},{self.dpr}"
