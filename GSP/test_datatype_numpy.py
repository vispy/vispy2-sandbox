# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import GSP
import numpy as np
from datatype import Datatype

if __name__ == '__main__':

    GSP.mode("client", reset=True, record=False, output=False)
    datatypes = {
        "rgb":  Datatype("u1:r:1;u1:g:1;u1:b:1;"),
        "rgba": Datatype("u1:r:1;u1:g:1;u1:b:1;u1:a:1;"),
        "argb": Datatype("u1:a:1;u1:r:1;u1:g:1;u1:b:1;"),
        
        "rgb(f)":  Datatype("f4:r:1;f4:g:1;f4:b:1;"),
        "rgba(f)": Datatype("f4:r:1;f4:g:1;f4:b:1;f4:a:1;"),
        "argb(f)": Datatype("f4:a:1;f4:r:1;f4:g:1;f4:b:1;"),

        "ivec2": Datatype("i4::2;"),
        "ivec3": Datatype("i4::3;"),
        "ivec4": Datatype("i4::4;"),

        "vec2": Datatype("f4::2;"),
        "vec3": Datatype("f4::3;"),
        "vec4": Datatype("f4::4;"),
                  
        "xy":   Datatype("f4:x:1;f4:y:1;"),
        "xyz":  Datatype("f4:x:1;f4:y:1;f4:z:1;"),
        "xyzw": Datatype("f4:x:1;f4:y:1;f4:z:1;f4:w:1;"),

        "mat2x2": Datatype("f4::4;"),
        "mat3x3": Datatype("f4::9;"),
        "mat4x4": Datatype("f4::16;") }

    for key in datatypes.keys():
        d1 = datatypes[key].datatype
        d2 = Datatype.from_numpy(Datatype.to_numpy(d1))
        print(f"{key:7}: {d1==d2}")
