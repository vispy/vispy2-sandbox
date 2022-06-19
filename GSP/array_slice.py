# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked
from array import Array

class ArraySlice(Object):

    @typechecked
    @command("")
    def __init__(self, array : Array,
                       start : int
                       stop : int):
        Object.__init__(self)
        self.array = array
        self.start = start
        self.stop = stop
    
    def __repr__(self):
        return f'ArraySlice [id={self.id}]: Array[id={self.array.id}]["{self.start}:{self.stop}"]'

