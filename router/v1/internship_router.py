from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from internship.internship_schema import InternshipInput, InternshipOutput
from internship.internship_service import InternshipService
from typing import List

router = APIRouter(
    prefix="/internship",
    tags=["internship"]
)

@router.post("", status_code=201, response_model=InternshipOutput)
def create_internship(data: InternshipInput, session: Session = Depends(get_db)):
    _service = InternshipService(session)
    return _service.create_internship(data)

@router.get("", status_code=200, response_model=List[InternshipOutput])
def get_all_internships(skip: int = 0, limit: int = 10, session: Session = Depends(get_db)):
    _service = InternshipService(session)
    return _service.get_all_internships(skip, limit)

@router.put("", status_code=200, response_model=InternshipInput)
def update_internship(data: InternshipInput, session: Session = Depends(get_db)):
    _service = InternshipService(session)
    return _service.update_internship(data)

@router.delete("/{id}", status_code=204)
def delete_internship(id: int, session: Session = Depends(get_db)):
    _service = InternshipService(session)
    return _service.delete_internship_by_id(id)