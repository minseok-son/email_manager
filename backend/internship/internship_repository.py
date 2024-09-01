from sqlalchemy.orm import Session
from internship.internship_model import Internship
from internship.internship_schema import InternshipInput, InternshipOutput
from typing import List, Optional, Type

class InternshipRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_internship(self, data: InternshipInput) -> InternshipOutput:
        internship = Internship(**data.model_dump(exclude_none=True))
        self.session.add(internship)
        self.session.commit()
        self.session.refresh(internship)
        return InternshipOutput(id=internship.id, company=internship.company, stage=internship.stage)

    def get_all_internships(self, skip: int = 0, limit: int = 10) -> List[InternshipOutput]:
        internships = self.session.query(Internship).offset(skip).limit(limit).all()
        return [InternshipOutput(**internship.__dict__) for internship in internships]

    def get_internship_by_company_name(self, company_name: str) -> Optional[Internship]:
        return self.session.query(Internship).filter_by(company=company_name).first()
    
    def internship_exists_by_company_name(self, company_name: str) -> bool:
        return self.session.query(Internship).filter_by(company=company_name).first() is not None

    def update_internship(self, internship: Type[Internship], data: InternshipInput) -> InternshipInput:
        internship.stage = data.stage
        self.session.commit()
        self.session.refresh(internship)
        return InternshipInput(**internship.__dict__)
    
    def delete_internship(self, internship: Type[Internship]) -> bool:
        self.session.delete(internship)
        self.session.commit()
        return True