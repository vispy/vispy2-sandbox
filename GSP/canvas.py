# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from GSP import Object, command

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
