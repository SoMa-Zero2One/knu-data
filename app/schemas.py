from pydantic import BaseModel, EmailStr, Field
from typing import List

class WebhookData (BaseModel) :
    email : EmailStr     = Field(description = "사용자 이메일")
    grade : float        = Field(description = "평균 학점 (GPA)")
    lang : str           = Field(description = "어학 성적")
    choices : List[str]  = Field(description = "1~5지망 대학명 리스트")
    college_name : str   = Field(description = "고정 값: knu")
