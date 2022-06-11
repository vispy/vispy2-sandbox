# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import GSP
from canvas import Canvas

if __name__ == '__main__':

    GSP.mode("client", reset=True, output=False)
    # ------------------------------------------
    canvas = Canvas(0, 0, 0, 0)
    canvas.set_size(512, 512)
    canvas.set_dpi(100)
    canvas.set_dpr(1)
    client_objects = GSP.objects()
    
    GSP.mode("server", reset=True)
    # ------------------------------------------
    for command in GSP.commands():
        GSP.process(command, globals(), locals())
    server_objects = GSP.objects()

    print(f"Client: {client_objects}")
    print(f"Server: {server_objects}")
    print(f"Test result: {client_objects == server_objects}")
