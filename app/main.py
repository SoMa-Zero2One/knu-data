from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import datetime

from app.database import SessionLocal
from app.models import User, PartnerUniversity, Application
from app.schemas import WebhookData, EmailRequest, NicknameRequest, LandingEmailRequest
from app.gpt_utils import standardize_universities
from app.utils import send_email, generate_nickname
from app.logging_config import setup_logging

setup_logging()

app = FastAPI()
logger = logging.getLogger("webhook")


def get_database() :
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


@app.post("/webhook")
def webhook (data : WebhookData, database : Session = Depends(get_database)) :

    try :
        
        ### User DB
        logger.debug(f"[Step 1] User DB : {data.email}")
        user = database.query(User).filter_by(email = data.email).first()
        
        if not user :
            uuid = str(uuid4())
            user = User(
                email    = data.email,
                uuid     = uuid,
                grade    = data.grade,
                lang     = data.lang
            )
            database.add(user)
            database.flush()
            user.nickname = generate_nickname(user.id)
           
        else :
            user.grade    = data.grade
            user.lang     = data.lang
            
        database.commit()
        database.refresh(user)
        
        logger.debug(f"[Step 2] User DB : {user.uuid}")

        ### Send Email
        logger.debug(f"[Step 3] Send Email : {data.email}")
        send_email(data.email, user.nickname, user.uuid, data.college_name)
        logger.debug(f"[Step 4] Send Email : {data.email}")
        
        ### Standardize University
        logger.debug(f"[Step 5] Standardize University : {data.choices}")
        std_choices = standardize_universities(data.choices, data.college_name)
        logger.debug(f"[Step 6] Standardize University : {std_choices}")
        
        ### Partner University DB
        logger.debug(f"[Step 7] Partner University DB : {user.id}")
        for idx, name in enumerate (std_choices, start = 1) :
            name = name.strip()
            if not name : break
            
            partner_university = database.query(PartnerUniversity).filter_by(name = name).first()
            logger.debug(f"[Step 8-{idx}] Partner University DB : {name}")
            if not partner_university : 
                logger.debug(f"[Step 8-{idx}] not found")
                continue
            
            app_rec = Application(
                user_id               = user.id,
                partner_university_id = partner_university.id,
                choice                = idx
            )
            database.add(app_rec)
            
        database.commit()
        logger.debug(f"[Step 9] All Done")
        
        return {"status" : "success", "user_id" : user.id}
        
    except Exception as e :
        logger.error(f"Error : {e}")
        raise HTTPException(500, f"Error : {e}")


@app.post("/generate-nickname")
def generate_nickname_endpoint(data : NicknameRequest) :

    try :
        logger.debug(f"[Generate Nickname Endpoint] : user_id {data.user_id}")
        nickname = generate_nickname(data.user_id)
        logger.debug(f"[Nickname Generated] : {nickname}")
        return {"status" : "success", "nickname" : nickname}
    
    except Exception as e :
        logger.error(f"Nickname generation error: {e}")
        raise HTTPException(status_code=500, detail=f"닉네임 생성 중 오류가 발생했습니다 : {e}")


@app.post("/send-email")
def send_email_endpoint(data : EmailRequest) :
    
    try :
        logger.debug(f"[Send Email] Endpoint : {data.to_address}")
        send_email(data.to_address, data.nickname, data.uuid, data.college_name)
        logger.debug(f"[Sent Email] Successfully : {data.to_address}")
        return {"status" : "success"}
    
    except Exception as e :
        logger.error(f"Email sending error: {e}")
        raise HTTPException(status_code=500, detail=f"이메일 전송 중 오류가 발생했습니다: {e}")


@app.post("/landing-email")
def landing_email_endpoint (data : LandingEmailRequest) :

    try :
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        landing_file_path = "data/landing.txt"
        
        with open(landing_file_path, "a", encoding = "utf-8") as f :
            f.write(f"{data.email} {current_time}\n")
        
        logger.debug(f"[Landing Email] Saved : {data.email} at {current_time}")
        
        return {"status" : "success", "message" : "이메일이 성공적으로 저장되었습니다."}
    
    except Exception as e :
        logger.error(f"Landing email save error : {e}, {data.email}")
        raise HTTPException(status_code=500, detail=f"이메일 저장 중 오류가 발생했습니다: {e}")
