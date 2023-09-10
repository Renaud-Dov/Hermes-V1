import enum


class Status(enum.Enum): # ticket status (open, in progress, closed)
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    DELETED = "deleted"

