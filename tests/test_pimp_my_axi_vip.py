import textwrap

import pimp_my_axi_vip.pimp_my_axi_vip as pmav


def test_xsim_ini_remove_empty(tmp_path):
    """If there is no xilinx_vip line, do nothing"""

    f = tmp_path / "xsim.ini"

    XSIM_INI_CONTENT = textwrap.dedent(
        """
    std=$RDI_DATADIR/xsim/vhdl/std
    ieee=$RDI_DATADIR/xsim/vhdl/ieee
    ieee_proposed=$RDI_DATADIR/xsim/vhdl/ieee_proposed
    vl=$RDI_DATADIR/xsim/vhdl/vl
    """
    )
    f.write_text(XSIM_INI_CONTENT)

    pmav.xsim_ini_remove_xilinx_vip(str(f))

    print(f.read_text())

    assert f.read_text() == XSIM_INI_CONTENT


def test_xsim_ini_remove(tmp_path):
    """Remove the `xilinx_vip` line"""

    f = tmp_path / "xsim.ini"

    XSIM_INI_CONTENT = textwrap.dedent(
        """
        std=$RDI_DATADIR/xsim/vhdl/std
        ieee=$RDI_DATADIR/xsim/vhdl/ieee
        ieee_proposed=$RDI_DATADIR/xsim/vhdl/ieee_proposed
        xilinx_vip=/home/jan/Projects/AXI/test_prj/tmp/xsim.dir/xilinx_vip
        vl=$RDI_DATADIR/xsim/vhdl/vl
        """
    )
    XSIM_INI_CONTENT_EXPECTED = textwrap.dedent(
        """
        std=$RDI_DATADIR/xsim/vhdl/std
        ieee=$RDI_DATADIR/xsim/vhdl/ieee
        ieee_proposed=$RDI_DATADIR/xsim/vhdl/ieee_proposed
        vl=$RDI_DATADIR/xsim/vhdl/vl
        """
    )
    f.write_text(XSIM_INI_CONTENT)

    pmav.xsim_ini_remove_xilinx_vip(str(f))

    assert f.read_text() == XSIM_INI_CONTENT_EXPECTED
