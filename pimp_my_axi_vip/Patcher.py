import enum


class _DiffHeader(str):
    """Store first line"""


class _DiffExtendedHeaderLine(str):
    """Store extended header lines"""


class _DiffFromToLine:
    def __init__(self, s: str, is_add: bool):
        self.s = s
        self.is_add = is_add


class _DiffChunkHeader:
    def __init__(self, s: str):
        self.s = s


class _DiffChunkLineNoChange(str):
    pass


class _DiffChunkLineAdd(str):
    pass


class _DiffChunkLineRem(str):
    pass


class Patcher:
    @staticmethod
    def parse_patch(filename: str):
        @enum.unique
        class State(enum.Enum):
            IDLE = enum.auto()
            HEADER = enum.auto()
            EXT_HEADER = enum.auto()
            FROM_TO_LINE = enum.auto()
            CHUNK_HDR = enum.auto()
            CHUNK_LINE = enum.auto()

        state = State.IDLE
        out_l = []

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

            print(state, line)
            if state == State.HEADER:
                out_l.append(_DiffHeader(line))
            elif state == State.EXT_HEADER:
                out_l.append(_DiffExtendedHeaderLine(line))
            elif state == State.FROM_TO_LINE:
                first_word = line.split(" ")[0]
                assert first_word in ["+++", "---"]
                is_add = first_word == "+++"
                out_l.append(_DiffFromToLine(line, is_add))
            elif state == State.CHUNK_HDR:
                out_l.append(_DiffChunkHeader(line))
            elif state == State.CHUNK_LINE:
                if line[0] == " ":
                    out_l.append(_DiffChunkLineNoChange(line))
                elif line[0] == "+":
                    out_l.append(_DiffChunkLineAdd(line))
                elif line[0] == "-":
                    out_l.append(_DiffChunkLineRem(line))

        return out_l
