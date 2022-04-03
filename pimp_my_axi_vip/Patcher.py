import dataclasses
import enum
import os
import re
import shutil
from typing import List


class _TokenHeader(str):
    """Store first line"""


class _TokenExtendedHeaderLine(str):
    """Store extended header lines"""


class _TokenFromToLine:
    def __init__(self, s: str, is_add: bool):
        self.s = s
        self.is_add = is_add


class _TokenChunkHeader(str):
    pass


class _TokenChunkLine(str):
    pass


class _TokenChunkLineNoChange(_TokenChunkLine):
    pass


class _TokenChunkLineAdd(_TokenChunkLine):
    pass


class _TokenChunkLineRem(_TokenChunkLine):
    pass


@dataclasses.dataclass
class Chunk:
    header: _TokenChunkHeader
    lines: List[_TokenChunkLine]
    start_lineno: int
    end_lineno: int

    def __init__(self, header, lines):
        self.header = header
        self.lines = lines
        m = re.match(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@", header)
        self.start_lineno = int(m.group(1))
        self.end_lineno = self.start_lineno + int(m.group(2)) - 1


class Patcher:
    @classmethod
    def patch(cls, in_filename: str, patch_filename: str):
        cls._create_backup(in_filename)

        patch_tokens = cls._tokenize_patch(patch_filename)
        cls._verify_patch(patch_tokens, in_filename)

        patch_chunks = cls._create_chunks(patch_tokens)

        cls._apply_patch(patch_chunks, in_filename)

    @staticmethod
    def _create_backup(in_filename: str):
        postfixes = [".bak"]
        postfixes.extend(f".bak{i}" for i in range(2, 1000))

        for postfix in postfixes:
            new_name = in_filename + postfix
            if os.path.exists(new_name):
                continue
            shutil.copy(src=in_filename, dst=new_name)
            return
        else:
            raise RuntimeError(
                "We unsuccessfully tried 1000 different names for the backup"
            )

    @staticmethod
    def _tokenize_patch(filename: str) -> List:
        @enum.unique
        class State(enum.Enum):
            IDLE = enum.auto()
            HEADER = enum.auto()
            EXT_HEADER = enum.auto()
            FROM_TO_LINE = enum.auto()
            CHUNK_HDR = enum.auto()
            CHUNK_LINE = enum.auto()

        state = State.IDLE
        tokens = []

        for line in open(filename, "r").readlines():
            if state == State.IDLE:
                state = State.HEADER
            elif state == State.HEADER:
                state = State.EXT_HEADER
            elif state == State.EXT_HEADER:
                first_word = line.split(" ")[0]
                if first_word not in ["index", "mode", "new", "deleted"]:
                    state = State.FROM_TO_LINE
            elif state == State.FROM_TO_LINE:
                first_word = line.split(" ")[0]
                if first_word not in ["+++", "---"]:
                    state = State.CHUNK_HDR
            elif state == State.CHUNK_HDR:
                state = State.CHUNK_LINE
            elif state == State.CHUNK_LINE:
                if line[0] == "@":
                    state = State.CHUNK_HDR

            # print(state, line)
            if state == State.HEADER:
                tokens.append(_TokenHeader(line))
            elif state == State.EXT_HEADER:
                tokens.append(_TokenExtendedHeaderLine(line))
            elif state == State.FROM_TO_LINE:
                first_word = line.split(" ")[0]
                assert first_word in ["+++", "---"]
                is_add = first_word == "+++"
                tokens.append(_TokenFromToLine(line, is_add))
            elif state == State.CHUNK_HDR:
                tokens.append(_TokenChunkHeader(line))
            elif state == State.CHUNK_LINE:
                if line[0] == " ":
                    tokens.append(_TokenChunkLineNoChange(line))
                elif line[0] == "+":
                    tokens.append(_TokenChunkLineAdd(line))
                elif line[0] == "-":
                    tokens.append(_TokenChunkLineRem(line))

        return tokens

    def _verify_patch(patch_tokens, in_filename):
        assert patch_tokens[0].find("diff") == 0

        for token in patch_tokens:
            if isinstance(token, _TokenFromToLine):
                if token.is_add:
                    basename_from_patch = os.path.basename(token.s.strip())
                    assert basename_from_patch == os.path.basename(in_filename)

    def _create_chunks(patch_tokens: List):
        cur_hdr = None
        cur_lines = []

        chunks = []
        for token in patch_tokens:
            if isinstance(token, _TokenChunkHeader):
                if cur_hdr is None:
                    cur_hdr = token
                else:
                    chunks.append(Chunk(cur_hdr, cur_lines))
                    cur_hdr = token
                    cur_lines = []
            elif isinstance(token, _TokenChunkLine):
                cur_lines.append(token)

        if cur_hdr is not None and len(cur_lines) != 0:
            chunks.append(Chunk(cur_hdr, cur_lines))

        return chunks

    def _apply_patch(patch_chunks: List[Chunk], in_filename: str):

        with open(in_filename, "r") as in_file:
            in_file_iter = enumerate(in_file.readlines(), start=1)

            chunk_iter = iter(patch_chunks)
            chunk = next(chunk_iter)

            out_file_list = []

            for lineno, line in in_file_iter:
                if chunk is not None and lineno == chunk.start_lineno:
                    # in chunk
                    for chunk_line in chunk.lines:
                        if chunk_line[0] == " ":
                            out_file_list.append(chunk_line[1:])
                            if not chunk_line[1:] == line:
                                raise RuntimeError(
                                    "patch does not apply cleanly, "
                                    + f'expected "{chunk_line[1:-1]}", '
                                    + f'received "{line[:-1]}"'
                                )
                            if lineno != chunk.end_lineno:
                                lineno, line = next(in_file_iter)
                        if chunk_line[0] == "+":
                            out_file_list.append(chunk_line[1:])
                        if chunk_line[0] == "-":
                            lineno, line = next(in_file_iter)
                    try:
                        chunk = next(chunk_iter)
                    except StopIteration:
                        chunk = None
                else:
                    # not in chunk, just pass through
                    out_file_list.append(line)

        with open(in_filename, "w") as in_file:
            for line in out_file_list:
                in_file.write(line)
