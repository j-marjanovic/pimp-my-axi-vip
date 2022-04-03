#! /usr/bin/env python3

import logging
import os
from pathlib import Path
from typing import Any, Union

from pimp_my_axi_vip.Patcher import Patcher

Openable = Union[str, bytes, int, "os.PathLike[Any]"]


def xsim_ini_remove_xilinx_vip(xsimini_file: Openable):
    """Remove `xilinx_vip` library from the xsim.ini"""

    LIB_TO_REM = "xilinx_vip"

    in_lines = open(xsimini_file, "r").readlines()
    out_lines = []

    for in_line in in_lines:
        if not in_line.find(LIB_TO_REM) == 0:
            out_lines.append(in_line)

    assert len(in_lines) - 1 == len(out_lines), "One line should be removed in this step"

    open(xsimini_file, "w").write("".join(out_lines))
    logging.info(f"    removed `xilinx_vip` from {xsimini_file}")


def patch_axi_vip_pkg(axi_vip_pkg_filename: Openable, patch_filename: Openable):
    Patcher.patch(axi_vip_pkg_filename, patch_filename)
    logging.info(f"    patched {axi_vip_pkg_filename}")


def main():
    logging.basicConfig(level=logging.INFO)

    XILINX_FOLDER = "/home/jan/Xilinx"
    DATA_FOLDER = os.path.join(XILINX_FOLDER, "Vivado/2021.2/data")

    logging.info("0. Parameters")
    logging.info(f"    {XILINX_FOLDER=}")
    logging.info(f"    {DATA_FOLDER=}")

    logging.info("1. Removing `xilinx_vip` library from `xsim.ini`")
    xsim_ini_remove_xilinx_vip(os.path.join(DATA_FOLDER, "xsim/xsim.ini"))

    logging.info("2. Patching  `axi_vip_pkg.sv`")
    axi_vip_pkg_filename = os.path.join(DATA_FOLDER, "xilinx_vip/hdl/axi_vip_pkg.sv")
    patch_filename = Path(__file__).parent / "patches/0000-axi_vip_pkg.patch"
    patch_axi_vip_pkg(axi_vip_pkg_filename, patch_filename)


if __name__ == "__main__":
    main()
