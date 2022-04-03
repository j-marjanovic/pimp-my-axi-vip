#! /usr/bin/env python3

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Union

from pimp_my_axi_vip.Patcher import Patcher

Openable = Union[str, bytes, int, "os.PathLike[Any]"]


def xsim_ini_remove_xilinx_vip(xsimini_file: Openable):
    """Remove `xilinx_vip` library from the xsim.ini"""

    LIB_TO_REM = "xilinx_vip"

    # create backup first
    shutil.copy(xsimini_file, xsimini_file + ".bak")

    in_lines = open(xsimini_file, "r").readlines()
    out_lines = []

    for in_line in in_lines:
        if not in_line.find(LIB_TO_REM) == 0:
            out_lines.append(in_line)

    assert len(in_lines) - 1 == len(
        out_lines
    ), "One line should be removed in this step"

    open(xsimini_file, "w").write("".join(out_lines))
    logging.info(f"    removed `xilinx_vip` from {xsimini_file}")


def patch_axi_vip_pkg(axi_vip_pkg_filename: Openable, patch_filename: Openable):
    Patcher.patch(axi_vip_pkg_filename, patch_filename)
    logging.info(f"    patched {axi_vip_pkg_filename}")


def compile_library(xilinx_vivado_dir, list_filename):
    tmpdir = tempfile.mkdtemp()
    logging.info(f"    tmpdir: {tmpdir}")

    files_to_compile = open(list_filename, "r").readlines()
    for file_to_compile in files_to_compile:
        filename = file_to_compile.strip().replace("$XILINX_VIVADO", xilinx_vivado_dir)
        logging.info(f"    compiling {filename}")

        out = subprocess.check_output(
            [
                "xvlog",
                "--sv",
                "--work",
                "xilinx_vip",
                "-i",
                os.path.join(xilinx_vivado_dir, "data/xilinx_vip/include"),
                filename,
            ],
            cwd=tmpdir,
        )
        logging.debug(f"    result: {out}")

    logging.info("    compiled the `xilinx_vip library")

    return tmpdir


def copy_library_to_xilinx_dir(lib_tmp_folder, data_dir):
    dst_dir = os.path.join(data_dir, "xsim/ip/xilinx_vip_pimped")

    shutil.copytree(
        src=os.path.join(lib_tmp_folder, "xsim.dir/xilinx_vip"),
        dst=dst_dir,
        dirs_exist_ok=True,
    )

    return dst_dir


def xsim_ini_add_xilinx_vip(xsimini_file: Openable, xilinx_vip_dir: Openable):
    out_lines = open(xsimini_file, "r").readlines()
    out_lines.append(f"xilinx_vip={xilinx_vip_dir}")

    open(xsimini_file, "w").write("".join(out_lines))
    logging.info(f"    added {xilinx_vip_dir} to {xsimini_file}")


def main():
    logging.basicConfig(level=logging.INFO)

    XILINX_DIR = "/home/jan/Xilinx"
    DATA_DIR = os.path.join(XILINX_DIR, "Vivado/2021.2/data")

    logging.info("0. Parameters")
    logging.info(f"    {XILINX_DIR=}")
    logging.info(f"    {DATA_DIR=}")

    logging.info("1. Removing `xilinx_vip` library from `xsim.ini`")
    xsim_ini_remove_xilinx_vip(os.path.join(DATA_DIR, "xsim/xsim.ini"))

    logging.info("2. Patching  `axi_vip_pkg.sv`")
    axi_vip_pkg_filename = os.path.join(DATA_DIR, "xilinx_vip/hdl/axi_vip_pkg.sv")
    patch_filename = Path(__file__).parent / "patches/0000-axi_vip_pkg.patch"
    patch_axi_vip_pkg(axi_vip_pkg_filename, patch_filename)

    logging.info("3. Compiling the patched library")
    lib_tmp_folder = compile_library(
        os.path.join(XILINX_DIR, "Vivado/2021.2"),
        os.path.join(DATA_DIR, "xilinx_vip/xilinx_vip_pkg.list.f"),
    )

    logging.info("4. Copying the compiled library to Xilinx `data` folder")
    lib_dir = copy_library_to_xilinx_dir(lib_tmp_folder, DATA_DIR)

    lib_dir = "/home/jan/Xilinx/Vivado/2021.2/data/xsim/ip/xilinx_vip_pimped"
    logging.info("5. Adding the pimped library back to `xsim.ini`")
    xsim_ini_add_xilinx_vip(os.path.join(DATA_DIR, "xsim/xsim.ini"), lib_dir)


if __name__ == "__main__":
    main()
