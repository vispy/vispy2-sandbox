# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked
from transform import Transform

class TransformMatrix(Transform):

    @typechecked
    @command("")
    def __init__(self, data  : bytes):
        Transform.__init__(self)
        self.dtype = "f4"
        self.data = data
        self._array = np.frombuffer(data, dtype=self.dtype).copy()

    @typechecked
    @command("set_data")
    def set_data(self, data: bytes ):
        data = np.frombuffer(data, dtype=self._array.dtype)
        self._array.ravel()[:] = data

    def __repr__(self):
        return f"Transform[Matrix] [id={self.id}]: {self.dtype}, {self._array}"
        
    def __eq__(self, other):
        for key in ("dtype",):
            if getattr(self, key) != getattr(other, key):
                return False
        if not np.array_equal(self._array, other._array):
            return False
        return True
    
    
