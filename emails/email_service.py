from emails.email_repository import EmailRepository
from emails.email_schema import EmailInput, EmailOutput
from internship.internship_service import InternshipService
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

class EmailService:
    def __init__(self, session: Session):
        self.repository = EmailRepository(session)
        self.internship_service = InternshipService(session)
    
    def create_email(self, data: EmailInput, company: str) -> EmailOutput:
        internship_id = self.internship_service.get_internship_id_by_commpay(company)
        data.internship_id = internship_id
        return self.repository.create_email(data)
    
    def get_all_emails(self, skip: int = 0, limit: int = 10) -> List[EmailOutput]:
        return self.repository.get_all_emails(skip, limit)
    
    def get_emails_by_company(self, company: str) -> List[EmailOutput]:
        return self.repository.get_emails_by_company(company)
    
    def delete_email_by_id(self, id: int) -> bool:
        email = self.repository.get_email_by_id(id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return self.repository.delete_email(email)
    
