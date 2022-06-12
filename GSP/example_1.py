# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import GSP
from canvas import Canvas
from viewport import Viewport

if __name__ == '__main__':

    GSP.mode("client")
    canvas = Canvas(512, 512, 100, 1, False)
    viewport = Viewport(canvas.id, 0, 0, 512, 512)
