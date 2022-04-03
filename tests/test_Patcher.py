from pathlib import Path

from pimp_my_axi_vip import Patcher


def test_tokenizer():
    tokens = Patcher.Patcher._tokenize_patch(
        Path(__file__).parent / "resources/example_pkg.patch"
    )

    assert isinstance(tokens[0], Patcher._TokenHeader)
    assert isinstance(tokens[1], Patcher._TokenExtendedHeaderLine)
    assert isinstance(tokens[2], Patcher._TokenFromToLine)
    assert isinstance(tokens[3], Patcher._TokenFromToLine)


def test_create_backup(tmpdir):
    orig_file = tmpdir.join("test.sv")
    orig_file.write("package test;\nendpackage\n")

    Patcher.Patcher._create_backup(orig_file)

    print(tmpdir.listdir())
    assert tmpdir.join("test.sv.bak").check()


def test_create_backup_more(tmpdir):
    orig_file = tmpdir.join("test.sv")
    orig_file.write("package test;\nendpackage\n")

    Patcher.Patcher._create_backup(orig_file)
    Patcher.Patcher._create_backup(orig_file)

    print(tmpdir.listdir())
    assert tmpdir.join("test.sv.bak").check()
    assert tmpdir.join("test.sv.bak2").check()


def test_create_chunks():
    tokens = Patcher.Patcher._tokenize_patch(
        Path(__file__).parent / "resources/example_pkg.patch"
    )

    chunks = Patcher.Patcher._create_chunks(tokens)
    assert len(chunks) == 3


def _test_full_patch_generic(test_name, tmpdir):
    orig_file_test = tmpdir.join(f"{test_name}.txt")
    orig_file_test.write(
        (open(Path(__file__).parent / f"resources/{test_name}.txt.orig", "r")).read()
    )

    patch_filename = Path(__file__).parent / f"resources/{test_name}.patch"

    Patcher.Patcher.patch(orig_file_test, patch_filename)

    exp_out = [
        row for row in open(Path(__file__).parent / f"resources/{test_name}.txt")
    ]
    result_out = [row for row in open(orig_file_test)]
    assert exp_out == result_out


def test_full_patch_add(tmpdir):
    _test_full_patch_generic("add", tmpdir)


def test_full_patch_modify(tmpdir):
    _test_full_patch_generic("modify", tmpdir)


def test_full_patch_remove(tmpdir):
    _test_full_patch_generic("remove", tmpdir)


def test_full_patch_combined(tmpdir):

    orig_file_test = tmpdir.join("example_pkg.sv")
    orig_file_resources = open(
        Path(__file__).parent / "resources/example_pkg.sv.orig", "r"
    )
    orig_file_test.write(orig_file_resources.read())

    patch_filename = Path(__file__).parent / "resources/example_pkg.patch"

    Patcher.Patcher.patch(orig_file_test, patch_filename)

    exp_out = [row for row in open(Path(__file__).parent / f"resources/example_pkg.sv")]
    result_out = [row for row in open(orig_file_test)]
    assert exp_out == result_out
