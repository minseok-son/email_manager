import time
# from celery_files.celeryconfig import celery
from dotenv import load_dotenv
import imaplib
import email
import os
import re
from typing import List
import google.generativeai as genai
import google.api_core.exceptions
from collections import defaultdict
from bs4 import BeautifulSoup
import urllib.parse
import requests
import time
from datetime import datetime

load_dotenv()

class GenAIAPIClient:
    def __init__(self, max_calls_per_minute: int = 15):
        self.max_calls_per_minute = max_calls_per_minute
        self.calls_made = 0
        self.reset_time = time.time()
        self.configure_genai()

    def configure_genai(self):
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_content(self, prompt_message: str) -> str:
        if self.calls_made >= self.max_calls_per_minute:
            self.wait_until_reset()
        
        try:
            response = self.model.generate_content(prompt_message)
            self.calls_made += 1
            return response
        except google.api_core.exceptions.ResourceExhausted:
            self.wait_until_reset()
            return self.generate_content(prompt_message)

    def wait_until_reset(self):
        elapsed_time = time.time() - self.reset_time
        if elapsed_time < 60:
            time.sleep(60 - elapsed_time)
        self.made_calls = 0
        self.reset_time = time.time()

def filter_by_subject() -> List[str]:
    try:
        response = requests.get("http://localhost:8000/api/v1/email/latest-email-date/")
        response.raise_for_status()  # Raise an exception for bad status codes

        latest_email_date = response.json()
        if latest_email_date:
            latest_email_date = datetime.fromisoformat(latest_email_date)
            formatted_date = latest_email_date.strftime("%d-%b-%Y")
        else:
            formatted_date = "14-Aug-2024"  # Default date if API response is empty

    except requests.exceptions.RequestException as e:
        formatted_date = "14-Aug-2024"  # Default date if API request fails
    
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    mail.select("INBOX")

    print("Starting date ", formatted_date)

    _, msgs = mail.uid('Search', None, f'SINCE "{formatted_date}"')
    prompt_message = "Given these Ids and subjects of emails, return only and just the list of ids and their subjects and nothing else if the subject sounds related to an internship application "
    num_subject_filtered = 0
    for uid in msgs[0].split():
        _, msg = mail.uid('Fetch', uid, "(RFC822)")
        raw_message = msg[0][1]

        msg = email.message_from_bytes(raw_message)

        subject = msg['Subject']
        decoded_subject, encoding = email.header.decode_header(subject)[0]
        if encoding is not None:
            subject = decoded_subject.decode(encoding)
        
        num_subject_filtered += 1
        if num_subject_filtered % 10 == 0:  # Print progress every 10 emails
            print(f"Filtered by subject: {num_subject_filtered} emails")
        prompt_message += "Id: " + str(uid) + " Subject: " + str(subject) + "\n"
    
    mail.logout()
    print(f"Filtered by subject: {num_subject_filtered} emails")

    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt_message)

    pattern = r"b'(\d+)"
    str_ids = re.findall(pattern, response.text)
    print("Done filtering by subject: " + str(len(str_ids)))
    return [bytes(id, 'utf-8') for id in str_ids]

def filter_by_body(uids: List[bytes]) -> dict[list]:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    mail.select("INBOX")

    prompt_message = "From these messages extract company and stage (Applied, Interview, Accepted, Rejected) from internship-related email. Additionally indicate the confidence level of the evaluation from 1-5. Format response as: Company: _______, Stage: _______, Confidence: _____, URL: ______, Timestamp: _______ and nothing else. If the body of the email indicates that this person did not apply to the company, then return N/A. "

    num_body_filtered = 0
    for uid in uids:
        _, msg = mail.uid("Fetch", uid, "(RFC822)")
        raw_message = msg[0][1]

        msg = email.message_from_bytes(raw_message)
        msg_id = msg['Message-ID']
        timestamp = email.utils.parsedate_to_datetime(msg['Date'])
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
        num_body_filtered += 1
        if num_body_filtered % 10 == 0:  # Print progress every 10 emails
            print(f"Filtered by body: {num_body_filtered} emails")
        prompt_message += body + f" URL: {url}, Timestamp: {timestamp}" + "\n\n"
    
    mail.logout()
    print(f"Filtered by body: {num_body_filtered} emails")

    try:
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_message)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    print(response.text)

    pattern = r"Company: (.+), Stage: (.+), Confidence: (\d+), URL: (.+), Timestamp: (.+)"
    matches = re.findall(pattern, response.text)
    results = defaultdict(list)
    mapping = {"Applied": 0, "Interview": 1, "Accepted": 2, "Rejected": 3}

    for company, stage, confidence, url, timestamp in matches:
        if company != "N/A" and stage != "N/A" and confidence != "N/A":
            results[company].append((mapping[stage], int(confidence), url, timestamp))
    print(results)
    print("Done filtering by body")
    return results
    

# @celery.task
# def hourly_task():
#     uids = filter_by_subject("tmp")
#     results = filter_by_body(uids)

#     internship_service = InternshipService()
#     email_service = EmailService()

#     for company in results.keys():
#         stage = results[company][-1][0]
#         try:
#             internship_service.create_internship(InternshipInput(company=company, stage=stage))
#         except(HTTPException):
#             pass

#     for company in results.keys():
#         for _, confidence, url in results[company]:
#             try:
#                 email_service.create_email(EmailInput(url=url, confidence=confidence), company)
#             except(HTTPException):
#                 pass
while True:
    uids = filter_by_subject()
    results = filter_by_body(uids)
    
    for company in results.keys():
        stage = max(results[company], key=lambda x: x[0])[0]
        try:
            response = requests.post("http://localhost:8000/api/v1/internship", json={"id": None, "company": company, "stage": stage})
            response.raise_for_status()
        except requests.exceptions.RequestException:
            pass

    for company in results.keys():
        for _, confidence, url, timestamp in results[company]:
            try:
                response = requests.post(f"http://localhost:8000/api/v1/email/{company}", json={"id": None, "internship_id": None, "timestamp": timestamp, "url": url, "confidence": confidence})
                response.raise_for_status()
            except requests.exceptions.RequestException:
                pass
    
    print("Done processing emails")
    time.sleep(3600)