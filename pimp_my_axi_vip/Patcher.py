import enum
import os
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


class _TokenChunkHeader:
    def __init__(self, s: str):
        self.s = s


class _TokenChunkLineNoChange(str):
    pass


class _TokenChunkLineAdd(str):
    pass


class _TokenChunkLineRem(str):
    pass


class Patcher:
    @classmethod
    def patch(cls, in_filename: str, patch_filename: str):
        cls._create_backup(in_filename)
        patch_tokens = cls._tokenize_patch(patch_filename)
        cls._verify_patch(patch_tokens, in_filename)

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
