# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import GSP
from canvas import Canvas
from viewport import Viewport

if __name__ == '__main__':

    GSP.mode("client", reset=True, output=False)
    # ------------------------------------------
    canvas = Canvas(512,512, 100, 1)
    viewport = Viewport(canvas.id, 0, 0, 512, 512)
    client_objects = GSP.objects()

    
    GSP.mode("server", reset=True)
    # ------------------------------------------
    for command in GSP.commands():
        GSP.process(command, globals(), locals())
    server_objects = GSP.objects()

    
    print(client_objects == server_objects)
