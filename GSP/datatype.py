# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked

class Datatype(Object):

    @classmethod
    def from_numpy(cls, dtype):
        datatype = ""
        dtype = str(dtype)
        if dtype.startswith("["):
            for item in eval(dtype):
                iname, itype, isize = item
                isize = np.prod(isize)
                datatype += "%s:%s:%d;" % (itype,iname,isize)
        elif dtype.startswith("("):
            itype, isize = eval(dtype)
            isize = np.prod(isize)
            datatype += "%s::%d;" % (itype,isize)
        else:
            datatype += "%s;" % (dtype)
        return datatype


    @classmethod
    def to_numpy(cls, datatype):
        dtype = []
        for item in datatype.split(";"):
            item = item.split(":")
            if len(item) == 3:
                itype, iname, isize = item
                if not len(iname):
                    dtype.append((itype, (int(isize),)))
                else:
                    dtype.append((iname, itype, (int(isize),)))
            elif len(item) == 2:
                itype, iname = item
                dtype.append((iname, itype, (1,)))
            elif len(item) == 1:
                itype = item[0]
                dtype.append((itype, (1,)))
        if len(dtype) == 1:
            dtype = dtype[0]
            if len(dtype) == 3: 
                return dtype[1:]
            else:
                return dtype
        else:
            return dtype
    
    @typechecked
    @command("")
    def __init__(self, datatype : str):
        Object.__init__(self)
        self.datatype = datatype
  
if __name__ == "__main__":

    # datatype description = "item_type:[name:[item_count]]; ..."
    datatypes = { "rgb":  Datatype("u1:r; u1:g; u1:b"),
                  "rgba": Datatype("u1:r; u1:g; u1:b; u1:a"),
                  "argb": Datatype("u1:a, u1:r; u1:g; u1:b;"),
              
                  "rgb(f)":  Datatype("f4:r; f4:g; f4:b"),
                  "rgba(f)": Datatype("f4:r; f4:g; f4:b; f4:a"),
                  "argb(f)": Datatype("f4:a, f4:r; f4:g; f4:b;"),

                  "ivec2": Datatype("i4:2"),
                  "ivec3": Datatype("i4:3"),
                  "ivec4": Datatype("i4:4"),

                  "vec2": Datatype("f4:2"),
                  "vec3": Datatype("f4:3"),
                  "vec4": Datatype("f4:4"),
                  
                  "xy":   Datatype("f4:x; f4:y"),
                  "xyz":  Datatype("f4:x; f4:y; f4:z"),
                  "xyzw": Datatype("f4:x; f4:y; f4:z; f4:w"),

                  "mat2x2": Datatype("f4::4"),
                  "mat3x3": Datatype("f4::9"),
                  "mat4x4": Datatype("f4::16") }

