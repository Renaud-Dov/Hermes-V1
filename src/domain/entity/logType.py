import enum


class LogType(enum.Enum): # ticket status (open, in progress, closed)
    CREATED_TICKET = "created_ticket"
    CLOSED_TICKET = "closed_ticket"
    DELETED_TICKET = "deleted_ticket"
    REOPENED_TICKET = "reopened_ticket"
    NEW_PARTICIPANT = "new_participant"
    RENAMED_TICKET = "renamed_ticket"


