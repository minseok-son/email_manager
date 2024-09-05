from celeryconfig import celery
from dotenv import load_dotenv
import imaplib
import email
import os
import re
from typing import List
import google.generativeai as genai
from collections import defaultdict
from bs4 import BeautifulSoup
import urllib.parse
from internships.internship_service import InternshipService
from internships.internship_schema import InternshipInput
from emails.email_service import EmailService
from emails.email_schema import EmailInput
from fastapi import HTTPException

load_dotenv()

def filter_by_subject(date: str) -> List[str]:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    mail.select("INBOX")

    _, msgs = mail.uid('Search', None, 'SINCE "14-Aug-2024"')
    prompt_message = "Given these Ids and subjects of emails, return only and just the list of ids and their subjects and nothing else if the subject sounds related to an internship application "

    for uid in msgs[0].split():
        _, msg = mail.uid('Fetch', uid, "(RFC822)")
        raw_message = msg[0][1]

        msg = email.message_from_bytes(raw_message)

        subject = msg['Subject']
        decoded_subject, encoding = email.header.decode_header(subject)[0]
        if encoding is not None:
            subject = decoded_subject.decode(encoding)
        print("ID: " + str(uid) + " Subject: " + str(subject))
        prompt_message += "Id: " + str(uid) + " Subject: " + str(subject) + "\n"
    
    mail.logout()

    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt_message)

    pattern = r"b'(\d+)"
    str_ids = re.findall(pattern, response.text)
    return [bytes(id, 'utf-8') for id in str_ids]

def filter_by_body(uids: List[bytes]) -> dict[list]:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    mail.select("INBOX")

    prompt_message = "From these messages extract company and stage (Applied, Interview, Accepted, Rejected) from internship-related email. Additionally indicate the confidence level of the evaluation from 1-5. Format response as: Company: _______, Stage: _______, Confidence: _____, URL: ______ and nothing else. If the body of the email indicates that this person did not apply to the company, then return N/A. "

    for uid in uids:
        _, msg = mail.uid("Fetch", uid, "(RFC822)")
        raw_message = msg[0][1]

        msg = email.message_from_bytes(raw_message)
        msg_id = msg['Message-ID']

        url = f'https://mail.google.com/mail/u/0/#search/rfc822msgid:{urllib.parse.quote(msg_id)}'

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                if content_type == "text/html":
                    html_content = part.get_payload(decode=True).decode()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body = soup.get_text(strip=True)
                    break
        else:
            html_content = msg.get_payload(decode=True).decode()
            soup = BeautifulSoup(html_content, 'html.parser')
            body = soup.get_text(strip=True)

        prompt_message += body + f" URL: {url}" + "\n\n"
    
    mail.logout()

    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt_message)

    pattern = r"Company: (.+), Stage: (.+), Confidence: (\d+), URL: (.+)"
    matches = re.findall(pattern, response.text)
    results = defaultdict(list)

    for company, stage, confidence, url in matches:
        if company != "N/A" and stage != "N/A" and confidence != "N/A":
            results[company].append((stage, int(confidence), url))
    
    return results
    

@celery.task
def hourly_task():
    uids = filter_by_subject("tmp")
    results = filter_by_body(uids)

    internship_service = InternshipService()
    email_service = EmailService()

    for company in results.keys():
        stage = results[company][-1][0]
        try:
            internship_service.create_internship(InternshipInput(company=company, stage=stage))
        except(HTTPException):
            pass

    for company in results.keys():
        for url, confidence in results[company]:
            try:
                email_service.create_email(EmailInput(url=url, confidence=confidence), company)
            except(HTTPException):
                pass
        