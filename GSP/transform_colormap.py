# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked
from array import Array
from transform import Transform

class TransformColormap(Transform):

    @typechecked
    @command("")
    def __init__(self, values : Array,
                       colormap : str):
        Transform.__init__(self)
        self.values = values
        self.colormap = colormap

    def __repr__(self):
        return f"Transform[Colormap] [id={self.id}]: {self.colormap}({self.values.id})"
        

    
    
