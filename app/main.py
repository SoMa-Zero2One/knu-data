from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database import SessionLocal, User, PartnerUniversity, Application
from app.schemas import WebhookData
from app.gpt_utils import standardize_universities
from app.utils import send_email

logging.basicConfig(
    filename = "/home/ec2-user/email-pipeline/logs/webhook.log",
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filemode = "a"
)

logger = logging.getLogger("webhook")

app = FastAPI()


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
        user = database.query(User).filter_by(email=data.email).first()
        uuid = str(uuid4())
        if not user :
            user = User(
                email    = data.email,
                uuid     = uuid,
                nickname = data.nickname,
                gpa      = data.grade,
                lang     = data.lang
            )
            database.add(user)
            
        else :
            user.nickname = data.nickname
            user.gpa      = data.grade
            user.lang     = data.lang
        database.commit()
        database.refresh(user)
        
        logger.debug(f"[Step 2] User DB : {uuid}")

        ### Send Email
        logger.debug(f"[Step 3] Send Email : {data.email}")
        send_email(data.email, data.nickname, uuid, data.college_name)
        logger.debug(f"[Step 4] Send Email : {data.email}")
        
        ### Standardize University
        logger.debug(f"[Step 5] Standardize University : {data.choices}")
        std_choices = standardize_universities(data.choices, data.college_name)
        logger.debug(f"[Step 6] Standardize University : {std_choices}")
        
        ### Partner University DB
        logger.debug(f"[Step 7] Partner University DB : {user.id}")
        for idx, name in enumerate (std_choices, start = 1) :
            partner_university = database.query(PartnerUniversity).filter_by(name = name).first()
            if not partner_university : continue
            
            logger.debug(f"[Step 8-{idx}] Partner University DB : {name}")
            
            app_rec = Application(
                user_id               = user.id,
                partner_university_id = partner_university.id,
                choice                = idx
            )
            database.add(app_rec)
        database.commit()
        
        logger.debug(f"[Step 9] All Done")
        
        return {"status": "success", "user_id": user.id}
        
    except Exception as e :
        logger.error(f"Error: {e}")
        raise HTTPException(500, f"Error: {e}")
