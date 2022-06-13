# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import GSP
import numpy as np
from array import Array
from datatype import Datatype

if __name__ == '__main__':

    GSP.mode("client", reset=True, output=False)
    # ------------------------------------------
    shape = [3,]
    dtype = Datatype("u4")
    data = np.arange(3,dtype=np.uint32).tobytes()
    array = Array(shape, dtype, data)
    
    array.set_data(0, (1 + np.arange(3, dtype=np.uint32)).tobytes())
    client_objects = GSP.objects()
    
    GSP.mode("server", reset=True)
    # ------------------------------------------
    for command in GSP.commands():
        GSP.process(command, globals(), locals())
    server_objects = GSP.objects()

    print(f"Client: {client_objects}")
    print(f"Server: {server_objects}")
    print(f"Test result: {client_objects == server_objects}")

