from pydantic import BaseModel, EmailStr, Field
from typing import List

class WebhookData (BaseModel) :
    email : EmailStr     = Field(description = "사용자 이메일")
    grade : float        = Field(description = "평균 학점 (GPA)")
    lang : str           = Field(description = "어학 성적")
    choices : List[str]  = Field(description = "1~5지망 대학명 리스트")
    college_name : str   = Field(description = "고정 값: knu")

class EmailRequest (BaseModel) :
    to_address : EmailStr = Field(description = "수신자 이메일 주소")
    nickname : str        = Field(description = "사용자 닉네임")
    uuid : str            = Field(description = "사용자 UUID")
    college_name : str    = Field(description = "학교 이름")

class NicknameRequest (BaseModel) :
    user_id : int         = Field(description = "사용자 ID")

class LandingEmailRequest (BaseModel) :
    email : EmailStr      = Field(description = "랜딩 페이지에서 입력받은 이메일 주소")
