from sqlalchemy import Column, ForeignKey, Integer, String
from database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    body = Column(String)

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id"))
    company = Column(String)
    stage = Column(String)