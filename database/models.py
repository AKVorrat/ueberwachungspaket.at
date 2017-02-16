from sqlalchemy import Column, Integer, String
from . import Base

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    number = Column(String(20), unique=True, nullable=False)
    time = Column(Integer, nullable=False)

    def __init__(self, number=None, time=None):
        self.number = number
        self.time = time

    def __repr__(self):
        return "<Reminder for {}>".format(self.number)
