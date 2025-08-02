import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename = "/home/ec2-user/email-pipeline/logs/email.log",
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filemode = "a"
)

logger = logging.getLogger("email")


def send_email (to_address : str, nickname : str, uuid : str, college_name : str) :
    
    logger.debug(f"[Send Email] : {to_address}")
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
        
    logger.debug(f"[Sent Email] : {to_address}")
    