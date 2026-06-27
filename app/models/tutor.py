from sqlalchemy import Column, ForeignKey, Integer
from app.models.base import Base


class Tutor(Base):
    __tablename__ = "tutors"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
