from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, Annotated
from uuid import UUID, uuid4
from pydantic import BaseModel
import models
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session


import imaplib
import email
from bs4 import BeautifulSoup
import re
from meta_ai_api import MetaAI
from collections import defaultdict

from dotenv import load_dotenv
import os

load_dotenv()

class EmailBase(BaseModel):
    id: Optional[UUID]
    subject: str
    body: str

class InternshipBase(BaseModel):
    id: Optional[UUID]
    company: str
    stage: str

class Mail:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = imaplib.IMAP4_SSL("imap.gmail.com")
            cls._instance.login(os.environ['EMAIL'], os.environ['PASSWORD'])
            cls._instance.select("INBOX")
        return cls._instance

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Filter emails by their subject and return ids of emails that sound like internship applications
def filter_by_subject():
    mail = Mail.get_instance()

    # Search for emails (e.g., "ALL")
    _, messages = mail.uid('Search', None, 'SINCE "14-Aug-2024" BEFORE "22-Aug-2024"')
    prompt_message = ""

    # Fetch email content
    for uid in messages[0].split():
        _, msg = mail.uid('Fetch', uid, "(RFC822)")
        raw_message = msg[0][1]
        
        
        # Parse the raw message content using email library
        message = email.message_from_bytes(raw_message)
        subject = message["Subject"]
        
        decoded_subject, encoding = email.header.decode_header(subject)[0]
        if encoding is not None:
            subject = decoded_subject.decode(encoding)
        # print("ID: " + str(uid) + " Subject: " + str(subject))
        prompt_message += "Id: " + str(uid) + " Subject: " + str(subject) + "\n"

    ai = MetaAI()
    response = ai.prompt(message="Given these Ids and subjects of emails, return only and just the list of ids and nothing else if the subject sounds related to an internship application " + prompt_message)
    pattern = r"b'(\d+)"
    str_ids = re.findall(pattern, response['message'])
    ids = [bytes(id, 'utf-8') for id in str_ids]
    print("DONE")   
    return ids

# Filter emails further by their body and extract company and stage information or N/A if not related
def filter_by_body(ids, db: db_dependency):
    mail = Mail.get_instance()

    h_map = defaultdict(list)
    ai = MetaAI()
    print(ids)

    for id in ids:
        _, msg = mail.uid('Fetch', id, "(RFC822)")
        raw_message = msg[0][1]
        
        # Parse the raw message content using email library
        message = email.message_from_bytes(raw_message)

        body = ""
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                # content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body = soup.get_text(strip=True)
                    break
        else:
            html_content = message.get_payload(decode=True).decode()
            soup = BeautifulSoup(html_content, 'html.parser')
            body = soup.get_text(strip=True)

        # print(body)

        response = ai.prompt(message="Extract company and stage (Applied, Interview, Accepted, Rejected) from internship-related email. If not related, return N/A for Company and Stage. Format response as: Company: _______, Stage: _______ and return nothing else" + body)
        print(response)

        company_name = re.search(r'Company: (.+),', response['message']).group(1)
        stage_name = re.search(r'Stage: (.+)', response['message']).group(1)
        print(company_name, stage_name)
        id_value = int(id.decode())

        if company_name != "N/A":
            existing_internship = db.query(models.Internship).get(id_value)

            if not existing_internship:
                db_internship = models.Internship(id=id_value, company=company_name, stage=stage_name)
                db.add(db_internship)
                db.commit()
            h_map[company_name].append(id)
    
    return h_map

@app.get("/emails/")
async def read_emails(db: db_dependency):
    res = filter_by_subject()
    h_map = filter_by_body(res, db)
    return h_map

@app.post("/emails/")
def create_email(email: EmailBase, db: db_dependency):
    db_email = models.Email(subject=email.subject, body=email.body)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

