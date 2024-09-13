from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from config.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    internship_id = Column(Integer, ForeignKey('internships.id'))
    timestamp = Column(DateTime)
    url = Column(String, nullable=False)
    confidence = Column(Integer)
    