# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from GSP import Object, command
    
class Array(Object):

    # Authorized types for class attributes
    types = { "id" : (int,),
              "shape": (list, tuple,),
              "dtype": (str,) }

    @command("")
    def __init__(self, shape, dtype):
        Object.__init__(self)
        self.shape = shape
        self.dtype = dtype

    @command("set_data", encode=["data"])
    def set_data(self, offset, data):
        pass

if __name__ == '__main__':
    import GSP

    GSP.mode("client")
    array = Array( [3,3], "uint32")
    array.set_data(0, [1,2,3])
    
