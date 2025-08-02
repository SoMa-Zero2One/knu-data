import os, json
import openai
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    filename = "/home/ec2-user/email-pipeline/logs/gpt.log",
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filemode = "a"
)

logger = logging.getLogger("gpt")


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def standardize_universities (choice_list : list[str], school_name : str) -> list[str] :

    logger.debug(f"[Standardize Universities] : {choice_list}")
    
    SCHOOL_LIST_PATH = DATA_DIR / f"{school_name}_list.json"
    
    with open(SCHOOL_LIST_PATH, encoding="utf-8") as f :
        BASE_SCHOOL_LIST = json.load(f)
    
    base_json = json.dumps(BASE_SCHOOL_LIST, ensure_ascii=False)
    choices_json = json.dumps(choice_list, ensure_ascii=False)

    prompt = (
        base_json
        + "\n 내가 영어 이름이나 한글 이름을 입력하면 위의 대학 이름 중에서 가장 유사하거나 동일한 학교를 찾아서 출력해줘\n"
        + "output은 이름을 하나씩 줄바꿈으로 알려줘 \n input : "
        + choices_json
    )

    response = openai.chat.completions.create(
        model = "gpt-4.1-mini",
        messages = [
            {"role" : "system", "content" : "You standardize university names."},
            {"role" : "user",   "content" : prompt}
        ],
        temperature = 0
    )
    
    content = response.choices[0].message.content
    
    return_list = content.split("\n")
    logger.debug(f"[Standardize Universities] : {return_list}")
    
    
    try :
        return return_list
    
    except Exception as e :
        logger.error(f"[Standardize Universities] : {e}")
        return choice_list
