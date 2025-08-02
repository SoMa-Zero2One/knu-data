from pydantic import BaseModel, EmailStr, Field
from typing import List

class WebhookData (BaseModel) :
    timestamp : str      = Field(description = "제출 시각, 포맷: 'yyyy-MM-dd HH:mm:ss'")
    email : EmailStr     = Field(description = "사용자 이메일")
    nickname : str       = Field(description = "닉네임")
    grade : float        = Field(description = "평균 학점 (GPA)")
    lang : str           = Field(description = "어학 성적")
    duration : str       = Field(description = "모집 단위 (1개학기/2개학기)")
    choices : List[str]  = Field(description = "1~5지망 대학명 리스트")
    college_name : str   = Field(description = "고정 값: knu")
