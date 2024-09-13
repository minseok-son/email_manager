from emails.email_repository import EmailRepository
from emails.email_schema import EmailInput, EmailOutput
from internships.internship_service import InternshipService
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

class EmailService:
    def __init__(self, session: Session):
        self.email_repository = EmailRepository(session)
        self.internship_service = InternshipService(session)
    
    def create_email(self, data: EmailInput, company: str) -> EmailOutput:
        if self.email_repository.email_exists_by_timestamp(data.timestamp):
            raise HTTPException(status_code=400, detail="Email already exists")
        internship_id = self.internship_service.get_internship_id_by_commpay(company)
        data.internship_id = internship_id
        return self.email_repository.create_email(data)
    
    def get_all_emails(self, skip: int = 0, limit: int = 10) -> List[EmailOutput]:
        return self.email_repository.get_all_emails(skip, limit)
    
    def get_emails_by_company(self, company: str) -> List[EmailOutput]:
        return self.email_repository.get_emails_by_company(company)
    
    def get_latest_email_date(self) -> str:
        date = self.email_repository.get_latest_email_date()
        if not date:
            raise HTTPException(status_code=404, detail="Date not found")
        return date
    
    def delete_email_by_id(self, id: int) -> bool:
        email = self.email_repository.get_email_by_id(id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return self.email_repository.delete_email(email)
    
