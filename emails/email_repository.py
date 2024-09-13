from sqlalchemy.orm import Session
from emails.email_model import Email
from emails.email_schema import EmailInput, EmailOutput
from internships.internship_model import Internship
from typing import List, Optional, Type
from datetime import datetime

class EmailRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_email(self, data: EmailInput) -> EmailOutput:
        email = Email(**data.model_dump(exclude_none=True))
        self.session.add(email)
        self.session.commit()
        self.session.refresh(email)
        return EmailOutput(**email.__dict__)

    def get_all_emails(self, skip: int = 0, limit: int = 10) -> List[EmailOutput]:
        emails = self.session.query(Email).offset(skip).limit(limit).all()
        return [EmailOutput(**email.__dict__) for email in emails]
    
    def get_email_by_id(self, email_id: int) -> Optional[Email]:
        return self.session.query(Email).filter_by(id=email_id).first()
    
    def get_emails_by_company(self, company: str) -> List[EmailOutput]:
        emails = self.session.query(Email).join(Internship).filter(Internship.company == company).all()
        return [EmailOutput(**email.__dict__) for email in emails]
    
    def get_latest_email_date(self):
        latest_email = self.session.query(Email).order_by(Email.timestamp.desc()).first()
        return latest_email.timestamp if latest_email else None
    
    def delete_email(self, email: Type[Email]) -> bool:
        self.session.delete(email)
        self.session.commit()
        return True
    
    def email_exists_by_timestamp(self, timestamp: datetime) -> bool:
        return self.session.query(Email).filter_by(timestamp=timestamp).first() is not None