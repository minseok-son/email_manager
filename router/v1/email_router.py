from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from emails.email_schema import EmailInput, EmailOutput
from emails.email_service import EmailService
from typing import List

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

@router.post("/{company}", status_code=201, response_model=EmailOutput)
def create_email(data: EmailInput, company: str, session: Session = Depends(get_db)):
    _service = EmailService(session)
    return _service.create_email(data, company)

@router.get("/{company}", status_code=200, response_model=List[EmailOutput])
def get_emails_by_company(company: str, session: Session = Depends(get_db)):
    _service = EmailService(session)
    return _service.get_emails_by_company(company)

@router.delete("/{id}", status_code=204)
def delete_email(id: int, session: Session = Depends(get_db)):
    _service = EmailService(session)
    return _service.delete_email_by_id(id)