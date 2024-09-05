from sqlalchemy import Column, Integer, String, ForeignKey
from config.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    confidence = Column(Integer)
    internship_id = Column(Integer, ForeignKey('internships.id'))