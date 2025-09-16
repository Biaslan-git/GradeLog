from sqlalchemy import Column, ForeignKey, null
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.attributes import backref_listeners
from src.database import Base


class User(Base):
    __tablename__ = 'users'

    chat_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=False)

    subjects: Mapped[list['Subject']] = relationship(
        'Subject', 
        back_populates='user',
        cascade="all, delete-orphan"
    )

    grades: Mapped[list['Grade']] = relationship(
        'Grade', 
        back_populates='user',
        cascade="all, delete-orphan"
    )
    
class Subject(Base):
    __tablename__ = 'subjects'

    title: Mapped[str] = mapped_column(nullable=False)
    numerator: Mapped[int] = mapped_column(nullable=False)
    denominator: Mapped[int] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', back_populates='subjects')

    grades: Mapped[list['Grade']] = relationship(
        'Grade', 
        back_populates='subject',
        cascade="all, delete-orphan"
    )

class Grade(Base):
    __tablename__ = 'grades'

    grade1: Mapped[int] = mapped_column(nullable=False)
    grade2: Mapped[int] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', back_populates='grades')

    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    subject: Mapped['Subject'] = relationship('Subject', back_populates='grades')




