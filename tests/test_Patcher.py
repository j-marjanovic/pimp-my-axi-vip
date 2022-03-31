from pathlib import Path
from pimp_my_axi_vip import Patcher


def test_patcher():
    parsed_lines = Patcher.Patcher.parse_patch(
        Path(__file__).parent / "resources/example_pkg.patch"
    )

    assert isinstance(parsed_lines[0], Patcher._DiffHeader)
    assert isinstance(parsed_lines[1], Patcher._DiffExtendedHeaderLine)
    assert isinstance(parsed_lines[2], Patcher._DiffFromToLine)
    assert isinstance(parsed_lines[3], Patcher._DiffFromToLine)
