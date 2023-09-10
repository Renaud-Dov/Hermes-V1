#  Copyright (c) 2023.
#  Author: Dov Devers (https://bugbear.fr)
#  All right reserved

import enum


class CloseType(enum.Enum):
    Resolve = 0
    Duplicate = 1
    Delete = 2
    ForceResolve = 3

