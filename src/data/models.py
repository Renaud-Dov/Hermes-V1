import datetime
import uuid
from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, BigInteger, func, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from src.data.engine import Base, engine
from src.domain.entity.TicketStatus import Status
from src.domain.entity.logType import LogType


class TicketLog(Base):
    __tablename__ = "ticket_logs"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    ticket: Mapped["Ticket"] = relationship(back_populates="logs")
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))

    kind: Mapped["LogType"]
    by: Mapped[str]
    at: Mapped[datetime.datetime] = mapped_column()
    message: Mapped[Optional[str]]


class TicketParticipant(Base):
    __tablename__ = "ticket_participants"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="participants")
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"))

    user_id: Mapped[str] = mapped_column()
    taken_at: Mapped[datetime.datetime] = Column(DateTime(timezone=True), default=func.now())


class TicketTag(Base):
    __tablename__ = "ticket_tags"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="tags")
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.id"))

    tag: Mapped[str] = mapped_column()


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    # forum: Mapped["Forum"] = relationship(back_populates="tickets")
    forum_id: Mapped[str] = mapped_column()
    guild_id: Mapped[str] = mapped_column()

    name: Mapped[str] = mapped_column()
    thread_id: Mapped[str] = mapped_column(unique=True)
    status: Mapped["Status"] = mapped_column(default=Status.OPEN)

    created_by: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column()
    taken_at: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)
    updated_at: Mapped[datetime.datetime] = mapped_column()
    closed_at: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)

    participants: Mapped[List["TicketParticipant"]] = relationship(back_populates="ticket",
                                                                   cascade="all, delete-orphan")
    reopened_times: Mapped[int] = mapped_column(default=0)
    webhook_message_url: Mapped[str] = mapped_column()

    logs: Mapped[List["TicketLog"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    tags: Mapped[List["TicketTag"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_id={self.ticket_id}, created_by={self.created_by}, created_at={self.created_at}, updated_at={self.updated_at}, status={self.status})>"

# class Forum(Base):
#     __tablename__ = "forums"
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     guild_id: Mapped[int] = mapped_column()
#     channel_id: Mapped[int] = mapped_column()
#     webhook_channel: Mapped[int] = mapped_column()
#     name: Mapped[str] = mapped_column()
#     trace_tag: Mapped[str] = mapped_column()
#     end_tag: Mapped[str] = mapped_column()
#     closing_tag: Mapped[str] = mapped_column()
#     # current_tags: Mapped[List[str]] = mapped_column()
#     created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
#     updated_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
#
#     tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="forum", cascade="all, delete-orphan")
#
#     def __repr__(self):
#         return f"<Forum(id={self.id}, guild_id={self.guild_id}, channel_id={self.channel_id}, webhook_channel={self.webhook_channel}, name={self.name}, trace_tag={self.trace_tag}, end_tag={self.end_tag}, closing_tag={self.closing_tag}, current_tags={self.current_tags}, created_at={self.created_at}, updated_at={self.updated_at})>"
