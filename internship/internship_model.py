from sqlalchemy import Column, Integer, String
from config.database import Base

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True)
    company = Column(String, index=True, unique=True, nullable=False)
    stage = Column(Integer, nullable=False)