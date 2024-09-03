from sqlalchemy.orm import Session
from emails.email_model import Email
from emails.email_schema import EmailInput, EmailOutput
from internship.internship_model import Internship
from typing import List, Optional, Type

class EmailRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_email(self, data: EmailInput) -> EmailOutput:
        email = Email(**data.model_dump(exclude_none=True))
        self.session.add(email)
        self.session.commit()
        self.session.refresh(email)
        return EmailOutput(url=email.url, internship_id=email.internship_id)

    def get_all_emails(self, skip: int = 0, limit: int = 10) -> List[EmailOutput]:
        emails = self.session.query(Email).offset(skip).limit(limit).all()
        return [EmailOutput(**email.__dict__) for email in emails]
    
    def get_email_by_id(self, email_id: int) -> Optional[Email]:
        return self.session.query(Email).filter_by(id=email_id).first()
    
    def get_emails_by_company(self, company: str) -> List[EmailOutput]:
        emails = self.session.query(Email).join(Internship).filter(Internship.company == company).all()
        return [EmailOutput(**email.__dict__) for email in emails]
    
    def delete_email(self, email: Type[Email]) -> bool:
        self.session.delete(email)
        self.session.commit()
        return True