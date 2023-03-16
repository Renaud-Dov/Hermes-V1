#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import enum


class TypeClose(enum.Enum):
    Resolve = 2
    Duplicate = 3
    Delete = 4
    ForceResolve = 8
    Other = 0


class TypeStatusTicket(enum.Enum):
    Other = 0
    Created = 1
    Resolved = 2
    Duplicate = 3
    Deleted = 4
    Joined = 5
    Closed = 6
    Recreated = 7
    ForceResolved = 8


def status_converter(close: TypeClose) -> TypeStatusTicket:
    """
    Converts a TypeClose to a TypeStatusTicket
    @param close: TypeClose to convert
    @return: TypeStatusTicket converted
    """
    return TypeStatusTicket(close.value)
