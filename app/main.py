import os
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from app.database import SessionLocal, User, PartnerUniversity, Application
from app.gpt_utils import standardize_universities
from app.schemas import WebhookData


load_dotenv()
app = FastAPI()

def get_database() :
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

def send_email(to_address : str, nickname : str, uuid : str) :
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    subject = "[교환학생 비교 폼] 보내드립니다!"
    body = f"""
안녕하세요, {nickname}님!
참여해주신 교환학생 비교 폼 관련하여 연락드립니다!
아래 링크를 통해 정리된 내용을 보실 수 있어요!
✅ 확인 링크 : link1, {uuid}

성적 비교는 아래와 같이 정리했습니다!


다만 더 정확하고 공정한 비교를 위해 학점과 어학 점수가 공개된 비교 폼의 경우, 성적 인증을 해주신 분들 기준으로 정리해 드리는 것이 더 적절하다고 판단했습니다.
불편을 드리지 않도록 아래 구글폼을 통해 간단히 인증해주시면 확인 후 반영해드릴게요!
✅ 제출 링크 : link2

혹시 추가로 궁금한 점이나 개선되었으면 하는 부분, 교환학생 준비하시면서 불편한 점이 있으시다면 편하게 말씀해주세요!

참고용으로만 봐주시면 감사하겠습니다!

감사합니다.
"""

    msg = MIMEText(body)
    msg["From"]     = smtp_user
    msg["To"]       = to_address
    msg["Subject"]  = subject

    with smtplib.SMTP(smtp_host, smtp_port) as smtp :
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)


@app.post("/webhook")
def webhook (data : WebhookData, db : Session = Depends(get_database)) :

    user = db.query(User).filter_by(email=data.email).first()
    uuid = str(uuid4())
    if not user :
        user = User(
            email    = data.email,
            uuid     = uuid,
            nickname = data.nickname,
            gpa      = data.grade,
            lang     = data.lang,
            status   = 1
        )
        db.add(user)
        
    else :
        user.nickname = data.nickname
        user.gpa      = data.grade
        user.lang     = data.lang
    db.commit()
    db.refresh(user)

    try :
        send_email(data.email, data.nickname, uuid)
    except Exception as e :
        raise HTTPException(500, f"메일 발송 실패: {e}")

    std_choices = standardize_universities(data.choices)
    
    for idx, name in enumerate (std_choices, start = 1) :
        partner_university = db.query(PartnerUniversity).filter_by(name = name).first()
        if not partner_university : continue
        
        app_rec = Application(
            user_id               = user.id,
            partner_university_id = partner_university.id,
            choice                = idx
        )
        db.add(app_rec)
        
    db.commit()

    return {"status": "success", "user_id": user.id}
