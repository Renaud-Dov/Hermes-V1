import enum


class TypeClose(enum.Enum):
    Other = 0
    Resolved = 2
    Duplicate = 3
    Closed = 6
    Deleted = 4


class TypeStatusTicket(enum.Enum):
    Other = 0
    Created = 1
    Resolved = 2
    Duplicate = 3
    Deleted = 4
    Joined = 5
    Closed = 6


def status_converter(close: TypeClose) -> TypeStatusTicket:
    return TypeStatusTicket(close.value)
