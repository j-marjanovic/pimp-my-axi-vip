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


def test_full_patch(tmpdir):

    orig_file_test = tmpdir.join("example_pkg.sv")
    orig_file_resources = open(Path(__file__).parent / "resources/example_pkg.sv", "r")
    orig_file_test.write(orig_file_resources.read())

    patch_filename = Path(__file__).parent / "resources/example_pkg.patch"

    Patcher.Patcher.patch(orig_file_test, patch_filename)
