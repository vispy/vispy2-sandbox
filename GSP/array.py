# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked

class Array(Object):

    # Convenience method, not part of the protocol
    @classmethod
    def from_numpy(cls, Z):
        if (isinstance(Z, np.ndarray)):
            return Array(list(Z.shape), Z.dtype.str, Z.tobytes())
        raise ValueError(f"Unknown type for {Z}, cannot convert to Array")

    # Convenience method, not part of the protocol
    @classmethod
    def to_numpy_dtype(cls, dtype):
        import re
        
        dtypes = { "int8" : "i1", "int16" : "i2",  "int32" : "i4",
                   "uint8" : "u1", "uint16" : "u2",  "uint32" : "u4",
                   "float32" : "f4",

                   "ivec2" : [("x", "i4"), ("y", "i4")],
                   "ivec3" : [("x", "i4"), ("y", "i4"), ("z", "i4")],
                   "ivec4" : [("x", "i4"), ("y", "i4"), ("z", "i4"), ("w", "i4")],

                   "vec2" : [("x", "f4"), ("y", "f4")],
                   "vec3" : [("x", "f4"), ("y", "f4"), ("z", "f4")],
                   "vec4" : [("x", "f4"), ("y", "f4"), ("z", "f4"), ("w", "f4")],

                   "mat2x2" : ("f4", (2,2)),
                   "mat3x3" : ("f4", (3,3)),
                   "mat4x4" : ("f4", (4,4)) }

        if dtype in dtypes.keys():
            return dtypes[dtype]
        elif dtype.startswith("ivec"):
            names = re.search("ivec\[(.+)\]", dtype).group(1).split(",")
            return [(name, "i4") for name in names]
        elif dtype.startswith("vec"):
            names = re.search("vec\[(.+)\]", dtype).group(1).split(",")
            return [(name, "f4") for name in names]
        else:
            raise ValueError("Cannot convert {dtpype} to numpy dtype")
                
    
    @typechecked
    @command("")
    def __init__(self, shape : Union[int,list,tuple],
                       dtype : str,
                       data  : bytes):
        Object.__init__(self)
        self.shape = shape
        self.dtype = dtype
        self.data = data
        self._array = np.frombuffer(data, dtype=dtype).reshape(shape).copy()

    @typechecked
    @command("set_data")
    def set_data(self, offset : int,
                       data   : bytes ):
        size = len(data) // self._array.dtype.itemsize
        data = np.frombuffer(data, dtype=self._array.dtype)
        self._array.ravel()[offset:offset+size] = data

    def __repr__(self):
        return f"Array [id={self.id}]: {tuple(self.shape)}, {self.dtype}, {self._array}"
        
    def __eq__(self, other):
        for key in ("shape", "dtype"):
            if getattr(self, key) != getattr(other, key):
                return False
        if not np.array_equal(self._array, other._array):
            return False
        return True
    
    
    
# This is necessary if we want to access a subpart of an array or a specific
# field. For example, if we have an array holding position as xyz, how do we
# access the "x" view if we want to use it for a colormap ? Does this mean we
# need to support structured array ? Or do we consider position / color to be
# very specific cases ?
class ArrayView(Object):

    @typechecked
    @command("")
    def __init__(self, source : Array):
        Object.__init__(self)
        self.source = source
