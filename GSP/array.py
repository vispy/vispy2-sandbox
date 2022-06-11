# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import Object, command
from typeguard import typechecked


class Array(Object):

    @typechecked
    @command("")
    def __init__(self, shape : Union[list,tuple],
                       dtype : str):
        Object.__init__(self)
        self.shape = shape
        self.dtype = dtype

    @typechecked
    @command("set_data")
    def set_data(self, offset : int,
                       data   : bytes ):
        pass
    
    
if __name__ == '__main__':
    import base64
    
    import GSP
    GSP.mode("client")
    array = Array( [3,3], "uint32")
    array.set_data(0, np.arange(3).tobytes())
    
    

    
    
    
