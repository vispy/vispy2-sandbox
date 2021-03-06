# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import numpy as np
from typing import Union
from GSP import OID, Object, command
from typeguard import typechecked
from array import Array

class Transform(Object):
    def __init__(self):
        Object.__init__(self)

    def __repr__(self):
        return f"Transform [id={self.id}]"

    
