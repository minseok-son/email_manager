from internship.internship_repository import InternshipRepository
from internship.internship_schema import InternshipInput, InternshipOutput
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

class InternshipService:
    def __init__(self, session: Session):
        self.repository = InternshipRepository(session)

    def create_internship(self, data: InternshipInput) -> InternshipOutput:
        if self.repository.internship_exists_by_company_name(data.company):
            raise HTTPException(status_code=400, detail="Company already exists")
        return self.repository.create_internship(data)
    
    def get_all_internships(self, skip: int = 0, limit: int = 10) -> List[InternshipOutput]:
        return self.repository.get_all_internships(skip, limit)
    
    def update_internship(self, data: InternshipInput) -> InternshipInput:
        internship = self.repository.get_internship_by_company_name(data.company)
        if not internship:
            raise HTTPException(status_code=404, detail="Company not found")
        return self.repository.update_internship(internship, data)
    
    def delete_internship_by_name(self, company_name: str) -> bool:
        internship = self.repository.get_internship_by_company_name(company_name)
        if not internship:
            raise HTTPException(status_code=404, detail="Company not found")
        return self.repository.delete_internship(internship)
    
