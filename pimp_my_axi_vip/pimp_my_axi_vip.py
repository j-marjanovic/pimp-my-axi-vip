#! /usr/bin/env python3

import os
from typing import Any, Union

Openable = Union[str, bytes, int, "os.PathLike[Any]"]


def xsim_ini_remove_vivado_ip(xsimini_file: Openable):
    """Remove `vivado_ip` library from the xsim.ini"""

    LIB_TO_REM = "xilinx_vip"

    in_lines = open(xsimini_file, "r").readlines()
    out_lines = []

    for in_line in in_lines:
        if not in_line.find(LIB_TO_REM) == 0:
            out_lines.append(in_line)

    open(xsimini_file, "w").write("".join(out_lines))
