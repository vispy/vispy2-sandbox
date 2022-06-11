# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from typing import Union
from GSP import Object, command
from typeguard import typechecked


class Array(Object):

    # Authorized types for class attributes
    types = { "id" : (int,),
              "shape": (list, tuple,),
              "dtype": (str,) }

    @typechecked
    @command("")
    def __init__(self, shape : Union[list,tuple],
                 dtype :       str):
        Object.__init__(self)
        self.shape = shape
        self.dtype = dtype

    @typechecked
    @command("set_data", encode=["data"])
    def set_data(self, offset : int,
                       data   : Union[list,tuple] ):
        pass

if __name__ == '__main__':
    import GSP

    GSP.mode("client")
    array = Array( [3,3], "uint32")
    array.set_data(0, [1,2,3])
    
