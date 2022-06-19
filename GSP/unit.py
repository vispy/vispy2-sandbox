# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
from enum import Enum
from array import Array
from typing import List, Tuple, Union
from GSP import Object, command
from typeguard import typechecked


class Unit:

    units = None
    
    @typechecked
    @command("")
    def __init__(self, name : str,
                       symbol : str):
        Object.__init__(self)
        self.name = name
        self.symbol = symbol

# See https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Values_and_units
Unit.units = {

    # Absolute
    "cm" : Unit("centimeter", "cm"),
    "mm" : Unit("millimeter", "mm"),
    "in" : Unit("inch", "in"),
    "pt" : Unit("point", "pt"),
    "px" : Unit("pixel", "px"),

    # Relative
    "em" : Unit("font size", "em"),
    "lw" : Unit("line width", "lw"),
    "sw" : Unit("stroke width", "sw"),
    "vw" : Unit("viewport width", "vw"),
    "vh" : Unit("viewport height", "vh"),
    "vmax" : Unit("viewport max(width,height)", "vmax"),
    "vmin" : Unit("viewport min(width,height)", "vmin"),
    "cw" : Unit("canvas width", "cw"),
    "ch" : Unit("canvas height", "ch"),
    "cmax" : Unit("canvas max(width,height)", "cmax"),
    "cmin" : Unit("canvas min(width,height)", "cmin"),
}
