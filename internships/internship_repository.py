from sqlalchemy.orm import Session
from internships.internship_model import Internship
from internships.internship_schema import InternshipInput, InternshipOutput
from typing import List, Optional, Type

class InternshipRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_internship(self, data: InternshipInput) -> InternshipOutput:
        internship = Internship(**data.model_dump(exclude_none=True))
        self.session.add(internship)
        self.session.commit()
        self.session.refresh(internship)
        return InternshipOutput(company=internship.company, stage=internship.stage)

    def get_all_internships(self, skip: int = 0, limit: int = 10) -> List[InternshipOutput]:
        internships = self.session.query(Internship).offset(skip).limit(limit).all()
        return [InternshipOutput(**internship.__dict__) for internship in internships]
    
    def get_internship_by_id(self, internship_id: int) -> Optional[Internship]:
        return self.session.query(Internship).filter_by(id=internship_id).first()

    def internship_exists_by_id(self, internship_id: int) -> bool:
        return self.session.query(Internship).filter_by(id=internship_id).first() is not None

    def get_internship_by_company(self, company: str) -> Optional[Internship]:
        return self.session.query(Internship).filter_by(company=company).first()
    
    def internship_exists_by_company(self, company: str) -> bool:
        return self.session.query(Internship).filter_by(company=company).first() is not None

    def update_internship(self, internship: Type[Internship], data: InternshipInput) -> InternshipInput:
        internship.stage = data.stage
        self.session.commit()
        self.session.refresh(internship)
        return InternshipInput(**internship.__dict__)
    
    def delete_internship(self, internship: Type[Internship]) -> bool:
        self.session.delete(internship)
        self.session.commit()
        return True